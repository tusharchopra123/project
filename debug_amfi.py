import requests

url = "https://www.amfiindia.com/spages/NAVAll.txt"
print(f"Fetching {url}...")
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    lines = response.text.split('\n')
    print(f"Fetched {len(lines)} lines.")
    
    target_code = "122640" # Parag Parikh Flexi Cap Regular Plan
    found = False
    
    for line in lines:
        if target_code in line:
            print(f"\nFOUND LINE for {target_code}:")
            print(line.strip())
            parts = line.split(';')
            print(f"Split parts ({len(parts)}): {parts}")
            found = True
            
    if not found:
        print(f"\nISIN {target_isin} NOT FOUND in AMFI data.")
        
except Exception as e:
    print(f"Error: {e}")
