import pandas as pd
from backend.models import analyze_portfolio
import json

def test_nesting():
    # Mock data with ISIN that has details
    # INF109K016L0 is ICICI Prudential Large Cap Fund
    data = [
        {'date': '2023-01-01', 'amount': -10000, 'isin': 'INF109K016L0', 'type': 'transaction', 'description': 'ICICI Pru Large Cap'},
        {'date': '2024-01-01', 'current_value': 15000, 'isin': 'INF109K016L0', 'type': 'valuation', 'description': 'ICICI Pru Large Cap'}
    ]
    df = pd.DataFrame(data)
    
    res = analyze_portfolio(df)
    
    print("Holdings structure:")
    for h in res.get('holdings', []):
        print(f"Fund: {h['description']}")
        print(f"Has 'analytics' key: {'analytics' in h}")
        if 'analytics' in h:
            print(f"Analytics Keys: {list(h['analytics'].keys())}")
            assert 'alpha' in h['analytics']
            assert 'cagr' in h['analytics']

if __name__ == "__main__":
    test_nesting()
