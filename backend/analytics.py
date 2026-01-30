import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta, date
from functools import lru_cache

# Benchmark Ticker (Nifty 50)
BENCHMARK_TICKER = "^NSEI"
RISK_FREE_RATE = 0.06
TRADING_DAYS = 252

@lru_cache(maxsize=100)
def fetch_fund_nav(scheme_code: str):
    """Fetch historical NAV and metadata from mfapi.in"""
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('data'):
            return None
            
        nav_data = data['data']
        df = pd.DataFrame(nav_data)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        df['nav'] = pd.to_numeric(df['nav'])
        df = df.rename(columns={'nav': 'fund_nav'})
        df = df.sort_values('date').set_index('date')
        
        # Extract metadata
        meta = data.get('meta', {})
        category = meta.get('scheme_category', 'Unknown')
        
        return {
            'nav_data': df,
            'category': category
        }
    except Exception as e:
        print(f"Error fetching fund data for {scheme_code}: {e}")
        return None

def classify_fund_category(scheme_category: str) -> str:
    """Classify fund into broad asset class based on scheme category"""
    if not scheme_category:
        return 'Others'
    
    category = scheme_category.upper()
    
    # Equity funds (including Index funds)
    if any(keyword in category for keyword in ['EQUITY', 'ELSS', 'INDEX']):
        return 'Equity'
    # Debt funds
    elif any(keyword in category for keyword in ['DEBT', 'INCOME', 'BOND', 'GILT', 'LIQUID', 'DURATION']):
        return 'Debt'
    # Hybrid/Balanced funds
    elif any(keyword in category for keyword in ['HYBRID', 'BALANCED', 'AGGRESSIVE', 'CONSERVATIVE']):
        return 'Hybrid'
    # Commodities (Gold, Silver, etc.)
    elif any(keyword in category for keyword in ['GOLD', 'SILVER', 'COMMODITY']):
        return 'Commodities'
    # Default to Others
    else:
        return 'Others'

@lru_cache(maxsize=1)
def fetch_benchmark_data():
    """Fetch Nifty 50 data from yfinance"""
    try:
        # Fetch last 5 years
        # end_date = datetime.now()
        # start_date = end_date - timedelta(days=365*5)
        # ticker = yf.Ticker(BENCHMARK_TICKER)
        # df = ticker.history(start=start_date, end=end_date)
        
        # Using download for simpler DF
        # Fetch max history to allow long fund lives
        # Fetch maximum history to avoid capping fund life or growth charts
        df = yf.download(BENCHMARK_TICKER, period="max", progress=False)
        if df.empty:
            return None
        
        # Keep only Close
        df = df[['Close']]
        df.columns = ['benchmark_nav']
        return df
    except Exception as e:
        print(f"Error fetching benchmark: {e}")
        return None

