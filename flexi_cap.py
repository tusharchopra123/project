import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mftool import Mftool
import yfinance as yf
from datetime import datetime, timedelta
import io

# ==========================================
# 1. USER CONFIGURATION
# ==========================================
MY_FUNDS = {
    # --- FLEXI CAP FUNDS (Direct Growth Only) ---
    '151796': '360 ONE FLEXICAP FUND-DIRECT PLAN- GROWTH',
    '154043': 'Abakkus Flexi Cap Fund - Direct - Growth',
    '120564': 'Aditya Birla Sun Life Flexi Cap Fund - Growth - Direct Plan',
    '141925': 'Axis Flexi Cap Fund - Direct Plan - Growth',
    '151895': 'Bajaj Finserv Flexi Cap Fund-Direct Plan-Growth',
    '118424': 'BANDHAN Flexi Cap Fund-Direct Plan-Growth',
    '148404': 'BANK OF INDIA Flexi Cap Fund Direct Plan -Growth',
    '150387': 'Baroda BNP Paribas Flexi Cap Fund - Direct Plan - Growth Option',
    '118275': 'CANARA ROBECO FLEXICAP FUND - DIRECT PLAN - GROWTH OPTION',
    '153738': 'CAPITALMIND FLEXI CAP FUND DIRECT GROWTH',
    '119076': 'DSP Flexi Cap Fund - Direct Plan - Growth',
    '140353': 'Edelweiss Flexi Cap Fund - Direct Plan - Growth Option',
    '118535': 'Franklin India Flexi Cap Fund - Direct - Growth',
    '118955': 'HDFC Flexi Cap Fund - Growth Option - Direct Plan',
    '152135': 'Helios Flexi Cap Fund - Direct Plan - Growth Option',
    '120046': 'HSBC Flexi Cap Fund - Direct Growth',
    '148990': 'ICICI Prudential Flexicap Fund - Direct Plan - Growth',
    '149763': 'Invesco India Flexi Cap Fund - Direct Plan - Growth',
    '151379': 'ITI Flexi Cap Fund- Direct Plan- Growth',
    '153859': 'JioBlackRock Flexi Cap Fund - Direct Plan - Growth Option',
    '120492': 'JM Flexicap Fund (Direct) - Growth Option',
    '120166': 'Kotak Flexicap Fund - Growth - Direct',
    '120264': 'LIC MF Flexi Cap Fund-Direct Plan-Growth',
    '149104': 'Mahindra Manulife Flexi Cap Fund - Direct Plan -Growth',
    '151412': 'Mirae Asset Flexi Cap Fund - Direct Plan - Growth',
    '129046': 'Motilal Oswal Flexi cap Fund Direct Plan-Growth Option',
    '143793': 'Navi Flexi Cap Fund - Direct Plan - Growth',
    '149094': 'Nippon India Flexi Cap Fund - Direct Plan - Growth Plan - Growth Option',
    '151917': 'NJ Flexi Cap Fund - Direct Plan - Growth Option',
    '133839': 'PGIM India Flexi Cap Fund - Direct Plan - Growth Option',
    '122639': 'Parag Parikh Flexi Cap Fund - Direct Plan - Growth',
    '120843': 'quant Flexi Cap Fund - Growth Option-Direct Plan',
    '149450': 'Samco Flexi Cap Fund - Direct Plan - Growth Option',
    '119718': 'SBI Flexicap Fund - DIRECT PLAN - Growth Option',
    '144905': 'Shriram Flexi Cap Fund - Direct Growth',
    '150571': 'Sundaram Flexicap Fund Direct Growth',
    '144546': 'Tata Flexi Cap Fund-Direct Plan-Growth',
    '118883': 'Taurus Flexi Cap Fund - Direct Plan - Growth',
    '153872': 'THE WEALTH COMPANY FLEXI CAP FUND - DIRECT GROWTH',
    '152584': 'TRUSTMF Flexi Cap Fund-Direct Plan- Growth',
    '153543': 'Unifi Flexi Cap Fund - Direct Growth',
    '119292': 'Union Flexi Cap Fund - Direct Plan - Growth Option',
    '120662': 'UTI - Flexi Cap Fund-Growth Option - Direct',
    '150346': 'WhiteOak Capital Flexi Cap Fund Direct Plan-Growth',
}

