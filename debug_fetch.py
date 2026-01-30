from backend.isin_lookup import get_scheme_details
from backend.analytics import fetch_fund_nav, calculate_growth_comparison
import pandas as pd

print("--- Debugging Data Fetch ---")

# 1. Test ISIN Lookup
test_isin = "INF209K01VA7" # Some random ISIN or one from user's portfolio?
# I'll use a common one or one seen in logs if possible. 
# Better: List a few common ones.
isins = ["INF109K010A6", "INF209K01VA7", "INF846K01EW2"]

print(f"Testing Lookup for ISINs: {isins}")
for isin in isins:
    details = get_scheme_details(isin)
    print(f"ISIN: {isin} -> Details: {details}")
    
    if details and details.get('code'):
        # 2. Test NAV Fetch
        print(f"  Fetching NAV for Code: {details['code']}...")
        df = fetch_fund_nav(details['code'])
        if df is None:
            print("  NAV Fetch Failed (None)")
        elif df.empty:
            print("  NAV Fetch Returned Empty DF")
        else:
            print(f"  NAV Fetch Success: {len(df)} rows. Last: {df.index[-1]}")
            
# 3. Test Growth Chart with mock data
print("\n--- Testing Growth Chart Logic ---")
mock_txs = [
    {'date': '2023-01-01', 'amount': -10000.0, 'type': 'transaction', 'isin': isins[0]}
]
print(f"Mock Transactions: {mock_txs}")
try:
    chart = calculate_growth_comparison(mock_txs)
    print(f"Chart Points: {len(chart)}")
    if not chart:
        print("Chart is empty! Debugging why...")
        # Check if ISIN was found
        det = get_scheme_details(isins[0])
        if not det or not det.get('code'):
            print("  Reason: ISIN not resolved.")
        else:
            df = fetch_fund_nav(det['code'])
            if df is None or df.empty:
                print("  Reason: NAV fetch failed.")
            else:
                print("  Reason: Logic filtering?")
                valid_isins = set([isins[0]]) 
                # Wait, inside function it calls get_scheme_details again.
except Exception as e:
    print(f"Growth Chart Exception: {e}")
