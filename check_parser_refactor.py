from backend.parser import parse_cam_pdf
from backend.models import calculate_portfolio_xirr

def check_final():
    print("Checking Refactored Parser on sample_cam_with_transaction.pdf...")
    data = parse_cam_pdf("sample_cam_with_transaction.pdf", password="123456")
    
    transactions = [x for x in data if x.get('type') == 'transaction']
    holdings = [x for x in data if x.get('type') == 'holding']
    
    current_val = sum(h['current_value'] for h in holdings)
    
    print(f"Transactions: {len(transactions)}")
    print(f"Current Value: {current_val:,.2f}")
    
    xirr = calculate_portfolio_xirr(transactions, current_val)
    print(f"Calculated XIRR: {xirr*100:.2f}%")
    
    # Check if transactions now have proper names
    if transactions:
        print("\n--- Sample Transaction ---")
        print(f"Desc: {transactions[0]['description']}")
        print(f"Amount: {transactions[0]['amount']}")

if __name__ == "__main__":
    check_final()