BENCHMARK_TICKER = '^NSEI'  # Nifty 50
BENCHMARK_LABEL = 'Nifty 50'
YEARS_OF_DATA = 10          
ROLLING_WINDOW = 3          
RISK_FREE_RATE = 0.06       

# ==========================================
# 2. DATA ENGINE
# ==========================================
mf = Mftool()

def search_fund():
    """Interactive helper to find the AMFI Scheme Code"""
    print("\n--- FUND SEARCH TOOL ---")
    query = input("Enter a part of the fund name (e.g., 'hdfc top 100'): ")
    print(f"Searching for '{query}'...")
    try:
        all_schemes = mf.get_scheme_codes()
        matches = {k:v for k,v in all_schemes.items() if query.lower() in v.lower()}
        if not matches:
            print("No matches found. Try a shorter name.")
            return
        print(f"\nFound {len(matches)} matches. Copy the 'Code' for your config:")
        print("-" * 90)
        print(f"{'CODE':<10} | {'NAME'}")
        print("-" * 90)
        for code, name in matches.items():
            print(f"{code:<10} | {name}")
        print("-" * 90 + "\n")
    except Exception as e:
        print(f"Error connecting to AMFI: {e}")

def get_data_from_yahoo(ticker, years):
    """Fetcher for ETFs and Benchmarks via Yahoo Finance"""
    start_date = (datetime.now() - timedelta(days=years*365 + 365)).strftime('%Y-%m-%d')
    try:
        df = yf.download(ticker, start=start_date, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            try: series = df['Adj Close'].iloc[:, 0]
            except: series = df['Close'].iloc[:, 0]
        else:
            if 'Adj Close' in df.columns: series = df['Adj Close']
            else: series = df['Close']
        series = pd.to_numeric(series, errors='coerce').dropna()
        series.sort_index(ascending=True, inplace=True)
        return series
    except: return None

def get_fund_nav(code, label):
    # === HYBRID LOGIC ===
    # If code ends with .NS or .BO, assume it is an ETF/Stock and use Yahoo
    if '.NS' in str(code) or '.BO' in str(code):
        print(f"-> Fetching ETF/Stock {label} ({code}) via Yahoo...")
        return get_data_from_yahoo(code, YEARS_OF_DATA)
    
    # Otherwise, assume it is a Mutual Fund and use AMFI
    print(f"-> Fetching MF {label} ({code}) via AMFI...")
    try:
        data = mf.get_scheme_historical_nav(code, as_json=False)
        if not data or 'data' not in data: return None
        df = pd.DataFrame(data['data'])
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        df['nav'] = pd.to_numeric(df['nav'])
        df.set_index('date', inplace=True)
        # FORCE ASCENDING ORDER
        df.sort_index(ascending=True, inplace=True)
        return df['nav']
    except: return None

def get_benchmark_data(ticker, years):
    print(f"-> Fetching Benchmark {ticker}...")
    return get_data_from_yahoo(ticker, years)

# ==========================================
# 3. METRICS ENGINE (UPDATED)
# ==========================================
def calculate_all_metrics(fund_series, bench_series):
    # Align data by date
    df = pd.DataFrame({'Fund': fund_series, 'Bench': bench_series}).dropna()
    if df.empty or len(df) < 20: return None
    
    # --- FUND LIFE (Calendar Years) ---
    fund_life_years = (df.index[-1] - df.index[0]).days / 365.25

    ret = df.pct_change().dropna()
    if ret.empty: return None

    TRADING_DAYS = 252
    days = len(ret)
    
    cagr_f = (1 + ret['Fund']).prod() ** (TRADING_DAYS / days) - 1
    bench_cagr = (1 + ret['Bench']).prod() ** (TRADING_DAYS / days) - 1
    
    vol = ret['Fund'].std() * np.sqrt(TRADING_DAYS)
    sharpe = (cagr_f - RISK_FREE_RATE) / vol if vol != 0 else 0
    
    rf_daily = (1 + RISK_FREE_RATE) ** (1/TRADING_DAYS) - 1
    neg_excess = np.minimum(ret['Fund'] - rf_daily, 0)
    down_dev = np.sqrt(np.mean(neg_excess**2)) * np.sqrt(TRADING_DAYS)
    sortino = (cagr_f - RISK_FREE_RATE) / down_dev if down_dev != 0 else 0
    
    # --- DRAWDOWN & RECOVERY LOGIC (UPDATED) ---
    cumulative = (1 + ret['Fund']).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_dd = drawdown.min()

    # 1. Find the date of the lowest point (Valley)
    max_dd_date = drawdown.idxmin()
    
    # 2. Find the Peak value *before* or *at* that valley
    peak_val_at_valley = peak.loc[max_dd_date]
    
    # 3. Look at data *after* the valley to find when we crossed that peak
    post_valley_data = cumulative.loc[max_dd_date:]
    
    # Filter for days where NAV is >= Peak
    recovery_indices = post_valley_data[post_valley_data >= peak_val_at_valley].index
    
    # Exclude the valley date itself (unless it was a 0% drop, which is trivial)
    real_recovery_dates = recovery_indices[recovery_indices > max_dd_date]
    
    if len(real_recovery_dates) > 0:
        recovery_date = real_recovery_dates[0]
        recovery_days = (recovery_date - max_dd_date).days
    else:
        recovery_days = "Unrecovered"
    
    cov = ret['Fund'].cov(ret['Bench'])
    var = ret['Bench'].var()
    beta = cov / var if var != 0 else 0
    alpha = cagr_f - (RISK_FREE_RATE + beta * (bench_cagr - RISK_FREE_RATE))
    
    active_ret = ret['Fund'] - ret['Bench']
    tracking_error = active_ret.std() * np.sqrt(TRADING_DAYS)
    info_ratio = (cagr_f - bench_cagr) / tracking_error if tracking_error != 0 else 0
    
    up_mkt = ret[ret['Bench'] >= 0]
    up_cap = ((1 + up_mkt['Fund']).prod()**(TRADING_DAYS/len(up_mkt)) - 1) / \
             ((1 + up_mkt['Bench']).prod()**(TRADING_DAYS/len(up_mkt)) - 1) * 100 if len(up_mkt)>0 else 0
    down_mkt = ret[ret['Bench'] < 0]
    down_cap = ((1 + down_mkt['Fund']).prod()**(TRADING_DAYS/len(down_mkt)) - 1) / \
               ((1 + down_mkt['Bench']).prod()**(TRADING_DAYS/len(down_mkt)) - 1) * 100 if len(down_mkt)>0 else 0

    return {
        'FundLife': fund_life_years,
        'CAGR': cagr_f, 'Alpha': alpha, 'Beta': beta, 'InfoRatio': info_ratio,
        'Sharpe': sharpe, 'Sortino': sortino, 
        'MaxDD': max_dd, 'RecDays': recovery_days, # New Metric
        'UpCap': up_cap, 'DownCap': down_cap
    }

def get_rolling_stats(series, years):
    window = int(years * 252)
    if len(series) < window: return None, None
    roll = (series / series.shift(window))**(1/years) - 1
    roll = roll.dropna()
    if roll.empty: return None, None
    return {'Avg': roll.mean(), 'Max': roll.max(), 'Min': roll.min(), 'Pos': (roll > 0).mean()}, roll

# ==========================================
# 4. EXCEL FORMATTING ENGINE
# ==========================================
def clean_name_for_legend(name):
    short = name.split('-')[0].strip()
    short = short.split('(')[0].strip()
    return short

def run_analysis():
    print("Initializing Analysis...")
    bench_data = get_benchmark_data(BENCHMARK_TICKER, YEARS_OF_DATA)
    if bench_data is None: 
        print("Critical Error: Could not fetch Benchmark data.")
        return

    all_funds = {BENCHMARK_LABEL: bench_data}
    
    for code, label in MY_FUNDS.items():
        s = get_fund_nav(code, label)
        if s is not None: 
            all_funds[label] = s
            
    if len(all_funds) < 2:
        print("Error: No fund data fetched successfully.")
        return

    final_table = {}
    rolling_df = pd.DataFrame()
    b_series = all_funds[BENCHMARK_LABEL]

    for label, series in all_funds.items():
        if label == BENCHMARK_LABEL: m = calculate_all_metrics(b_series, b_series)
        else: m = calculate_all_metrics(series, b_series)
        
        r_stats, r_series = get_rolling_stats(series, ROLLING_WINDOW)
        
        if m is None:
            print(f"  [Skipping] Data too short/empty for {label}")
            continue

        if r_stats is None:
            r_stats = {'Avg': np.nan, 'Max': np.nan, 'Min': np.nan, 'Pos': np.nan}
            print(f"  [Note] {label} is too young for {ROLLING_WINDOW}-year rolling stats.")
        else:
            rolling_df[label] = r_series

        final_table[label] = [
            m['FundLife'],
            m['CAGR'], m['Alpha'], m['Beta'], m['InfoRatio'], m['Sharpe'], m['Sortino'], 
            m['MaxDD'], m['RecDays'], # Added here
            m['UpCap'], m['DownCap'], 
            r_stats['Avg'], r_stats['Max'], r_stats['Min'], r_stats['Pos']
        ]

    if not final_table:
        print("No valid data generated.")
        return

    # Updated Column Headers
    columns = [
        'Fund Life (Yrs)',
        'CAGR', 'Alpha', 'Beta', 'Info Ratio', 'Sharpe Ratio', 'Sortino Ratio', 
        'Max Drawdown', 'MaxDD Rec. (Days)', 
        'Upside Capture', 'Downside Capture', 
        f'Avg Roll {ROLLING_WINDOW}Y', f'Max Roll {ROLLING_WINDOW}Y', 
        f'Min Roll {ROLLING_WINDOW}Y', '% Positive'
    ]
    df_results = pd.DataFrame(final_table, index=columns).T

    filename = "Pro_Fund_Report_Final.xlsx"
    print(f"\nFormatting and writing to {filename}...")
    
    try:
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        workbook = writer.book
        
        # Formats
        fmt_percent = workbook.add_format({'num_format': '0.00%'})
        fmt_decimal = workbook.add_format({'num_format': '0.00'})
        fmt_number  = workbook.add_format({'num_format': '0.0'})
        fmt_days    = workbook.add_format({'num_format': '0', 'align': 'center'}) # For Days
        fmt_red     = workbook.add_format({'font_color': '#9C0006', 'bg_color': '#FFC7CE'})
        fmt_yellow  = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C5700'}) 
        
        df_results.to_excel(writer, sheet_name='Summary')
        worksheet = writer.sheets['Summary']
        
        # Apply Column Widths & Formats
        worksheet.set_column('B:B', 8, fmt_number)   # Fund Life
        worksheet.set_column('C:D', 12, fmt_percent) # CAGR, Alpha
        worksheet.set_column('E:H', 12, fmt_decimal) # Beta to Sortino
        worksheet.set_column('I:I', 12, fmt_percent) # MaxDD
        worksheet.set_column('J:J', 15, fmt_days)    # MaxDD Recovery (Days) - NEW
        worksheet.set_column('K:L', 15, fmt_decimal) # Capture Ratios
        worksheet.set_column('M:P', 15, fmt_percent) # Rolling Stats
        
        # Conditional Formatting (Red for negative numbers)
        worksheet.conditional_format('C2:P100', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': fmt_red})
        
        # Conditional Formatting (Yellow for young funds)
        worksheet.conditional_format('B2:B100', {'type': 'cell', 'criteria': '<', 'value': 3, 'format': fmt_yellow})

        if not rolling_df.empty:
            rolling_df.to_excel(writer, sheet_name='Rolling Data')
            worksheet_chart = workbook.add_worksheet('Charts')
            
            plt.figure(figsize=(14, 8)) 
            
            for col in rolling_df.columns:
                style = '--' if col == BENCHMARK_LABEL else '-'
                width = 2.5 if col == BENCHMARK_LABEL else 1.5
                color = 'black' if col == BENCHMARK_LABEL else None
                short_label = clean_name_for_legend(col)
                plt.plot(rolling_df.index, rolling_df[col], label=short_label, linestyle=style, linewidth=width, color=color)
            
            plt.axhline(0, color='red', alpha=0.3)
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:.0%}".format(x)))
            plt.title(f'{ROLLING_WINDOW}-Year Rolling Returns (Daily Steps)')
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, fontsize='medium')
            plt.grid(True, alpha=0.3)
            
            img_data = io.BytesIO()
            plt.savefig(img_data, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            
            worksheet_chart.insert_image('B2', 'rolling_plot.png', {'image_data': img_data})

        writer.close()
        print("Success! Open 'Pro_Fund_Report_Final.xlsx'.")
    except PermissionError:
        print("\nERROR: Could not save file. Close Excel and try again.")

if __name__ == "__main__":
    while True:
        print("\nSelect Mode:")
        print("1. Search for Fund Codes (AMFI)")
        print("2. Run Portfolio Analysis")
        print("3. Exit")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1': search_fund()
        elif choice == '2': run_analysis(); break
        elif choice == '3': break