import re
import json

def _extract_holdings(text):
    print("--- Starting Extraction Logic ---")
    holdings = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        
        # Skip empty lines (from dump format e.g. "53: 51: ...")
        # I need to clean the dump prefix "Number: Number: " if I use dump.txt directly
        # But for this test, let's assume I pass the CLEAN text from the PDF dump 
        # (I will manually populate the list with the problematic lines to test)
        pass 
        
    return holdings

def test_logic():
    # Raw lines from Page 1 (Dump lines 53 and 56 approx)
    # Be careful to string-escape correctly
    raw_lines = [
        "31528522/07 INF109K016L0 P8042 - ICICI Prudential Large Cap Fund 257,000.000 2,214.692 29-Jan-2026 123.52 273,558.76 CAMS",
        "(erstwhile Bluechip Fund) - Direct Plan -",
        "Growth (formerly ICICI Prudential Focused",
        "Bluechip Equity Fund) (Non-Demat)",
        "31528522/07 INF109K010A6 P8104 - ICICI Prudential Banking and PSU 41,605.000 1,234.801 29-Jan-2026 35.2277 43,499.20 CAMS",
        "Debt Fund - Direct Plan - Growth (Non",
        "-Demat)",
        "39855900/29 INF109K010A6 P8104 - ICICI Prudential Banking and PSU 100,000.000 2,905.961 29-Jan-2026 35.2277 102,370.32 CAMS",
        "Debt Fund - Direct Plan - Growth (Demat)",
        "Total 2,636,705.02 2,834,204.07"
    ]
    
    print(f"Testing {len(raw_lines)} lines...")
    
    holdings = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        line_num = i
        i += 1
        
        print(f"Line {line_num}: {line[:50]}...")
        
        numbers = re.findall(r'([\d,]+\.\d+)', line)
        print(f"  Numbers Found: {numbers}")
        
        # Case 1
        if len(numbers) >= 2 and len(line) > 30 and "Statement" not in line:
            if line.strip().lower().startswith("total"):
                print("  -> Ignored Total line")
                continue
                
            print("  -> Case 1 Match")
            isin_match = re.search(r'(INF\w{9})', line)
            isin = isin_match.group(1) if isin_match else None
            
            clean_nums = [float(n.replace(',', '')) for n in numbers]
            sorted_nums = sorted(clean_nums, reverse=True)
            current_value = sorted_nums[0]
            cost = sorted_nums[1] if len(sorted_nums) > 1 else 0.0
            
            scheme_name = line
            if isin: scheme_name = scheme_name.replace(isin, "")
            scheme_name = re.sub(r'[\d,]+\.\d+.*$', '', scheme_name).strip()
            
            print(f"  -> Extracted: {scheme_name} | Cost: {cost} | Val: {current_value}")
            holdings.append({"description": scheme_name, "amount": cost, "current_value": current_value})
            continue
            
        # Case 2
        isin_match = re.search(r'(INF\w{9})', line)
        folio_match = re.search(r'^\s*\d+/\d+', line)
        
        if isin_match or folio_match:
            print("  -> Case 2 Header Match")
            # Look ahead logic...
            # ...
            pass

    print("\nTotal Holdings Found:", len(holdings))
    print(json.dumps(holdings, indent=2))

if __name__ == "__main__":
    test_logic()
