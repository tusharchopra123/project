from backend.parser import parse_cam_pdf
from backend.models import calculate_portfolio_xirr
import json
import pandas as pd

def test_transactions():
    print("Testing parser on sample_cam_with_transaction.pdf...")
    data = parse_cam_pdf("sample_cam_with_transaction.pdf", password="123456")
    
    print(f"Extracted {len(data)} items.")
    
    # Filter for transactions
    transactions = [x for x in data if x.get('type') == 'transaction']
    holdings = [x for x in data if x.get('type') == 'holding']
    
    print(f"Transactions found: {len(transactions)}")
    print(f"Holdings found: {len(holdings)}")
    
    if len(transactions) > 0:
        print("\n--- First 3 Transactions ---")
        print(json.dumps(transactions[:3], indent=2, default=str))
        
        # Calculate XIRR
        print("\n--- Calculating XIRR ---")
        current_val = sum(h['current_value'] for h in holdings)
        print(f"Total Current Value from Holdings: {current_val}")
        
        xirr_val = calculate_portfolio_xirr(transactions, current_val)
        print(f"Calculated XIRR: {xirr_val * 100:.2f}%")
    else:
        print("No transactions found to calculate XIRR.")

if __name__ == "__main__":
    test_transactions()
