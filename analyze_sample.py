import pdfplumber

def analyze_pdf(path, password):
    print(f"Analyzing {path}...")
    try:
        with pdfplumber.open(path, password=password) as pdf:
            print(f"Total Pages: {len(pdf.pages)}")
            if len(pdf.pages) > 0:
                page = pdf.pages[0]
                print("\n--- Page 1 Text (First 1000 chars) ---")
                print(page.extract_text()[:1000])
                print("\n--- Page 1 Tables ---")
                tables = page.extract_tables()
                print(f"Found {len(tables)} tables")
                if tables:
                    for i, table in enumerate(tables):
                        print(f"Table {i} (First row): {table[0] if table else 'Empty'}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_pdf("sample_cam.pdf", "123456")
