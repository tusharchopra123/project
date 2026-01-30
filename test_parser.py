from backend.parser import parse_cam_pdf
import json

def test():
    print("Testing parser on sample_cam.pdf (Holdings Mode)...")
    transactions = parse_cam_pdf("sample_cam.pdf", password="123456")
    print(f"Found {len(transactions)} items.")
    
    # Check specifically for the ICICI fund
    icici_funds = [t for t in transactions if "INF109K010A6" in str(t.get("isin", "")) or "ICICI Prudential Banking" in t.get("description", "")]
    
    total_invested = sum(t['amount'] for t in icici_funds)
    total_current = sum(t['current_value'] for t in icici_funds)
    
    print(f"\n--- ICICI SUMMARY ---")
    print(f"Count: {len(icici_funds)}")
    print(f"Total Invested: {total_invested}")
    print(f"Total Current: {total_current}")
    # print(json.dumps(icici_funds, indent=2, default=str)) # Disable noise

if __name__ == "__main__":
    test()
