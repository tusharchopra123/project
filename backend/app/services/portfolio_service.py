
import pandas as pd
from pyxirr import xirr
from datetime import date, timedelta
import numpy as np
from .isin_lookup import get_scheme_details, clean_scheme_name

def calculate_portfolio_xirr(transactions: list, current_value: float = 0.0):
    """Calculates XIRR given a list of transactions."""
    dates = []
    amounts = []
    
    for t in transactions:
        try:
            d = pd.to_datetime(t['date']).date()
            dates.append(d)
            amounts.append(float(t['amount']))
        except Exception as e:
            continue
            
    if not dates:
        return 0.0
        
    if current_value > 0:
        dates.append(date.today())
        amounts.append(current_value)
        
    try:
        result = xirr(dates, amounts)
        if result is None or (isinstance(result, float) and (result != result)):  # NaN check
            return 0.0
        return result
    except Exception as e:
        print(f"XIRR calculation error: {e}")
        return 0.0

def is_sip_active(transactions: list) -> bool:
    """Determine if a scheme has an active SIP (Systematic Investment Plan)."""
    if not transactions:
        return False
        
    purchases = [t for t in transactions if float(t['amount']) < 0]
    
    if len(purchases) < 3:
        return False
        
    try:
        dates = sorted([pd.to_datetime(t['date']).date() for t in purchases])
    except:
        return False
        
    last_date = dates[-1]
    days_since_last = (date.today() - last_date).days
    
    if days_since_last > 45:
        return False
        
    recent_dates = dates[-6:]
    if len(recent_dates) < 3:
        return False
        
    intervals = []
    for i in range(1, len(recent_dates)):
        delta = (recent_dates[i] - recent_dates[i-1]).days
        intervals.append(delta)
        
    avg_interval = np.mean(intervals)
    std_dev_interval = np.std(intervals)
    
    if avg_interval > 0:
        cov = std_dev_interval / avg_interval
        if cov < 0.25:
            return True
            
    return False