def calculate_analytics(scheme_code: str):
    """Calculate all advanced analytics for a scheme"""
    fund_result = fetch_fund_nav(scheme_code)
    bench_df = fetch_benchmark_data()
    
    if fund_result is None or bench_df is None:
        return None
    
    fund_df = fund_result['nav_data']
        
    # Align data
    # Rename for merge
    fund_df = fund_df.rename(columns={'nav': 'fund_nav'})
    
    # Merge on Date index (inner join)
    merged = fund_df.join(bench_df, how='inner')
    
    if len(merged) < 20: # Match flexi_cap.py leniency
        return None
        
    # Calculate Daily Returns
    merged['fund_ret'] = merged['fund_nav'].pct_change()
    merged['bench_ret'] = merged['benchmark_nav'].pct_change()
    merged = merged.dropna()
    
    # --- Metrics Calculation ---
    fund_life_years = (merged.index[-1] - merged.index[0]).days / 365.25
    
    ret = merged[['fund_nav', 'benchmark_nav']].pct_change().dropna()
    ret.columns = ['Fund', 'Bench']
    days = len(ret)
    
    # 1. CAGR (Annualized)
    cagr_f = (1 + ret['Fund']).prod() ** (TRADING_DAYS / days) - 1
    bench_cagr = (1 + ret['Bench']).prod() ** (TRADING_DAYS / days) - 1
    
    # 2. Risk Metrics (Alpha, Beta)
    vol = ret['Fund'].std() * np.sqrt(TRADING_DAYS)
    sharpe = (cagr_f - RISK_FREE_RATE) / vol if vol != 0 else 0
    
    # Beta
    cov = ret['Fund'].cov(ret['Bench'])
    var = ret['Bench'].var()
    beta = cov / var if var != 0 else 0
    
    # CAPM Alpha (Annualized)
    alpha = cagr_f - (RISK_FREE_RATE + beta * (bench_cagr - RISK_FREE_RATE))
    
    # 3. Sortino Ratio
    rf_daily = (1 + RISK_FREE_RATE) ** (1/TRADING_DAYS) - 1
    neg_excess = np.minimum(ret['Fund'] - rf_daily, 0)
    downside_dev = np.sqrt(np.mean(neg_excess**2)) * np.sqrt(TRADING_DAYS)
    sortino = (cagr_f - RISK_FREE_RATE) / downside_dev if downside_dev != 0 else 0
    
    # 4. Information Ratio
    active_ret = ret['Fund'] - ret['Bench']
    tracking_error = active_ret.std() * np.sqrt(TRADING_DAYS)
    info_ratio = (cagr_f - bench_cagr) / tracking_error if tracking_error != 0 else 0
    
    # 5. Capture Ratios (Annualized)
    up_mkt = ret[ret['Bench'] >= 0]
    up_cap = ((1 + up_mkt['Fund']).prod()**(TRADING_DAYS/max(1, len(up_mkt))) - 1) / \
             ((1 + up_mkt['Bench']).prod()**(TRADING_DAYS/max(1, len(up_mkt))) - 1) * 100 if len(up_mkt)>0 else 0
             
    down_mkt = ret[ret['Bench'] < 0]
    down_cap = ((1 + down_mkt['Fund']).prod()**(TRADING_DAYS/max(1, len(down_mkt))) - 1) / \
               ((1 + down_mkt['Bench']).prod()**(TRADING_DAYS/max(1, len(down_mkt))) - 1) * 100 if len(down_mkt)>0 else 0
    
    # 6. Max Drawdown & Recovery
    cumulative = (1 + ret['Fund']).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    
    mdd_date = drawdown.idxmin()
    peak_val_at_mdd = peak.loc[mdd_date]
    post_mdd_data = cumulative.loc[mdd_date:]
    
    recovery_indices = post_mdd_data[post_mdd_data >= peak_val_at_mdd].index
    real_recovery_dates = recovery_indices[recovery_indices > mdd_date]
    
    recovery_days = "Unrecovered"
    if len(real_recovery_dates) > 0:
        recovery_days = (real_recovery_dates[0] - mdd_date).days

    # 7. Rolling Returns (3 Year)
    merged['rolling_3y'] = merged['fund_nav'].pct_change(periods=TRADING_DAYS * 3)
    rolling_3y = merged['rolling_3y'].dropna()
    rolling_3y_annual = (1 + rolling_3y) ** (1/3) - 1
    
    return {
        "fund_life": fund_life_years,
        "alpha": alpha,
        "beta": beta,
        "sharpe": sharpe,
        "sortino": sortino,
        "info_ratio": info_ratio,
        "upside_capture": up_cap,
        "downside_capture": down_cap,
        "max_drawdown": max_drawdown,
        "recovery_days": recovery_days,
        "cagr": cagr_f,
        "rolling_3y_min": rolling_3y_annual.min() if not rolling_3y_annual.empty else None,
        "rolling_3y_max": rolling_3y_annual.max() if not rolling_3y_annual.empty else None,
        "rolling_3y_avg": rolling_3y_annual.mean() if not rolling_3y_annual.empty else None,
        "rolling_pos": (rolling_3y_annual > 0).mean() if not rolling_3y_annual.empty else None,
    }

