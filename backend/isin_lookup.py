"""
ISIN to Fund Name lookup using AMFI NAV data
"""
import requests
import re
from functools import lru_cache

AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

@lru_cache(maxsize=1)
def _fetch_isin_mapping():
    """Fetch AMFI NAV data and build ISIN -> {name, code} mapping"""
    isin_map = {}
    try:
        response = requests.get(AMFI_NAV_URL, timeout=10)
        response.raise_for_status()
        
        for line in response.text.split('\n'):
            parts = line.split(';')
            if len(parts) >= 4:
                # Format: SchemeCode;ISIN1;ISIN2;SchemeName;NAV;Date
                scheme_code = parts[0].strip()
                scheme_name = parts[3].strip()
                # Extract all ISINs in columns 1 and 2
                for col in [1, 2]:
                    isin = parts[col].strip()
                    if isin and isin.startswith('INF') and len(isin) == 12:
                        isin_map[isin] = {"name": scheme_name, "code": scheme_code}
    except Exception as e:
        print(f"Warning: Could not fetch AMFI data: {e}")
    
    return isin_map


# Static mapping for old/legacy ISINs that might not be in the current AMFI file
STATIC_MAPPING = {
    "INF740K01031": {"name": "Parag Parikh Flexi Cap (Direct)", "code": "122639"},
    # Add more as discovered
}

def get_scheme_details(isin: str) -> dict:
    """
    Get scheme details (name, code) for an ISIN.
    Returns dict with 'name' and 'code' keys, or None if not found.
    """
    if not isin:
        return None
        
    isin = isin.strip().upper()
        
    # Check static mapping first or last? 
    # Maybe first is faster for known issues.
    if isin in STATIC_MAPPING:
        return STATIC_MAPPING[isin]

    isin_map = _fetch_isin_mapping()
    details = isin_map.get(isin)
    
    if details:
        # Clean up name as before
        name = details['name']
        name = re.sub(r'\s*-\s*(Direct|Regular)\s*(Plan)?.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([^)]*erstwhile[^)]*\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*-\s*(Growth|IDCW|Dividend|Bonus).*$', '', name, flags=re.IGNORECASE)
        return {"name": name.strip(), "code": details['code']}
        
    return None

def get_scheme_name(isin: str) -> str:
    """
    Get scheme name for an ISIN from AMFI data.
    Returns cleaned-up name.
    """
    details = get_scheme_details(isin)
    return details['name'] if details else ""


# Test
if __name__ == "__main__":
    test_isins = ["INF109K016L0", "INF179K01WA6", "INF109K010A6"]
    print("Testing ISIN lookup:")
    for isin in test_isins:
        name = get_scheme_name(isin)
        print(f"  {isin}: {name[:60] if name else 'NOT FOUND'}")