async def analyze_portfolio(df: pd.DataFrame):
    """
    Performs basic analysis on the portfolio dataframe.
    """
    if df.empty:
        return {}
    
    if 'current_value' in df.columns:
        if 'isin' not in df.columns:
             df['isin'] = None
        
        df['group_key'] = df['isin'].fillna(df['description'])
        
        all_groups = df.groupby('group_key')
        
        held_schemes = []
        total_invested_calc = 0.0
        
        for key, group in all_groups:
            if group['type'].iloc[0] == 'portfolio_summary':
                continue
                
            scheme_txs = group[group['type'] == 'transaction'].to_dict('records')
            scheme_holdings = group[group['type'] == 'holding']
            
            scheme_current_val = scheme_holdings['current_value'].sum()
            
            holdings_cost = scheme_holdings['amount'].sum()
            
            tx_net_invested = 0.0
            if scheme_txs:
                tx_net_invested = -sum(t['amount'] for t in scheme_txs)
            
            net_invested = holdings_cost if holdings_cost > 0 else tx_net_invested
                
            total_invested_calc += max(net_invested, 0)
            
            scheme_xirr = 0.0
            if scheme_txs and scheme_current_val > 0:
                 scheme_xirr = calculate_portfolio_xirr(scheme_txs, scheme_current_val)
            if scheme_xirr != scheme_xirr:  # NaN check
                scheme_xirr = 0.0
            
            best_desc = group['description'].iloc[0]
            best_isin = group['isin'].iloc[0] if 'isin' in group.columns else None
            
            if best_desc == "Unknown Scheme":
                continue
            
            days_invested = 0
            if scheme_txs:
                try:
                    dates = [pd.to_datetime(t['date']).date() for t in scheme_txs]
                    if dates:
                        first_tx_date = min(dates)
                        days_invested = (date.today() - first_tx_date).days
                except Exception as e:
                    print(f"Date calculation error: {e}")

            if scheme_current_val > 0 or net_invested > 0:
                scheme_name = clean_scheme_name(best_desc)  # Clean the fallback name
                try:
                    if best_isin:
                        details = await get_scheme_details(best_isin)
                        if details and details.get('name'):
                            scheme_name = details['name'] # Already cleaned by get_scheme_details
                except:
                    pass
                
                scheme_data = {
                    "description": best_desc,
                    "scheme_name": scheme_name,
                    "isin": best_isin,
                    "amount": net_invested,
                    "current_value": scheme_current_val,
                    "xirr": scheme_xirr,
                    "days_invested": days_invested,
                    "is_sip": is_sip_active(scheme_txs)
                }
                
                try:
                    from .analytics_service import calculate_analytics
                    
                    if best_isin:
                        details = get_scheme_details(best_isin)
                        if details and details.get('code'):
                            analytics = calculate_analytics(details['code'])
                            if analytics:
                                scheme_data['analytics'] = analytics
                except Exception as e:
                    print(f"Analytics error for {best_isin}: {e}")
                
                held_schemes.append(scheme_data)
        
        try:
            from .analytics_service import calculate_portfolio_scores
            scores = calculate_portfolio_scores(held_schemes)
            for s in held_schemes:
                isin = s.get('isin')
                if isin in scores:
                    s['score'] = scores[isin]
        except Exception as e:
            print(f"Scoring integration error: {e}")
        
        allocation = {}
        try:
            from .analytics_service import fetch_fund_nav, classify_fund_category
            for s in held_schemes:
                isin = s.get('isin')
                if isin:
                    details = await get_scheme_details(isin)
                    if details and details.get('code'):
                        fund_result = fetch_fund_nav(details['code'])
                        if fund_result:
                            category_raw = fund_result.get('category', 'Unknown')
                            asset_class = classify_fund_category(category_raw)
                            current_value = s.get('current_value', 0)
                            allocation[asset_class] = allocation.get(asset_class, 0) + current_value
                            s['asset_class'] = asset_class
        except Exception as e:
            print(f"Allocation aggregation error: {e}")
        
        current_val = sum(s['current_value'] for s in held_schemes)
        
        summary_item = next((r for r in df.to_dict('records') if r.get('type') == 'portfolio_summary'), None)
        if summary_item:
            print(f"Using PDF Summary: Inv {summary_item['amount']}, Val {summary_item['current_value']}")
            total_invested_calc = summary_item['amount']
        
        global_xirr = 0.0
        benchmark_xirr = 0.0
        growth_chart = []
        portfolio_stats = {}
        benchmark_stats = {}
        
        if 'type' in df.columns:
            tx_rows = df[df['type'] == 'transaction'].to_dict('records')
            if tx_rows:
                global_xirr = calculate_portfolio_xirr(tx_rows, current_val)
                print(f"Calculated Global XIRR: {global_xirr}")
                
                try:
                    from .analytics_service import calculate_benchmark_xirr, calculate_growth_comparison
                    benchmark_xirr = calculate_benchmark_xirr(tx_rows)
                    print(f"Calculated Benchmark XIRR: {benchmark_xirr}")
                    
                    growth_data = await calculate_growth_comparison(tx_rows)
                    growth_chart = growth_data.get('chart', [])
                    portfolio_stats = growth_data.get('portfolio_stats', {})
                    benchmark_stats = growth_data.get('benchmark_stats', {})
                except Exception as e:
                    print(f"Analytics error: {e}")
                    portfolio_stats = {}
                    benchmark_stats = {}

        return {
            "transaction_count": len(df),
            "xirr": global_xirr,
            "benchmark_xirr": benchmark_xirr,
            "total_investment": total_invested_calc,
            "current_valuation": current_val,
            "status": "Analyzed (Comprehensive)",
            "holdings": held_schemes,
            "growth_chart": growth_chart,
            "portfolio_stats": portfolio_stats,
            "benchmark_stats": benchmark_stats,
            "allocation": allocation
        }
