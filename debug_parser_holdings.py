from backend.parser import parse_cam_pdf
import pandas as pd

def debug_holdings():
    print("Debugging Extracted Holdings on sample_cam_with_transaction.pdf...")
    data = parse_cam_pdf("sample_cam_with_transaction.pdf", password="123456")
    
    holdings = [x for x in data if x.get('type') == 'holding']
    if not holdings:
        print("No holdings extracted.")
        return

    df = pd.DataFrame(holdings)
    print("\n--- Extracted Holdings Data ---")
    # Show Description, Amount (Cost), Current Value
    print(df[['description', 'amount', 'current_value']].sort_values('current_value', ascending=False).to_string())
    
    total_cost = df['amount'].sum()
    print(f"\nTotal Extracted Cost: {total_cost:,.2f}")

if __name__ == "__main__":
    debug_holdings()
