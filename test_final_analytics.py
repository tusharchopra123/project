import sys
import os
sys.path.append(os.getcwd())

from backend.analytics import calculate_analytics
import json

def test_analytics():
    # Parag Parikh Flexi Cap Fund - Direct Plan - Growth
    scheme_code = "122639"
    print(f"Testing analytics for scheme: {scheme_code}")
    
    res = calculate_analytics(scheme_code)
    if res:
        print("\nCalculated Metrics:")
        print(json.dumps(res, indent=4))
        
        # Basic sanity checks
        assert 'alpha' in res
        assert 'sharpe' in res
        assert 'sortino' in res
        assert 'cagr' in res
        assert 'upside_capture' in res
        assert 'downside_capture' in res
        print("\nAll expected keys present.")
    else:
        print("Failed to calculate analytics.")

if __name__ == "__main__":
    test_analytics()
