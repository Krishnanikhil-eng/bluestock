import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_performance():
    base_dir = Path(__file__).resolve().parent.parent.parent
    input_file = base_dir / "DATASETS/raw/07_scheme_performance.csv"
    output_file = base_dir / "DATASETS/processed/scheme_performance.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting scheme performance cleaning. Input: {input_file}")

    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        return

    original_count = len(df)
    logging.info(f"Original row count: {original_count}")

    # Initialize anomaly flags
    df['is_anomaly'] = False
    df['anomaly_reason'] = ""

    # 1. Ensure all return columns are numeric
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct']
    for col in return_cols:
        if col in df.columns:
            # Check original nulls/non-numeric before coercion
            original_non_numeric = pd.to_numeric(df[col], errors='coerce').isnull() & df[col].notnull()
            if original_non_numeric.any():
                df.loc[original_non_numeric, 'is_anomaly'] = True
                df.loc[original_non_numeric, 'anomaly_reason'] += f"Non-numeric values in {col}; "
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            logging.warning(f"Return column {col} not found in dataset!")

    # 2. Validate expense_ratio is between 0.1% and 2.5%
    if 'expense_ratio_pct' in df.columns:
        df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
        invalid_expense = (df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5) | df['expense_ratio_pct'].isnull()
        if invalid_expense.any():
            df.loc[invalid_expense, 'is_anomaly'] = True
            df.loc[invalid_expense, 'anomaly_reason'] += "Expense ratio outside [0.1%, 2.5%]; "
    else:
        logging.warning("expense_ratio_pct column not found in dataset!")

    # 3. Check for any other nulls in key performance metric columns
    metric_cols = ['alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct', 'aum_crore']
    for col in metric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            null_vals = df[col].isnull()
            if null_vals.any():
                df.loc[null_vals, 'is_anomaly'] = True
                df.loc[null_vals, 'anomaly_reason'] += f"Missing metric {col}; "

    # 4. Check for morningstar rating range [1, 5]
    if 'morningstar_rating' in df.columns:
        df['morningstar_rating'] = pd.to_numeric(df['morningstar_rating'], errors='coerce')
        invalid_rating = (df['morningstar_rating'] < 1) | (df['morningstar_rating'] > 5) | df['morningstar_rating'].isnull()
        if invalid_rating.any():
            df.loc[invalid_rating, 'is_anomaly'] = True
            df.loc[invalid_rating, 'anomaly_reason'] += "Morningstar rating outside [1, 5]; "

    # Clean up anomaly reason string if no anomaly
    df.loc[~df['is_anomaly'], 'anomaly_reason'] = "None"
    # Clean trailing semicolon and space from reason
    df['anomaly_reason'] = df['anomaly_reason'].str.rstrip('; ')

    anomaly_count = df['is_anomaly'].sum()
    logging.info(f"Identified {anomaly_count} anomalous/invalid records out of {original_count}")

    # Remove duplicates
    pre_dup_count = len(df)
    df = df.drop_duplicates()
    post_dup_count = len(df)
    if pre_dup_count != post_dup_count:
        logging.info(f"Removed {pre_dup_count - post_dup_count} duplicate records.")

    # Write cleaned file
    df.to_csv(output_file, index=False)
    logging.info(f"Cleaned scheme performance saved. Row count: {len(df)}. Saved to {output_file}")

if __name__ == "__main__":
    process_performance()
