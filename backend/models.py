import pandas as pd
from pyxirr import xirr
from datetime import date, timedelta
import numpy as np

def calculate_portfolio_xirr(transactions: list, current_value: float = 0.0):
    """
    Calculates XIRR given a list of transactions.
    If current_value > 0, it is added as a positive cash flow on today's date (Terminal Value).
    """
    dates = []
    amounts = []
    
    for t in transactions:
        try:
            # simple parsing, assuming ISO or standard format
            d = pd.to_datetime(t['date']).date()
            dates.append(d)
            amounts.append(float(t['amount']))
        except Exception as e:
            # print(f"Skipping transaction {t}: {e}")
            continue
            
    if not dates:
        return 0.0
        
    # Append Terminal Value (Current Portfolio Value)
    if current_value > 0:
        dates.append(date.today())
        amounts.append(current_value)
        
    try:
        # xirr returns a float
        result = xirr(dates, amounts)
        # Handle NaN - JSON can't serialize it
        if result is None or (isinstance(result, float) and (result != result)):  # NaN check
            return 0.0
        return result
    except Exception as e:
        print(f"XIRR calculation error: {e}")
        return 0.0

def is_sip_active(transactions: list) -> bool:
    """
    Determine if a scheme has an active SIP (Systematic Investment Plan).
    Logic:
    1. At least 3 purchases.
    2. Last purchase within ~45 days.
    3. Regular intervals (low CoV of purchase days).
    """
    if not transactions:
        return False
        
    # Filter for purchases (negative amount)
    purchases = [t for t in transactions if float(t['amount']) < 0]
    
    if len(purchases) < 3:
        return False
        
    # Sort by date
    try:
        # Check if date is string or object
        dates = sorted([pd.to_datetime(t['date']).date() for t in purchases])
    except:
        return False
        
    last_date = dates[-1]
    days_since_last = (date.today() - last_date).days
    
    # 1. Recency check (allow some buffer for weekends/processing)
    if days_since_last > 45:
        return False
        
    # 2. Regularity check
    # taking last 6 transactions to check regularity
    recent_dates = dates[-6:]
    if len(recent_dates) < 3:
        return False
        
    intervals = []
    for i in range(1, len(recent_dates)):
        delta = (recent_dates[i] - recent_dates[i-1]).days
        intervals.append(delta)
        
    # SIPs are usually ~30 days. Weekly SIPs ~7 days.
    avg_interval = np.mean(intervals)
    std_dev_interval = np.std(intervals)
    
    if avg_interval > 0:
        cov = std_dev_interval / avg_interval
        # Allow monthly (28-31) or weekly (7)
        # Filter out random lumpsums (high variance)
        if cov < 0.25:
            return True
            
    return False