def calculate_benchmark_xirr(transactions: list):
    """
    Calculate XIRR if the same transactions were invested in Nifty 50.
    transactions: list of dict { 'date': 'YYYY-MM-DD', 'amount': float }
    returns: float (XIRR)
    """
    bench_df = fetch_benchmark_data()
    if bench_df is None:
        return 0.0
        
    # We need pyxirr here
    from pyxirr import xirr
    
    dates = []
    amounts = []
    total_units = 0.0
    
    # Process transactions
    for t in transactions:
        try:
            t_date = pd.to_datetime(t['date']).date()
            amount = float(t['amount']) # negative for buy, positive for sell
            
            # Find closest benchmark price
            # We use asof to find price on or before the date
            try:
                # bench_df index is datetime
                price = bench_df.loc[bench_df.index <= pd.Timestamp(t_date)].iloc[-1]['benchmark_nav']
            except IndexError:
                # If date is before benchmark start, maybe skip or use first available?
                # Benchmark fetch is last 5 years. If tx is older, we might have issue.
                # Use first available if date is older
                if t_date < bench_df.index[0].date():
                     price = bench_df.iloc[0]['benchmark_nav']
                else:
                    continue

            # Amount is cashflow. 
            # If buying (neg amount), units = abs(amount) / price (units added)
            # If selling (pos amount), units = -amount / price (units removed)
            # Wait, amount is cash flow. 
            # Inv: -1000 -> Buy 1000 worth -> Units += 1000/Price
            # Red: +1000 -> Sell 1000 worth -> Units -= 1000/Price
            
            units_delta = -amount / price
            total_units += units_delta
            
            dates.append(t_date)
            amounts.append(amount)
            
        except Exception as e:
            # print(f"Bench XIRR tx error: {e}")
            pass
            
    if not dates or total_units <= 0:
        return 0.0
        
    # Terminal Value
    current_price = bench_df.iloc[-1]['benchmark_nav']
    terminal_value = total_units * current_price
    
    dates.append(date.today())
    amounts.append(terminal_value)
    
    try:
        res = xirr(dates, amounts)
        if res is None or (isinstance(res, float) and res != res):
            return 0.0
        return res
    except:
        return 0.0

