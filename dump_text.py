import pdfplumber

def dump_text():
    with pdfplumber.open("sample_cam.pdf", password="123456") as pdf:
        with open("dump.txt", "w", encoding="utf-8") as f:
            for i, page in enumerate(pdf.pages):
                f.write(f"--- Page {i+1} ---\n")
                text = page.extract_text()
                if text:
                    for j, line in enumerate(text.split('\n')):
                        f.write(f"{j}: {line}\n")
                f.write("\n")

if __name__ == "__main__":
    dump_text()