def analyze_portfolio(df: pd.DataFrame):
    """
    Performs basic analysis on the portfolio dataframe.
    """
    if df.empty:
        return {}
    
    # Check if we have 'current_value' column (from Holdings extraction)
    if 'current_value' in df.columns:
        # Fill missing ISINs with description to ensure everything has a group key
        if 'isin' not in df.columns:
             df['isin'] = None
        
        # Group by ISIN to collate all entries for the same fund
        # Fallback to description if ISIN is missing
        df['group_key'] = df['isin'].fillna(df['description'])
        
        # Group ALL data by ISIN (collates Demat + Non-Demat, different folios, etc.)
        all_groups = df.groupby('group_key')
        
        held_schemes = []
        total_invested_calc = 0.0
        
        for key, group in all_groups:
            # Skip portfolio_summary items
            if group['type'].iloc[0] == 'portfolio_summary':
                continue
                
            # Separate Transactions and Holdings for this scheme
            scheme_txs = group[group['type'] == 'transaction'].to_dict('records')
            scheme_holdings = group[group['type'] == 'holding']
            
            # Terminal Value for this scheme (sum of all holdings with this ISIN)
            scheme_current_val = scheme_holdings['current_value'].sum()
            
            # Invested Amount: Prefer PDF's "Total Cost Value" from Holdings if available
            # This is authoritative and includes opening balances from before statement period
            holdings_cost = scheme_holdings['amount'].sum()
            
            # Fallback to transaction-based calculation if Holdings didn't have cost
            tx_net_invested = 0.0
            if scheme_txs:
                # Sum all transaction amounts: neg = purchase, pos = redemption
                # Net invested = -sum (because purchases are negative)
                tx_net_invested = -sum(t['amount'] for t in scheme_txs)
            
            # Use Holdings cost if available (>0), otherwise use transaction sum
            net_invested = holdings_cost if holdings_cost > 0 else tx_net_invested
                
            total_invested_calc += max(net_invested, 0)  # Can't have negative total invested
            
            # Calculate Scheme XIRR
            scheme_xirr = 0.0
            if scheme_txs and scheme_current_val > 0:
                 scheme_xirr = calculate_portfolio_xirr(scheme_txs, scheme_current_val)
            # Sanitize NaN
            if scheme_xirr != scheme_xirr:  # NaN check
                scheme_xirr = 0.0
            
            # Get best description (first non-null)
            best_desc = group['description'].iloc[0]
            best_isin = group['isin'].iloc[0] if 'isin' in group.columns else None
            
            # Skip "Unknown Scheme" entries - these are duplicates from incomplete parsing
            if best_desc == "Unknown Scheme":
                continue
            
            # Calculate investment duration (days since first transaction)
            days_invested = 0
            if scheme_txs:
                try:
                    dates = [pd.to_datetime(t['date']).date() for t in scheme_txs]
                    if dates:
                        first_tx_date = min(dates)
                        days_invested = (date.today() - first_tx_date).days
                except Exception as e:
                    print(f"Date calculation error: {e}")

            # Add to list if it has value OR investment
            # Even if current value is 0 (missing NAV), we show the invested amount
            if scheme_current_val > 0 or net_invested > 0:
                # Get proper scheme name for display
                scheme_name = best_desc  # Default to description
                try:
                    from backend.isin_lookup import get_scheme_details
                    if best_isin:
                        details = get_scheme_details(best_isin)
                        if details and details.get('name'):
                            scheme_name = details['name']
                except:
                    pass
                
                scheme_data = {
                    "description": best_desc,
                    "scheme_name": scheme_name,  # Add proper scheme name
                    "isin": best_isin,
                    "amount": net_invested, # NET invested for UI
                    "current_value": scheme_current_val,
                    "xirr": scheme_xirr,
                    "days_invested": days_invested,
                    "is_sip": is_sip_active(scheme_txs)
                }
                
                # Try to add Advanced Analytics if ISIN matches a Scheme Code
                try:
                    # Lazy import to avoid circular dependency or startup issues
                    from backend.isin_lookup import get_scheme_details
                    from backend.analytics import calculate_analytics
                    
                    if best_isin:
                        details = get_scheme_details(best_isin)
                        if details and details.get('code'):
                            analytics = calculate_analytics(details['code'])
                            if analytics:
                                scheme_data['analytics'] = analytics
                except Exception as e:
                    print(f"Analytics error for {best_isin}: {e}")
                
                held_schemes.append(scheme_data)
        
        # Calculate Relative Quality Scores (Quant Model)
        try:
            from backend.analytics import calculate_portfolio_scores
            scores = calculate_portfolio_scores(held_schemes)
            for s in held_schemes:
                isin = s.get('isin')
                if isin in scores:
                    s['score'] = scores[isin]
        except Exception as e:
            print(f"Scoring integration error: {e}")
        
        # Calculate Asset Allocation
        allocation = {}
        try:
            from backend.analytics import fetch_fund_nav, classify_fund_category
            for s in held_schemes:
                isin = s.get('isin')
                if isin:
                    details = get_scheme_details(isin)
                    if details and details.get('code'):
                        fund_result = fetch_fund_nav(details['code'])
                        if fund_result:
                            category_raw = fund_result.get('category', 'Unknown')
                            asset_class = classify_fund_category(category_raw)
                            current_value = s.get('current_value', 0)
                            allocation[asset_class] = allocation.get(asset_class, 0) + current_value
                            # Also store in the individual scheme data
                            s['asset_class'] = asset_class
        except Exception as e:
            print(f"Allocation aggregation error: {e}")
        
        # Global Portfolio XIRR
        # Use ALL transactions and ALL current value
        # calculate global current val from the aggregated schemes
        current_val = sum(s['current_value'] for s in held_schemes)
        
        # Check for Authoritative Portfolio Summary (extracted from 'Total' row)
        summary_item = next((r for r in df.to_dict('records') if r.get('type') == 'portfolio_summary'), None)
        if summary_item:
            # consistency result: prefer the PDF's stated total
            print(f"Using PDF Summary: Inv {summary_item['amount']}, Val {summary_item['current_value']}")
            total_invested_calc = summary_item['amount']
            # We can also update current_valuation if we trust it more, or stick to sum of holdings
            # Usually sum of holdings is fine, but for Total Investment, the PDF summary is key.
        
        global_xirr = 0.0
        benchmark_xirr = 0.0
        growth_chart = []
        
        if 'type' in df.columns:
            tx_rows = df[df['type'] == 'transaction'].to_dict('records')
            if tx_rows:
                global_xirr = calculate_portfolio_xirr(tx_rows, current_val)
                print(f"Calculated Global XIRR: {global_xirr}")
                
                # Calculate Benchmark XIRR (Comparison)
                try:
                    from backend.analytics import calculate_benchmark_xirr, calculate_growth_comparison
                    benchmark_xirr = calculate_benchmark_xirr(tx_rows)
                    print(f"Calculated Benchmark XIRR: {benchmark_xirr}")
                    
                    growth_data = calculate_growth_comparison(tx_rows)
                    growth_chart = growth_data.get('chart', [])
                    portfolio_stats = growth_data.get('portfolio_stats', {})
                    benchmark_stats = growth_data.get('benchmark_stats', {})
                    print(f"Generated Growth Chart: {len(growth_chart)} points")
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

    # Fallback to Transaction Logic
    # Simple metric: Total transactions count
    total_tx = len(df)
    
    return {
        "transaction_count": total_tx,
        "xirr": 0.0, 
        "total_investment": 0,
        "current_valuation": 0,
        "status": "Analyzed (No Value Data)"
    }