def calculate_growth_comparison(transactions: list, held_schemes: dict = None):
    """
    Generate daily series for Portfolio Value vs Benchmark Value.
    transactions: list of dict details
    held_schemes: map of isin -> scheme_code (optional optimization)
    Returns: list of dict { date, invested, portfolio, benchmark }
    """
    bench_df = fetch_benchmark_data()
    
    empty_res = {
        "chart": [],
        "portfolio_stats": {},
        "benchmark_stats": {}
    }

    if bench_df is None:
        return empty_res
        
    # We need map of Code -> DF
    from backend.isin_lookup import get_scheme_details
    
    # 1. Prepare Fund Data
    # Clean ISINs from transactions
    unique_isins = set()
    for t in transactions:
        if t.get('isin'):
            clean_isin = t['isin'].strip().upper()
            t['isin'] = clean_isin # Update in place for consistency
            unique_isins.add(clean_isin)
            
    print(f"[DEBUG] Growth Chart: Found {len(unique_isins)} unique ISINs in transactions: {unique_isins}")
    
    fund_dfs = {}
    for isin in unique_isins:
        details = get_scheme_details(isin)
        if details:
            code = details['code']
            fund_result = fetch_fund_nav(code)
            if fund_result is not None:
                fund_dfs[isin] = fund_result['nav_data']
            else:
                print(f"[DEBUG] Growth Chart: No NAV data for {isin} (Code: {code})")
        else:
             print(f"[DEBUG] Growth Chart: No scheme details for {isin}")
            
    print(f"[DEBUG] Growth Chart: Fund DFs populated for: {list(fund_dfs.keys())}")
    
    if not fund_dfs:
        print("[DEBUG] Growth Chart: fund_dfs empty. Aborting.")
        return empty_res
        
    # 2. Filter Transactions: Only include those for which we have Fund Data
    valid_isins = set(fund_dfs.keys())
    valid_txs = [t for t in transactions if t.get('isin') in valid_isins]
    # valid_txs = transactions # Reverted "Include All" strategy
    
    print(f"[DEBUG] Growth Chart: Valid Transactions: {len(valid_txs)} out of {len(transactions)}")
    if not valid_txs:
        return empty_res

    # 3. Simulation Loop
    # Create a Date Range from First Valid Transaction to Today
    tx_df = pd.DataFrame(valid_txs)
    tx_df['date'] = pd.to_datetime(tx_df['date'])
    start_date = tx_df['date'].min()
    end_date = pd.Timestamp.now()
    
    # Create daily index
    date_range = pd.date_range(start=start_date, end=end_date, freq='D', normalize=True)
    
    # Pad start date for reindexing to ensure ffill works for the first date if it's a holiday
    pad_start_date = start_date - timedelta(days=7)
    pad_range = pd.date_range(start=pad_start_date, end=end_date, freq='D', normalize=True)
    
    # Trackers
    # Portfolio Units & Cost Basis per ISIN
    portfolio_units = {isin: 0.0 for isin in valid_isins}
    cost_basis = {isin: 0.0 for isin in valid_isins}
    
    # Benchmark Units & Cost Basis
    benchmark_units = 0.0
    benchmark_cost_basis = 0.0
    
    result_series = []
    
    
    # Benchmark Nav Series (resample to daily to handle weekends/holidays fill)
    # Normalize index to avoid timestamp mismatch (e.g. 15:30 vs 00:00)
    bench_df.index = pd.to_datetime(bench_df.index).normalize()
    if bench_df.index.tz is not None:
        bench_df.index = bench_df.index.tz_localize(None)
        
    # Handle potentially duplicate indices after normalization
    bench_df = bench_df[~bench_df.index.duplicated(keep='last')]
    
    bench_daily = bench_df.reindex(pad_range).ffill().bfill()
    
    # Check if bench_daily is all NaNs
    if bench_daily['benchmark_nav'].isna().all():
        print("[WARNING] Benchmark data is all NaN after reindexing. Check date ranges.")
    print(f"[DEBUG] Bench Daily Cols: {bench_daily.columns}")
    
    # Fund NAVs Daily
    fund_daily = {}
    for isin, df in fund_dfs.items():
        fund_daily[isin] = df.reindex(pad_range).ffill().bfill()
        
    # Normalize transaction dates to midnight
    tx_df['date'] = tx_df['date'].dt.normalize()
    
    # Index by date for easier lookup
    tx_df = tx_df.set_index('date').sort_index()
    
    for i, current_date in enumerate(date_range):
        # Process transactions for this day
        if current_date in tx_df.index:
            # Use loc with list to ensure DataFrame is returned even for single match
            # But loc on index with duplicates returns DataFrame automatically
            # If unique, it returns Series. We want DataFrame.
            matches = tx_df.loc[current_date]
            if isinstance(matches, pd.Series):
                day_txs = matches.to_frame().T
            else:
                day_txs = matches
                
            for _, t in day_txs.iterrows():
                try:
                    amt = float(t['amount'])
                except (ValueError, TypeError):
                    continue
                    
                if pd.isna(amt) or abs(amt) < 0.01:
                    continue
                    
                isin = t.get('isin')
                # print(f"[DEBUG] Processing TX on {current_date}: {amt} for {isin}")
                
                # Logic:
                # Amt < 0: Buy. Increases Cost Basis, Increases Units.
                # Amt > 0: Sell. Decreases Cost Basis proportionally, Decreases Units.
                
                # Fetch NAV for unit calculation logic
                # We need NAV to determine 'Units Scenarios'
                
                # Logic:
                # If we have fund data, update units and cost.
                if isin in fund_daily:
                    try:
                        # Get Fund NAV
                        val = fund_daily[isin].loc[current_date]
                        if isinstance(val, pd.DataFrame):
                            f_nav = val['fund_nav'].iloc[0]
                        elif isinstance(val, pd.Series):
                            f_nav = val['fund_nav']
                        else:
                             f_nav = np.nan
                        
                        if pd.notna(f_nav) and f_nav > 0:
                            if amt < 0:
                                # BUY
                                buy_amt = abs(amt)
                                units_added = buy_amt / f_nav
                                portfolio_units[isin] += units_added
                                cost_basis[isin] += buy_amt
                            else:
                                # SELL
                                sell_amt = amt
                                units_sold = sell_amt / f_nav
                                current_units = portfolio_units[isin]
                                if current_units > 0:
                                    ratio_kept = max(0, (current_units - units_sold) / current_units)
                                    cost_basis[isin] *= ratio_kept
                                    portfolio_units[isin] -= units_sold
                                else:
                                    cost_basis[isin] = 0
                                    portfolio_units[isin] = 0
                    except Exception as e:
                        pass
                    
                # BENCHMARK LOGIC
                try:
                    val = bench_daily.loc[current_date]
                    if isinstance(val, pd.DataFrame):
                        b_nav = val['benchmark_nav'].iloc[0]
                    elif isinstance(val, pd.Series):
                        b_nav = val['benchmark_nav']
                    else:
                        b_nav = np.nan
                        
                    if pd.notna(b_nav) and b_nav > 0:
                        if amt < 0:
                            # BUY
                            buy_amt = abs(amt)
                            units_added = buy_amt / b_nav
                            benchmark_units += units_added
                            benchmark_cost_basis += buy_amt
                        else:
                            # SELL
                            sell_amt = amt
                            units_sold = sell_amt / b_nav
                            
                            # Proportional Cost Basis Reduction
                            if benchmark_units > 0:
                                ratio_kept = max(0, (benchmark_units - units_sold) / benchmark_units)
                                benchmark_cost_basis *= ratio_kept
                                benchmark_units -= units_sold
                            else:
                                benchmark_cost_basis = 0
                                benchmark_units = 0
                except:
                    pass
        
        # Calculate Daily Valuation
        curr_port_val = 0.0
        total_active_cost = 0.0
        
        for isin, units in portfolio_units.items():
            if units > 0.001: # Filter dust
                total_active_cost += cost_basis[isin]
                try:
                    val = fund_daily[isin].loc[current_date]
                    if isinstance(val, pd.DataFrame):
                        f_nav = val['fund_nav'].iloc[0]
                    elif isinstance(val, pd.Series):
                        f_nav = val['fund_nav']
                    else:
                        f_nav = 0
                    
                    curr_port_val += units * f_nav
                except:
                    pass
                    
        curr_bench_val = 0.0
        try:
             val = bench_daily.loc[current_date]
             if isinstance(val, pd.DataFrame):
                b_nav = val['benchmark_nav'].iloc[0]
             elif isinstance(val, pd.Series):
                b_nav = val['benchmark_nav']
             else:
                b_nav = 0
             curr_bench_val = benchmark_units * b_nav
        except:
             pass
             pass
            
        # Add point
        # For graph smoothness, maybe only add if we have non-zero invested?
        if total_active_cost > 1 or curr_port_val > 1:
            result_series.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "invested": round(total_active_cost, 2),
                "portfolio": round(curr_port_val, 2),
                "benchmark": round(curr_bench_val, 2)
            })
            
    # 4. Calculate Portfolio Stats (MDD, Recovery)
    portfolio_mdd = 0
    portfolio_recovery = None
    benchmark_mdd = 0
    benchmark_recovery = None
    # 4. Return Chart Data Only (User requested removal of Portfolio Risk Metrics)
    # The frontend expects 'chart', 'portfolio_stats', 'benchmark_stats' keys.
    # We will return empty stats or just the keys to prevent errors.
    

    return {
        "chart": result_series,
        "portfolio_stats": {}, # Removed MaxDD/Recovery as requested
        "benchmark_stats": {}
    }


