import requests
import re
from functools import lru_cache
from sqlalchemy import select
from ..core.database import SessionLocal
from ..models import ISINMapping

AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

# Common headers to avoid blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

@lru_cache(maxsize=1)
def _fetch_isin_mapping_full():
    """
    Directly fetch AMFI data. This is prone to timeouts on cloud IPs.
    We'll mostly rely on get_scheme_details to handle individual lookups.
    """
    isin_map = {}
    try:
        # Using stream=True to handle large files better
        with requests.get(AMFI_NAV_URL, headers=HEADERS, timeout=15, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line: continue
                parts = line.split(';')
                if len(parts) >= 4:
                    scheme_code = parts[0].strip()
                    scheme_name = parts[3].strip()
                    for col in [1, 2]:
                        isin = parts[col].strip()
                        if isin and isin.startswith('INF') and len(isin) == 12:
                            isin_map[isin] = {"name": scheme_name, "code": scheme_code}
        print(f"DEBUG: Successfully fetched full AMFI map ({len(isin_map)} entries)")
    except Exception as e:
        print(f"DEBUG: Full AMFI fetch timed out/failed: {e}")
    return isin_map

# Static mapping for old/legacy ISINs that might not be in the current AMFI file
STATIC_MAPPING = {
    "INF740K01031": {"name": "Parag Parikh Flexi Cap (Direct)", "code": "122639"},
    "INF109K010A6": {"name": "ICICI Prudential Banking and PSU Debt Fund", "code": "101648"},
}

def clean_scheme_name(name: str) -> str:
    """Utility to remove junk from scheme names (PDF artifacts, direct/regular labels)"""
    if not name:
        return ""
    name = re.sub(r'^[A-Z0-9]{3,8}-', '', name)
    name = re.sub(r'\s*-\s*(Direct|Regular)\s*(Plan)?.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\([^)]*erstwhile[^)]*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*(Growth|IDCW|Dividend|Bonus).*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*\(.*$', '', name)
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
    return name.strip()

async def get_scheme_details(isin: str) -> dict:
    """
    Get scheme details (name, code) for an ISIN.
    Order: 
    1. Static Mapping
    2. DB Cache
    3. mfapi.in search (single isin)
    4. Full AMFI fetch (last resort)
    """
    if not isin: return None
    isin = isin.strip().upper()
    
    # 1. Static Mapping
    if isin in STATIC_MAPPING:
        return STATIC_MAPPING[isin]

    # 2. Check DB Cache
    try:
        async with SessionLocal() as db:
            res = await db.execute(select(ISINMapping).filter(ISINMapping.isin == isin))
            cached = res.scalars().first()
            if cached:
                return {"name": clean_scheme_name(cached.scheme_name), "code": cached.scheme_code}
    except Exception as e:
        print(f"DEBUG: DB Cache error: {e}")

    # 3. mfapi.in Fallback (Search by ISIN)
    # This is much faster and more reliable than the full AMFI file
    try:
        search_url = f"https://api.mfapi.in/mf/search?q={isin}"
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Take the best match
                match = data[0]
                details = {"name": clean_scheme_name(match['schemeName']), "code": str(match['schemeCode'])}
                
                # Cache it in DB for future
                try:
                    async with SessionLocal() as db:
                        new_entry = ISINMapping(isin=isin, scheme_code=details['code'], scheme_name=match['schemeName'])
                        db.add(new_entry)
                        await db.commit()
                except: pass
                
                return details
    except Exception as e:
        print(f"DEBUG: mfapi.in lookup failed for {isin}: {e}")

    # 4. Final Resort: Try to find in full AMFI (might hit timeout)
    # Note: This is now a sync call inside our async function, might block 
    # but it's a last resort anyway.
    isin_map = _fetch_isin_mapping_full()
    details = isin_map.get(isin)
    
    if details:
        details['name'] = clean_scheme_name(details['name'])
        # Cache it
        try:
            async with SessionLocal() as db:
                new_entry = ISINMapping(isin=isin, scheme_code=details['code'], scheme_name=details['name'])
                db.add(new_entry)
                await db.commit()
        except: pass
        return details
        
    return None

async def get_scheme_name(isin: str) -> str:
    """Helper for parsed results"""
    details = await get_scheme_details(isin)
    return details['name'] if details else ""
