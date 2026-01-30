import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
import numpy as np
from backend.analytics import fetch_benchmark_data, calculate_portfolio_scores, calculate_growth_comparison

def debug_issues():
    print("--- 1. Debugging Benchmark Data ---")
    bench = fetch_benchmark_data()
    if bench is not None:
        print(f"Benchmark DF Shape: {bench.shape}")
        print(f"Benchmark Index Type: {type(bench.index)}")
        print(f"Benchmark Index Example: {bench.index[0]}")
        print(f"Benchmark Head:\n{bench.head()}")
        
        # Check reindexing compatibility
        dates = pd.date_range(start=bench.index[0], periods=5, freq='D', normalize=True)
        print(f"Test Reindex Dates: {dates[0]} (Type: {type(dates[0])})")
        
        try:
            reindexed = bench.reindex(dates)
            print(f"Reindexed Head:\n{reindexed.head()}")
        except Exception as e:
            print(f"Reindexing Error: {e}")
    else:
        print("Benchmark fetch returned None")

    print("\n--- 2. Debugging Quant Score ---")
    # Mock data that should produce a score (Flat Structure)
    mock_schemes = [
        {
            'isin': 'TEST001',
            'analytics': {
                'alpha': 0.05, 'cagr': 0.12, 'max_drawdown': -0.15,
                'sharpe': 1.2, 'sortino': 1.5, 'info_ratio': 0.8, 'beta': 0.9
            }
        },
        {
            'isin': 'TEST002 (Missing)',
            'analytics': {}
        }
    ]
    
    scores = calculate_portfolio_scores(mock_schemes)
    print(f"Calculated Scores: {scores}")
    
    print("\n--- 3. Debugging Growth Chart (Benchmark) ---")
    txs = [
        {'date': '2023-01-01', 'amount': -10000, 'isin': 'INF740K01031', 'type': 'transaction'}, # Parag Parikh (Valid)
        {'date': '2024-01-01', 'current_value': 12000, 'isin': 'INF740K01031', 'type': 'valuation'}
    ]
    # Ensure scheme details are cached/available for this test
    # Ensure scheme details are cached/available for this test
    # Fix imports
    from backend.isin_lookup import get_scheme_details
    from backend.analytics import fetch_fund_nav
    
    details = get_scheme_details('INF740K01031')
    if details:
        print(f"Scheme Found: {details}")
        nav = fetch_fund_nav(details['code'])
        print(f"NAV Found: {nav is not None}")
    
    print("Calling calculate_growth_comparison...")
    chart_res = calculate_growth_comparison(txs)
    chart = chart_res.get('chart', [])
    print(f"Chart Points: {len(chart)}")
    if len(chart) > 0:
        print(f"Last Point: {chart[-1]}")
    else:
        print("Chart is empty.")

if __name__ == "__main__":
    debug_issues()
