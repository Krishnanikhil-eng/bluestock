import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data():
    base_dir = Path(__file__).resolve().parent.parent.parent
    db_file = base_dir / "mutual_fund_analysis.db"
    schema_file = base_dir / "SOURCE CODE/sql/create_schema.sql"

    # CSV file paths
    nav_file = base_dir / "DATASETS/processed/nav_history.csv"
    trans_file = base_dir / "DATASETS/processed/investor_transactions.csv"
    perf_file = base_dir / "DATASETS/processed/scheme_performance.csv"
    fund_file = base_dir / "DATASETS/raw/01_fund_master.csv"
    aum_file = base_dir / "DATASETS/raw/03_aum_by_fund_house.csv"

    # 1. Initialize SQLite Database engine and enable Foreign Keys
    engine = create_engine(f"sqlite:///{db_file}")
    
    # 2. Re-create tables by running schema script
    # To make this script reproducible, we drop tables first before creating them
    tables_to_drop = ["fact_nav", "fact_transactions", "fact_performance", "fact_aum", "dim_fund", "dim_date"]
    
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF;"))
        for table in tables_to_drop:
            conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
            logging.info(f"Dropped table if exists: {table}")
        
        # Read and execute schema DDL
        with open(schema_file, 'r') as sf:
            schema_ddl = sf.read()
        
        # Split DDL by semicolon to execute step-by-step
        for statement in schema_ddl.split(';'):
            clean_stmt = statement.strip()
            if clean_stmt:
                conn.execute(text(clean_stmt))
        logging.info("Database schema created successfully.")
        conn.execute(text("PRAGMA foreign_keys = ON;"))

    # 3. Load Cleaned CSV Files
    logging.info("Reading processed/raw datasets...")
    df_nav = pd.read_csv(nav_file)
    df_trans = pd.read_csv(trans_file)
    df_perf = pd.read_csv(perf_file)
    df_fund_raw = pd.read_csv(fund_file)
    df_aum_raw = pd.read_csv(aum_file)

    # 4. Process dim_fund (drop extra columns not in DDL)
    fund_cols = [
        "amfi_code", "fund_house", "scheme_name", "category", "sub_category", "plan",
        "launch_date", "benchmark", "min_sip_amount", "min_lumpsum_amount", 
        "fund_manager", "risk_category", "sebi_category_code"
    ]
    df_fund = df_fund_raw[fund_cols].drop_duplicates(subset=["amfi_code"])

    # 5. Process dim_date (generate calendar attributes dynamically)
    logging.info("Generating dim_date dimension...")
    # Gather all unique dates
    nav_dates = df_nav['date'].unique()
    trans_dates = df_trans['transaction_date'].unique()
    aum_dates = df_aum_raw['date'].unique()
    
    all_dates = set(nav_dates).union(set(trans_dates)).union(set(aum_dates))
    df_date_raw = pd.DataFrame(sorted(list(all_dates)), columns=['date'])
    df_date_raw['date_dt'] = pd.to_datetime(df_date_raw['date'])
    
    df_date = pd.DataFrame()
    df_date['date'] = df_date_raw['date']
    df_date['year'] = df_date_raw['date_dt'].dt.year
    df_date['month'] = df_date_raw['date_dt'].dt.month
    df_date['day'] = df_date_raw['date_dt'].dt.day
    df_date['quarter'] = df_date_raw['date_dt'].dt.quarter
    df_date['day_of_week'] = df_date_raw['date_dt'].dt.dayofweek # 0=Monday, 6=Sunday
    df_date['is_weekend'] = df_date_raw['date_dt'].dt.dayofweek.isin([5, 6]).astype(int)

    # 6. Load dataframes using SQLAlchemy's to_sql
    # Specify connection with Pragma foreign keys ON for the transaction
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        
        # Load dimensions first
        logging.info("Loading dim_date...")
        df_date.to_sql("dim_date", con=conn, if_exists="append", index=False)
        
        logging.info("Loading dim_fund...")
        df_fund.to_sql("dim_fund", con=conn, if_exists="append", index=False)
        
        # Load facts
        logging.info("Loading fact_nav...")
        df_nav.to_sql("fact_nav", con=conn, if_exists="append", index=False)
        
        logging.info("Loading fact_transactions...")
        df_trans.to_sql("fact_transactions", con=conn, if_exists="append", index=False)
        
        logging.info("Loading fact_performance...")
        df_perf.to_sql("fact_performance", con=conn, if_exists="append", index=False)
        
        logging.info("Loading fact_aum...")
        df_aum_raw.to_sql("fact_aum", con=conn, if_exists="append", index=False)

    # 7. Verification: check row counts
    logging.info("Verifying row counts...")
    verification_results = {}
    with engine.connect() as conn:
        for table in ["dim_date", "dim_fund", "fact_nav", "fact_transactions", "fact_performance", "fact_aum"]:
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
            verification_results[table] = cnt

    # Expected counts
    expected_counts = {
        "dim_date": len(df_date),
        "dim_fund": len(df_fund),
        "fact_nav": len(df_nav),
        "fact_transactions": len(df_trans),
        "fact_performance": len(df_perf),
        "fact_aum": len(df_aum_raw)
    }

    # Print comparison
    mismatch = False
    print("\n" + "="*50)
    print("DATABASE LOADING ROW COUNT VERIFICATION")
    print("="*50)
    for table in expected_counts:
        db_cnt = verification_results[table]
        csv_cnt = expected_counts[table]
        status = "PASS" if db_cnt == csv_cnt else "FAIL"
        print(f"Table: {table:<18} | CSV Count: {csv_cnt:<6} | DB Count: {db_cnt:<6} | Status: {status}")
        if status == "FAIL":
            mismatch = True
    print("="*50 + "\n")

    if mismatch:
        logging.error("Verification failed: row counts do not match!")
    else:
        logging.info("All table load verifications passed successfully!")

if __name__ == "__main__":
    load_data()
