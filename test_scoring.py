import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
from backend.analytics import calculate_portfolio_scores

def test_scoring():
    # Mock Data
    schemes = [
        {
            'isin': 'FUND_A_GOOD', 
            'analytics': {
                'performance': {'alpha': 5.0, 'cagr': 0.15, 'max_drawdown': -0.10},
                'risk_ratios': {'sharpe': 1.5, 'sortino': 2.0, 'info_ratio': 1.0, 'beta': 0.8}
            }
        },
        {
            'isin': 'FUND_B_AVG', 
            'analytics': {
                'performance': {'alpha': 1.0, 'cagr': 0.10, 'max_drawdown': -0.20},
                'risk_ratios': {'sharpe': 0.5, 'sortino': 0.8, 'info_ratio': 0.2, 'beta': 1.0}
            }
        },
        {
            'isin': 'FUND_C_BAD', 
            'analytics': {
                'performance': {'alpha': -2.0, 'cagr': 0.05, 'max_drawdown': -0.30},
                'risk_ratios': {'sharpe': 0.1, 'sortino': 0.1, 'info_ratio': -0.5, 'beta': 1.2}
            }
        }
    ]
    
    print("Calculating scores...")
    scores = calculate_portfolio_scores(schemes)
    print(f"Scores: {scores}")
    
    # Assertions
    assert scores['FUND_A_GOOD'] > scores['FUND_B_AVG'], "Good fund should score higher than Avg"
    assert scores['FUND_B_AVG'] > scores['FUND_C_BAD'], "Avg fund should score higher than Bad"
    
    print("Verification Passed!")

if __name__ == "__main__":
    test_scoring()
