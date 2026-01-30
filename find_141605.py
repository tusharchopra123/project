import pdfplumber
import re

# Find Opening Balance or any row with cost for ICICI Banking
with pdfplumber.open("sample_cam_with_transaction.pdf", password="123456") as pdf:
    in_icici = False  
    current_folio = None
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue
        for line in text.split('\n'):
            # Track folio
            folio_match = re.search(r'Folio\s*(?:No)?:?\s*(\d+\s*/\s*\d+|\d+)', line, re.IGNORECASE)
            if folio_match:
                current_folio = folio_match.group(1).replace(" ", "")
            
            if 'INF109K010A6' in line:
                in_icici = True
                print(f"\n=== Start ICICI Section (Folio {current_folio}) Pg {i+1} ===")
            
            # Look for opening balance or cost
            if in_icici and ('opening' in line.lower() or '41605' in line or '41,605' in line):
                print(f"  {line.strip()[:100]}")
