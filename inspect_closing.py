import pdfplumber

def inspect_closing_lines():
    print("Inspecting Closing Unit Balance lines in sample_cam_with_transaction.pdf...")
    with pdfplumber.open("sample_cam_with_transaction.pdf", password="123456") as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if "closing unit balance" in line.lower():
                    start = max(0, i-2)
                    end = min(len(lines), i+4)
                    print(f"--- Context ---")
                    for j in range(start, end):
                        print(lines[j].strip())

if __name__ == "__main__":
    inspect_closing_lines()
