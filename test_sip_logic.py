
from datetime import date, timedelta
import pandas as pd
import numpy as np

def is_sip_active(transactions):
    """
    Determine if a scheme has an active SIP.
    Logic:
    1. At least 3 purchases.
    2. Last purchase within ~45 days.
    3. Regular intervals (low stdev of days between purchases).
    """
    if not transactions:
        return False
        
    # Filter for purchases (negative amount)
    purchases = [t for t in transactions if float(t['amount']) < 0]
    
    if len(purchases) < 3:
        return False
        
    # Sort by date
    try:
        # Check if date is string or object
        dates = sorted([pd.to_datetime(t['date']).date() for t in purchases])
    except:
        return False
        
    last_date = dates[-1]
    days_since_last = (date.today() - last_date).days
    
    # 1. Recency check (allow some buffer for weekends/processing)
    if days_since_last > 45:
        return False
        
    # 2. Regularity check
    # taking last 6 transactions to check regularity
    recent_dates = dates[-6:]
    if len(recent_dates) < 3:
        return False # Should be covered by len check above but safe
        
    intervals = []
    for i in range(1, len(recent_dates)):
        delta = (recent_dates[i] - recent_dates[i-1]).days
        intervals.append(delta)
        
    # SIPs are usually ~30 days. Weekly SIPs ~7 days.
    # We check consistency.
    avg_interval = np.mean(intervals)
    std_dev_interval = np.std(intervals)
    
    # If standard deviation is low relative to mean, it's regular.
    # CoV (Coefficient of Variation) < 0.2 (20% variance allowed)
    if avg_interval > 0:
        cov = std_dev_interval / avg_interval
        # Allow monthly (28-31) or weekly (7)
        # Filter out random lumpsums
        if cov < 0.25:
            return True
            
    return False

# Test Cases
today = date.today()

# Case 1: Active Monthly SIP
case1 = [
    {'date': (today - timedelta(days=30*i)).isoformat(), 'amount': -5000} for i in range(6)
]
print(f"Case 1 (Active Monthly): {is_sip_active(case1)}")

# Case 2: Stopped SIP (Last tx 60 days ago)
case2 = [
    {'date': (today - timedelta(days=60 + 30*i)).isoformat(), 'amount': -5000} for i in range(6)
]
print(f"Case 2 (Stopped SIP): {is_sip_active(case2)}")

# Case 3: Random Lumpsums
case3 = [
    {'date': (today - timedelta(days=10)).isoformat(), 'amount': -5000},
    {'date': (today - timedelta(days=50)).isoformat(), 'amount': -10000},
    {'date': (today - timedelta(days=180)).isoformat(), 'amount': -5000},
    {'date': (today - timedelta(days=200)).isoformat(), 'amount': -5000},
]
print(f"Case 3 (Random Lumpsums): {is_sip_active(case3)}")

# Case 4: Few Transactions
case4 = [
    {'date': (today - timedelta(days=10)).isoformat(), 'amount': -5000},
    {'date': (today - timedelta(days=40)).isoformat(), 'amount': -5000},
]
print(f"Case 4 (Few Txs): {is_sip_active(case4)}")

