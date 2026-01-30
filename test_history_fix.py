import sys
import os
sys.path.append(os.getcwd())

from backend.analytics import calculate_analytics, calculate_growth_comparison
import json

def test_long_history():
    # Parag Parikh Flexi Cap Fund - Direct Plan - Growth
    # Code: 122639, ISIN: INF740K01031
    scheme_code = "122639"
    print(f"Testing analytics for scheme: {scheme_code}")
    
    res = calculate_analytics(scheme_code)
    if res:
        print(f"Calculated Fund Life: {res['fund_life']:.2f} years")
        assert res['fund_life'] > 5.0, f"Fund life {res['fund_life']} should be > 5 years for this fund (Inception 2013)"
        
    # Test explicit lookup
    from backend.isin_lookup import get_scheme_details
    from backend.analytics import fetch_fund_nav
    
    isin = 'INF740K01031'
    details = get_scheme_details(isin)
    print(f"Lookup for {isin}: {details}")
    
    if details:
        nav = fetch_fund_nav(details['code'])
        if nav is not None:
             print(f"NAV Data for {details['code']}: {len(nav)} rows")
        else:
             print(f"NAV Data for {details['code']} is None")
    
    # Test growth comparison structure
    txs = [
        {'date': '2015-01-01', 'amount': -10000, 'isin': 'INF740K01031', 'type': 'transaction'},
        {'date': '2024-01-01', 'current_value': 50000, 'isin': 'INF740K01031', 'type': 'valuation'}
    ]
    growth = calculate_growth_comparison(txs)
    print(f"Growth Data Keys: {growth.keys()}")
    print(f"Chart Points: {len(growth['chart'])}")
    
    if len(growth['chart']) > 0:
        print("First 5 points:", growth['chart'][:5])
        print("Last 5 points:", growth['chart'][-5:])
        
        # Verify non-zero values
        last_point = growth['chart'][-1]
        print(f"Last Point Values - Invested: {last_point.get('invested')}, Portfolio: {last_point.get('portfolio')}, Benchmark: {last_point.get('benchmark')}")

if __name__ == "__main__":
    test_long_history()
