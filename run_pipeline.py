"""
Master Execution Pipeline - Bluestock Mutual Fund Analytics
=============================================================
Executes the end-to-end data pipeline from raw dataset verification to
ETL cleaning, SQLite star schema ingestion, SQL analytics, advanced metrics,
and deliverable artifact generation.

Usage:
  python run_pipeline.py
"""

import os
import sys
import logging
import sqlite3
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add SOURCE CODE/scripts to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'SOURCE CODE', 'scripts')
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def step_1_data_ingestion():
    """Stage 1: Verify raw data availability."""
    logging.info("[STAGE 1/6] Verifying Raw Datasets...")
    from data_ingestion import verify_raw_datasets
    verify_raw_datasets()
    logging.info("✔ Stage 1 Complete: All raw datasets verified.")

def step_2_data_cleaning():
    """Stage 2: Clean NAV history, transactions, and scheme performance data."""
    logging.info("[STAGE 2/6] Executing ETL Data Cleaning...")
    from clean_nav import process_nav
    from clean_transactions import process_transactions
    from clean_performance import process_performance

    process_nav()
    process_transactions()
    process_performance()
    logging.info("✔ Stage 2 Complete: Cleaned CSVs generated in DATASETS/processed/")

def step_3_database_loading():
    """Stage 3: Load cleaned datasets into SQLite Star Schema."""
    logging.info("[STAGE 3/6] Building SQLite Star Schema Database...")
    from load_to_sqlite import load_data
    load_data()
    logging.info("✔ Stage 3 Complete: Database 'mutual_fund_analysis.db' fully populated.")

def step_4_analytical_queries():
    """Stage 4: Execute Analytical Business Intelligence SQL queries."""
    logging.info("[STAGE 4/6] Running Business Intelligence SQL Queries...")
    from run_queries import run_analytical_queries
    run_analytical_queries()
    logging.info("✔ Stage 4 Complete: Report saved to SOURCE CODE/reports/query_results.md")

def step_5_advanced_analytics():
    """Stage 5: Execute 8-Task Advanced Financial & Behavioral Analytics."""
    logging.info("[STAGE 5/6] Executing Advanced Portfolio Analytics...")
    from run_advanced_analytics import (
        calculate_historical_var_cvar,
        calculate_rolling_sharpe,
        analyze_investor_cohorts_yearly,
        analyze_sip_continuity_qualifying,
        calculate_sector_hhi,
        generate_5_advanced_insights,
        validate_analytics_final
    )

    var_df = calculate_historical_var_cvar()
    sharpe_df = calculate_rolling_sharpe()
    cohort_df = analyze_investor_cohorts_yearly()
    sip_df, sip_kpi = analyze_sip_continuity_qualifying()
    hhi_df = calculate_sector_hhi()
    insights = generate_5_advanced_insights()
    val_report = validate_analytics_final()

    logging.info(f"  - Historical VaR/CVaR computed for {len(var_df)} schemes.")
    logging.info(f"  - Rolling Sharpe evaluated for {len(sharpe_df)} schemes.")
    logging.info(f"  - Investor cohorts analyzed: {len(cohort_df)} cohort years.")
    logging.info(f"  - SIP Continuity Rate: {sip_kpi['sip_continuity_rate_pct']}% ({sip_kpi['consistent_investors_count']} consistent / {sip_kpi['qualifying_investors_count']} qualifying).")
    logging.info(f"  - Sector HHI calculated for {len(hhi_df) if hhi_df is not None else 0} equity schemes.")
    logging.info("✔ Stage 5 Complete: All advanced analytics executed successfully.")

