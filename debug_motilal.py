from backend.parser import parse_cam_pdf

data = parse_cam_pdf("sample_cam_with_transaction.pdf", password="123456")

# Find only Nasdaq 100 Fund (INF247L01718)
nasdaq = [d for d in data if d.get("isin") == "INF247L01718"]

print(f"Found {len(nasdaq)} entries for INF247L01718:")
for d in nasdaq:
    if d['type'] == 'transaction':
        raw = d.get('raw_desc', 'No raw')
        print(f"  Amt: {d.get('amount',0):>10.2f}  Raw: {raw[:80]}")
    else:
        print(f"  Type: {d['type']}, Val: {d.get('current_value',0)}")
