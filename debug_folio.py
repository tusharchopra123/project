import pdfplumber
import re

with pdfplumber.open("sample_cam_with_transaction.pdf", password="123456") as pdf:
    for page in pdf.pages[:3]:  # First 3 pages
        text = page.extract_text()
        if not text:
            continue
        lines = text.split('\n')
        for line in lines:
            # Look for folio patterns
            if re.search(r'folio|^\d+/\d+', line.lower()):
                print(f"FOLIO LINE: {line.strip()[:80]}")
