import pdfplumber
import re

def dump_potential_summary():
    print("Dumping potential summary rows from sample_cam_with_transaction.pdf...")
    with pdfplumber.open("sample_cam_with_transaction.pdf", password="123456") as pdf:
        count = 0
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            lines = text.split('\n')
            for line in lines:
                # Heuristic for Summary Row:
                # 1. Has numbers (Cost, Value, Units)
                numbers = re.findall(r'([\d,]+\.\d+)', line)
                if len(numbers) >= 2:
                    # 2. Not a transaction
                    if re.search(r'^\s*\d{2}[-./]\w{3}', line): continue
                    # 3. Not Closing Balance line
                    if "closing unit balance" in line.lower(): continue
                    # 4. Not Page number
                    if "page" in line.lower(): continue
                    
                    print(f"ROW: {line.strip()}")
                    count += 1
                    if count > 50: return # Limit output

if __name__ == "__main__":
    dump_potential_summary()
