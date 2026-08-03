import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_transactions():
    base_dir = Path(__file__).resolve().parent.parent.parent
    input_file = base_dir / "DATASETS/raw/08_investor_transactions.csv"
    output_file = base_dir / "DATASETS/processed/investor_transactions.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting transactions cleaning. Input: {input_file}")

    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        return

    original_count = len(df)
    logging.info(f"Original row count: {original_count}")

    # 1. Fix inconsistent date formats & Parse date
    # Using format='mixed' to handle potential multiple formats safely
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    null_dates = df['transaction_date'].isnull().sum()
    if null_dates > 0:
        logging.warning(f"Found {null_dates} rows with invalid/missing transaction dates. Dropping them.")
        df = df.dropna(subset=['transaction_date'])

    # Format to YYYY-MM-DD
    df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d')

    # 2. Standardize transaction_type values
    df['transaction_type'] = df['transaction_type'].astype(str).str.strip()
    type_map = {
        'sip': 'SIP', 'SIP': 'SIP', 'Sip': 'SIP',
        'lumpsum': 'Lumpsum', 'LUMPSUM': 'Lumpsum', 'Lumpsum': 'Lumpsum',
        'redemption': 'Redemption', 'REDEMPTION': 'Redemption', 'Redemption': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].map(type_map)
    
    invalid_types = df['transaction_type'].isnull().sum()
    if invalid_types > 0:
        logging.warning(f"Found {invalid_types} rows with invalid transaction types. Dropping them.")
        df = df.dropna(subset=['transaction_type'])

    # 3. Validate amount_inr > 0
    df['amount_inr'] = pd.to_numeric(df['amount_inr'], errors='coerce')
    null_amounts = df['amount_inr'].isnull().sum()
    if null_amounts > 0:
        logging.warning(f"Found {null_amounts} rows with null/non-numeric amount. Dropping them.")
        df = df.dropna(subset=['amount_inr'])

    invalid_amounts = df[df['amount_inr'] <= 0]
    if not invalid_amounts.empty:
        logging.warning(f"Dropping {len(invalid_amounts)} records where amount_inr <= 0")
        df = df[df['amount_inr'] > 0]

    # 4. Validate KYC status enum values
    df['kyc_status'] = df['kyc_status'].astype(str).str.strip().str.title()
    valid_kyc = ['Verified', 'Pending']
    invalid_kyc = df[~df['kyc_status'].isin(valid_kyc)]
    if not invalid_kyc.empty:
        logging.warning(f"Dropping {len(invalid_kyc)} records with invalid KYC status.")
        df = df[df['kyc_status'].isin(valid_kyc)]

    # 5. Remove duplicates if any
    pre_dup_count = len(df)
    df = df.drop_duplicates()
    post_dup_count = len(df)
    if pre_dup_count != post_dup_count:
        logging.info(f"Removed {pre_dup_count - post_dup_count} duplicate records.")

    # Write cleaned file
    df.to_csv(output_file, index=False)
    logging.info(f"Cleaned transactions saved. New row count: {len(df)}. Saved to {output_file}")

if __name__ == "__main__":
    process_transactions()
