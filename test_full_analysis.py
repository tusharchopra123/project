from backend.parser import parse_cam_pdf
from backend.models import analyze_portfolio
import pandas as pd

def check_analysis():
    print("Checking Full Analysis on sample_cam_with_transaction.pdf...")
    data = parse_cam_pdf("sample_cam_with_transaction.pdf", password="123456")
    df = pd.DataFrame(data)
    
    result = analyze_portfolio(df)
    
    print(f"\nGlobal XIRR: {result['xirr']*100:.2f}%")
    print(f"Total Invested: {result['total_investment']:,.2f}")
    
    print("\n--- Scheme Performance ---")
    holdings = result['holdings']
    # Sort by Current Value
    holdings.sort(key=lambda x: x['current_value'], reverse=True)
    
    for h in holdings[:10]: # Top 10
        xirr_str = f"{h['xirr']*100:.2f}%" if h['xirr'] else "N/A"
        print(f"{h['description'][:40]:<40} Val: {h['current_value']:<12,.2f} Inv: {h['amount']:<12,.2f} XIRR: {xirr_str}")

if __name__ == "__main__":
    check_analysis()
