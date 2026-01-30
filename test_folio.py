from backend.parser import parse_cam_pdf
from backend.models import analyze_portfolio
import pandas as pd

data = parse_cam_pdf("sample_cam_with_transaction.pdf", password="123456")
df = pd.DataFrame(data)
result = analyze_portfolio(df)

# Check ICICI Banking fund entries
icici = [h for h in result['holdings'] if 'ICICI' in h.get('description','') and 'Banking' in h.get('description','')]
print(f"ICICI Banking entries: {len(icici)}")
for h in icici:
    print(f"  Inv={h['amount']:,.0f}, Val={h['current_value']:,.0f}")
