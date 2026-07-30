import pandas as pd
from pathlib import Path

def validate_amfi_codes():
    fm_path = Path("data/raw/01_fund_master.csv")
    nav_path = Path("data/raw/02_nav_history.csv")

    df_fm = pd.read_csv(fm_path)
    df_nav = pd.read_csv(nav_path)

    fm_codes = set(df_fm['amfi_code'].unique())
    nav_codes = set(df_nav['amfi_code'].unique())

    matched_codes = fm_codes.intersection(nav_codes)
    missing_in_nav = fm_codes - nav_codes
    extra_in_nav = nav_codes - fm_codes

    print("=" * 60)
    print("AMFI CODE VALIDATION REPORT")
    print("=" * 60)
    print(f"Total Unique Schemes in Fund Master (`01_fund_master.csv`): {len(fm_codes)}")
    print(f"Total Unique Schemes in NAV History (`02_nav_history.csv`):  {len(nav_codes)}")
    print(f"Schemes Present in Both Datasets:                         {len(matched_codes)}")
    print(f"Match Coverage Rate:                                       {(len(matched_codes) / len(fm_codes)) * 100:.2f}%")
    print("-" * 60)
    
    if missing_in_nav:
        print(f"[WARNING] Missing in NAV History ({len(missing_in_nav)} codes): {missing_in_nav}")
    else:
        print("[CONFIRMED] 100% Match: EVERY AMFI code in fund_master exists in nav_history!")

    if extra_in_nav:
        print(f"[INFO] Extra codes in NAV History not in Fund Master ({len(extra_in_nav)} codes): {extra_in_nav}")
    else:
        print("[CONFIRMED] No extra unmapped codes found in nav_history.")

    print("\n" + "=" * 60)
    print("DATA QUALITY METRICS SUMMARY")
    print("=" * 60)
    
    # Check NAV History Quality
    total_nav_rows = len(df_nav)
    null_nav = df_nav['nav'].isnull().sum()
    null_dates = df_nav['date'].isnull().sum()
    duplicates = df_nav.duplicated(subset=['amfi_code', 'date']).sum()
    min_date = df_nav['date'].min()
    max_date = df_nav['date'].max()
    records_per_scheme = df_nav.groupby('amfi_code').size()

    print(f"* Total Historical NAV Records:   {total_nav_rows:,}")
    print(f"* Date Range Span:               {min_date} to {max_date}")
    print(f"* Duplicate (amfi_code, date):   {duplicates}")
    print(f"* Missing NAV Values:            {null_nav}")
    print(f"* Missing Date Values:           {null_dates}")
    print(f"* Records per Scheme (Min/Max):  {records_per_scheme.min()} / {records_per_scheme.max()}")
    print(f"* Average Records per Scheme:    {records_per_scheme.mean():.1f}")

    # Check Fund Master Quality
    fm_nulls = df_fm.isnull().sum()
    fm_null_cols = fm_nulls[fm_nulls > 0]
    print("\n* Fund Master Missing Value Check:")
    if fm_null_cols.empty:
        print("  - Zero missing values across all columns.")
    else:
        for col, count in fm_null_cols.items():
            print(f"  - Column '{col}': {count} missing values")

if __name__ == "__main__":
    validate_amfi_codes()

