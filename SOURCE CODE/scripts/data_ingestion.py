"""
Data Ingestion Module for Bluestock Mutual Fund Project
========================================================
This script verifies raw dataset file presence and integrity in DATASETS/raw/
before processing through the cleaning pipeline.
"""

import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify_raw_datasets():
    """Verify presence of required raw CSV files."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    raw_dir = base_dir / "DATASETS" / "raw"
    
    required_files = [
        "01_fund_master.csv",
        "02_nav_history.csv",
        "03_aum_by_fund_house.csv",
        "07_scheme_performance.csv",
        "08_investor_transactions.csv",
        "09_portfolio_holdings.csv"
    ]
    
    missing = []
    for f in required_files:
        file_path = raw_dir / f
        if not file_path.exists():
            missing.append(f)
            logging.error(f"Missing required raw file: {file_path}")
        else:
            logging.info(f"Verified raw file present: {f} ({os.path.getsize(file_path)} bytes)")
            
    if missing:
        raise FileNotFoundError(f"Missing {len(missing)} raw dataset files: {missing}")
        
    logging.info("All raw dataset files successfully verified.")
    return True

if __name__ == '__main__':
    verify_raw_datasets()