def step_6_generate_artifacts():
    """Stage 6: Export deliverables (var_cvar_report.csv, rolling_sharpe_chart.png, etc)."""
    logging.info("[STAGE 6/6] Exporting Final Deliverable Artifacts...")
    db_path = os.path.join(BASE_DIR, 'mutual_fund_analysis.db')
    conn = sqlite3.connect(db_path)

    # 1. Export var_cvar_report.csv
    from run_advanced_analytics import calculate_historical_var_cvar
    var_df = calculate_historical_var_cvar()
    csv_path = os.path.join(BASE_DIR, 'var_cvar_report.csv')
    var_df.to_csv(csv_path, index=False)
    logging.info(f"  - Generated {csv_path}")

    # 2. Export rolling_sharpe_chart.png
    nav_df = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav", conn)
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    nav_df = nav_df.sort_values(['amfi_code', 'date'])
    nav_df['daily_return'] = nav_df.groupby('amfi_code')['nav'].pct_change() * 100

    window = 90
    rolling_ts_dict = {}
    for amfi_code, group in nav_df.groupby('amfi_code'):
        group = group.sort_values('date')
        rets = group['daily_return']
        r_mean = rets.rolling(window).mean()
        r_std = rets.rolling(window).std()
        r_sharpe = (r_mean / r_std) * np.sqrt(252)
        group['rolling_sharpe'] = r_sharpe
        rolling_ts_dict[amfi_code] = group[['date', 'rolling_sharpe']].dropna()

    sample_schemes = [
        (120507, 'ICICI Pru Liquid Fund (Liquid Debt)'),
        (119598, 'SBI Small Cap Fund (Small Cap)'),
        (100033, 'HDFC Mid-Cap Opportunities (Mid Cap)'),
        (120843, 'Kotak Flexicap Fund (Flexi Cap)'),
        (148567, 'Mirae Asset Large Cap Fund (Large Cap)')
    ]

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    for amfi_code, label in sample_schemes:
        if amfi_code in rolling_ts_dict:
            ts = rolling_ts_dict[amfi_code]
            ax.plot(ts['date'], ts['rolling_sharpe'], label=label, linewidth=1.8)

    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.7)
    ax.set_title("Rolling 90-Day Sharpe Ratio Time-Series (5 Key Funds)", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Rolling 90-Day Sharpe Ratio (Annualized)", fontsize=11)
    ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()

    chart_path = os.path.join(BASE_DIR, 'rolling_sharpe_chart.png')
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    logging.info(f"  - Generated {chart_path}")

    # Copy chart to SOURCE CODE/reports/images/
    report_img_dir = os.path.join(BASE_DIR, 'SOURCE CODE', 'reports', 'images')
    os.makedirs(report_img_dir, exist_ok=True)
    shutil.copyfile(chart_path, os.path.join(report_img_dir, 'rolling_sharpe_chart.png'))

    # 3. Ensure Advanced_Analytics.ipynb is in root
    nb_src = os.path.join(BASE_DIR, 'SOURCE CODE', 'notebooks', '03_advanced_analytics.ipynb')
    nb_dst = os.path.join(BASE_DIR, 'Advanced_Analytics.ipynb')
    if os.path.exists(nb_src):
        shutil.copyfile(nb_src, nb_dst)
        logging.info(f"  - Synced {nb_dst}")

    conn.close()
    logging.info("✔ Stage 6 Complete: All deliverable artifacts exported successfully.")

def run_master_pipeline():
    """Execute all pipeline steps in sequence."""
    print("=" * 65)
    print(" BLUESTOCK MUTUAL FUND ANALYTICS - MASTER PIPELINE EXECUTION ")
    print("=" * 65)
    
    try:
        step_1_data_ingestion()
        step_2_data_cleaning()
        step_3_database_loading()
        step_4_analytical_queries()
        step_5_advanced_analytics()
        step_6_generate_artifacts()
        
        print("\n" + "=" * 65)
        print(" SUCCESS: END-TO-END PIPELINE COMPLETED WITH ZERO ERRORS!")
        print("=" * 65)
        return 0
    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}", exc_info=True)
        print("\n" + "=" * 65)
        print(f" FAILURE: PIPELINE TERMINATED WITH ERROR: {e}")
        print("=" * 65)
        return 1

if __name__ == '__main__':
    sys.exit(run_master_pipeline())
