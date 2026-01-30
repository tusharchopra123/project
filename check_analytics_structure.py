from backend.analytics import calculate_analytics
from backend.isin_lookup import get_scheme_details

details = get_scheme_details('INF740K01031') # Parag Parikh
code = details['code']
print(f"Testing Analytics for {code}")

data = calculate_analytics(code)
print(f"Keys: {data.keys()}")
print(f"Performance: {data.get('performance')}")
print(f"Risk: {data.get('risk_ratios')}")
