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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(AMFI_NAV_URL, headers=headers, timeout=15)
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
        pass

    
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