def calculate_portfolio_scores(schemes_data: list) -> dict:
    """
    Calculate a 0-100 'Quant Score' for each scheme based on its relative performance.
    Uses Min-Max scaling across the portfolio.
    
    Metrics & Weights:
    - Alpha (20%): Higher is better
    - Sharpe (20%): Higher is better
    - Sortino (20%): Higher is better
    - CAGR (10%): Higher is better
    - Information Ratio (10%): Higher is better
    - Beta (10%): Lower is better (Ideal ~1, but simpler is lower volatility relative to market?) 
      Actually for Beta, closer to 0 is lower volatility. 
    - Max Drawdown (10%): Lower magnitude (closer to 0) is better.
    """
    if not schemes_data:
        return {}
        
    # Extract metrics into a DataFrame for easy scaling
    rows = []
    for s in schemes_data:
        isin = s.get('isin')
        analytics = s.get('analytics', {})
        
        # safely get values, default to None (Flat inputs)
        row = {
            'isin': isin,
            'alpha': analytics.get('alpha'),
            'cagr': analytics.get('cagr'),
            'sharpe': analytics.get('sharpe'),
            'sortino': analytics.get('sortino'),
            'info_ratio': analytics.get('info_ratio'),
            'beta': analytics.get('beta'),
            'max_drawdown': analytics.get('max_drawdown') 
        }
        rows.append(row)
        
    df = pd.DataFrame(rows)
    df.set_index('isin', inplace=True)
    
    # Weights configuration
    weights = {
        'alpha': 0.25,
        'sharpe': 0.20,
        'sortino': 0.20,
        'cagr': 0.15,
        'info_ratio': 0.10,
        # 'beta': 0.0, # Beta is tricky, depends on strategy. Omit for general score?
        'max_drawdown': 0.10
    }
    
    scores = {}
    
    try:
        # Normalize each column
        for col, weight in weights.items():
            if col not in df.columns or df[col].isnull().all():
                continue
                
            series = df[col].astype(float).fillna(0) # Fill NaNs with 0 (neutral) or median? 0 is safe penalty
            
            min_val = series.min()
            max_val = series.max()
            rng = max_val - min_val
            
            if rng == 0:
                # All same, give full points or half?
                normalized = pd.Series(0.5, index=series.index)
            else:
                if col == 'max_drawdown':
                    # Max DD is negative (e.g. -0.5 is worse than -0.1). 
                    # Higher value (closer to 0) is better.
                    # Simple MinMax works: -0.1 (max) gets 1.0, -0.5 (min) gets 0.0
                    normalized = (series - min_val) / rng
                elif col == 'beta':
                    # Lower is better? (assuming minimizing risk). 
                    # Invert: 1 - MinMax
                    normalized = 1 - ((series - min_val) / rng)
                else:
                    # Higher is better
                    normalized = (series - min_val) / rng
            
            # Add weighted score
            for isin, val in normalized.items():
                scores[isin] = scores.get(isin, 0) + (val * weight)
        
        # Scale to 0-100
        # Check sum of weights used (in case some cols missing)
        used_weights = sum(weights[c] for c in weights if c in df.columns and not df[c].isnull().all())
        
        final_scores = {}
        for isin, raw_score in scores.items():
            if used_weights > 0:
                final = (raw_score / used_weights) * 100
            else:
                final = 0
            final_scores[isin] = round(final, 1)
            
        return final_scores
        
    except Exception as e:
        print(f"Scoring error: {e}")
        return {}
