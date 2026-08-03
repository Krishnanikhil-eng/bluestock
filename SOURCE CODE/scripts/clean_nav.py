import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_nav():
    # Paths relative to the script location
    base_dir = Path(__file__).resolve().parent.parent.parent
    input_file = base_dir / "DATASETS/raw/02_nav_history.csv"
    output_file = base_dir / "DATASETS/processed/nav_history.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting NAV history cleaning. Input: {input_file}")

    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        return

    original_count = len(df)
    logging.info(f"Original row count: {original_count}")

    # 1. Parse date to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    null_dates = df['date'].isnull().sum()
    if null_dates > 0:
        logging.warning(f"Found {null_dates} rows with invalid dates. Dropping them.")
        df = df.dropna(subset=['date'])

    # 2. Ensure nav is numeric and validate nav > 0
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    null_navs = df['nav'].isnull().sum()
    if null_navs > 0:
        logging.warning(f"Found {null_navs} rows with null/non-numeric NAV. Dropping them.")
        df = df.dropna(subset=['nav'])

    # Validate nav > 0
    invalid_navs = df[df['nav'] <= 0]
    if not invalid_navs.empty:
        logging.warning(f"Dropping {len(invalid_navs)} records where nav <= 0")
        df = df[df['nav'] > 0]

    # 3. Remove duplicate records (based on amfi_code and date)
    pre_dup_count = len(df)
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    post_dup_count = len(df)
    if pre_dup_count != post_dup_count:
        logging.info(f"Removed {pre_dup_count - post_dup_count} duplicate records.")

    # 4. Sort by amfi_code and date
    df = df.sort_values(by=['amfi_code', 'date'])

    # 5. Forward-fill missing nav values for holidays/weekends
    cleaned_dfs = []
    for amfi_code, group in df.groupby('amfi_code'):
        min_date = group['date'].min()
        max_date = group['date'].max()
        
        # Create full date range from min to max date
        full_date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Reindex the group to fill missing days
        group_reindexed = group.set_index('date').reindex(full_date_range)
        
        # Forward fill NAV values
        group_reindexed['nav'] = group_reindexed['nav'].ffill()
        
        # Fill amfi_code back
        group_reindexed['amfi_code'] = amfi_code
        
        # Reset index back to 'date'
        group_cleaned = group_reindexed.reset_index().rename(columns={'index': 'date'})
        cleaned_dfs.append(group_cleaned)

    # Combine back
    df_cleaned = pd.concat(cleaned_dfs, ignore_index=True)

    # Ensure amfi_code is integer
    df_cleaned['amfi_code'] = df_cleaned['amfi_code'].astype(int)

    # Re-verify NAV > 0 and no null values remain
    df_cleaned = df_cleaned.dropna(subset=['nav'])
    df_cleaned = df_cleaned[df_cleaned['nav'] > 0]

    # Sort final dataframe
    df_cleaned = df_cleaned.sort_values(by=['amfi_code', 'date'])

    # Write cleaned file
    df_cleaned.to_csv(output_file, index=False)
    logging.info(f"Cleaned NAV history saved. New row count: {len(df_cleaned)}. Saved to {output_file}")

if __name__ == "__main__":
    process_nav()
