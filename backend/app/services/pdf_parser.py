
import pdfplumber
import pandas as pd
import re
from .isin_lookup import get_scheme_name as lookup_isin_name

def parse_cam_pdf(file_path: str, password: str = None):
    print(f"Opening PDF: {file_path}")
    items = []
    
    try:
        with pdfplumber.open(file_path, password=password) as pdf:
            current_fund = "Unknown Scheme"
            current_isin = None
            current_folio = None  # Track Folio Number
            pending_fund_name = None  # Track multi-line fund names
            
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    line_strip = line.strip()
                    line_lower = line_strip.lower()
                    
                    # 0. Detect Folio Number (e.g., "Folio No: 21961126 / 89")
                    folio_match = re.search(r'Folio\s*(?:No)?:?\s*(\d+\s*/\s*\d+|\d+)', line_strip, re.IGNORECASE)
                    if folio_match:
                        current_folio = folio_match.group(1).replace(" ", "")
                        pending_fund_name = None  # Reset pending on new folio
                        continue
                    
                    # 1. Detect Fund Header (ISIN/Name)
                    isin_match = re.search(r'(INF\w{9})', line_strip)
                    if isin_match:
                        current_isin = isin_match.group(1)
                        # Extract Name: Try to combine pending (previous line) + current line
                        clean_name = line_strip
                        
                        # If line starts with (Demat) or similar, use pending fund name
                        if pending_fund_name and line_strip.startswith("("):
                            clean_name = pending_fund_name + " " + line_strip
                        
                        if "Advisor" in clean_name:
                            clean_name = clean_name.split("Advisor")[0]
                        # Remove ISIN from name
                        clean_name = re.sub(r'ISIN:?\s*INF\w{9}', '', clean_name)
                        # Remove trailing brackets (Demat/Advisor info)
                        clean_name = re.sub(r'\([^)]*\)\s*$', '', clean_name)
                        clean_name = re.sub(r'\([^)]*\)\s*$', '', clean_name)  # Double pass for nested
                        
                        current_fund = clean_name.strip().rstrip('-').strip()
                        
                        # Always try to get official name from AMFI data
                        amfi_name = lookup_isin_name(current_isin)
                        if amfi_name:
                            current_fund = amfi_name
                        
                        pending_fund_name = None
                        continue # Header processed
                    
                    # Check if this line looks like a fund name (for next ISIN line)
                    # Patterns: "XXXX-Fund Name" OR lines containing fund keywords
                    if 'INF' not in line_strip and not line_strip.startswith("("):
                        is_fund_name = False
                        # Pattern 1: Starts with "XXXX-"
                        if re.match(r'^[A-Z0-9]{3,8}-', line_strip):
                            is_fund_name = True
                        # Pattern 2: Contains fund-related keywords
                        fund_keywords = ['equity', 'debt', 'hybrid', 'balanced', 'bluechip', 
                                         'flexi', 'growth', 'liquid', 'overnight', 'gilt',
                                         'arbitrage', 'elss', 'index']
                        if any(kw in line_lower for kw in fund_keywords):
                            is_fund_name = True
                        
                        if is_fund_name:
                            pending_fund_name = line_strip
                            continue
                    
                    # 2. Skip Noise
                    if "statement" in line_lower or "page" in line_lower:
                        continue
                    if line_lower.startswith("total"):
                        # Capture Global Summary if it looks like the main table total
                        # "Total 2,636,705.02 2,834,204.06"
                        numbers = re.findall(r'([\d,]+\.\d+)', line_strip)
                        if len(numbers) >= 2:
                             clean_nums = [float(n.replace(',', '')) for n in numbers]
                             items.append({
                                "type": "portfolio_summary",
                                "description": "Portfolio Total",
                                "amount": clean_nums[0], # Cost
                                "current_value": clean_nums[1] if len(clean_nums) > 1 else 0 # Value
                             })
                        continue
                    if "mutual fund" in line_lower and "fund" in line_lower:
                        continue

                    # 3. Detect Transactions (Date Start)
                    # Regex: Start with Date (DD-Mon-YYYY or DD/MM/YYYY)
                    date_match = re.search(r'^\s*(\d{2}[-./](?:[A-Za-z]{3}|\d{2})[-./]\d{4})', line_strip)
                    if date_match and "stamp duty" not in line_lower and "charges" not in line_lower:
                        # It's a transaction!
                        date_str = date_match.group(1)
                        
                        numbers = re.findall(r'(-?[\d,]+\.\d{2,4})', line_strip)
                        if numbers:
                            clean_nums = [float(n.replace(',', '')) for n in numbers]
                            amount = clean_nums[0] # Fallback
                            amount = clean_nums[0]
                            
                            # Flow Direction
                            if any(x in line_lower for x in ["redemption", "sell", "switch out", "dividend payout"]):
                                amount = abs(amount) # Inflow (+)
                            elif any(x in line_lower for x in ["purchase", "sip", "switch in", "reinvestment", "systematic", "investment"]):
                                amount = -abs(amount) # Outflow (-)
                            
                            items.append({
                                "date": date_str,
                                "description": current_fund, # Link to Fund!
                                "isin": current_isin,
                                "folio": current_folio,  # Add Folio
                                "amount": amount,
                                "type": "transaction",
                                "raw_desc": line_strip # Keep original details
                            })
                        continue

                    # 4. Detect Holdings (Closing Balance OR Row Summary)
                    # Strategy A: Closing Unit Balance
                    if "closing unit balance" in line_lower:
                        # Try to extract "Total Cost Value" and "Market Value" from the line
                        # Format: "Total Cost Value: 41,605.00" or "Market Value on DATE: INR 43,499.20"
                        cost_match = re.search(r'Total\s*Cost\s*Value:?\s*([\d,]+\.?\d*)', line_strip, re.IGNORECASE)
                        value_match = re.search(r'Market\s*Value[^:]*:\s*(?:INR\s*)?([\d,]+\.?\d*)', line_strip, re.IGNORECASE)
                        
                        cost = 0.0
                        val = 0.0
                        
                        if cost_match:
                            cost = float(cost_match.group(1).replace(',', ''))
                        if value_match:
                            val = float(value_match.group(1).replace(',', ''))
                        
                        # Fallback: use last number as value if patterns didn't match
                        if val == 0:
                            numbers = re.findall(r'([\d,]+\.\d+)', line_strip)
                            if numbers:
                                val = float(numbers[-1].replace(',', ''))
                        
                        if val > 0:
                            items.append({
                                "date": "Current",
                                "description": current_fund,
                                "isin": current_isin,
                                "folio": current_folio,
                                "amount": cost,  # Now using extracted Total Cost Value!
                                "current_value": val,
                                "type": "holding"
                            })
                        continue

                    # Strategy B: Row-based Holding (for non-Transaction PDFs)
                    if not date_match:
                         numbers = re.findall(r'([\d,]+\.\d+)', line_strip)
                         if len(numbers) >= 2 and len(line_strip) > 15:
                             # Check blacklist again
                             if any(x in line_lower for x in ["purchase", "sip", "redemption", "switch", "dividend", "stt", "stamp", "advisor", "registra", "sys. investment", "charges"]):
                                 continue
                             
                             # Extract potential ISIN from THIS line (if not captured in header loop)
                             # This handles "one-liner" holdings in Summary PDF
                             row_isin_match = re.search(r'(INF\w{9})', line_strip)
                             row_fund_name = current_fund
                             
                             if row_isin_match:
                                 # Override current context for this line
                                 current_isin = row_isin_match.group(1)
                                 row_fund_name = line_strip.replace(current_isin, "")
                                 row_fund_name = re.sub(r'[\d,]+\.\d+.*$', '', row_fund_name).strip()
                            
                             # Values
                             clean_nums = [float(n.replace(',', '')) for n in numbers]
                             sorted_nums = sorted(clean_nums, reverse=True)
                             current_value = sorted_nums[0]
                             cost = sorted_nums[1] if len(sorted_nums) > 1 else 0.0
                             
                             items.append({
                                "date": "Current",
                                "description": row_fund_name,
                                "isin": current_isin,
                                "folio": current_folio,  # Add Folio
                                "amount": cost,
                                "current_value": current_value,
                                "type": "holding"
                             })

    except Exception as e:
        import traceback
        print(f"Error parsing PDF: {repr(e)}")
        print(traceback.format_exc())
        raise ValueError(f"Failed to parse PDF: {str(e)}")
        
    return items
