import pdfplumber
import re

def debug_icici():
    print("Scanning for P8104 / INF109K010A6 ...")
    with pdfplumber.open("sample_cam.pdf", password="123456") as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    # Check for partial folio or ISIN
                    if "ICICI Prudential Banking" in line or "INF109K010A6" in line:
                        print(f"--- MATCH FOUND at Page {page.page_number} Index {i} ---")
                        # Print context
                        start = max(0, i-5)
                        end = min(len(lines), i+20)
                        for j in range(start, end):
                            print(f"{j}: {lines[j]}")

if __name__ == "__main__":
    debug_icici()
