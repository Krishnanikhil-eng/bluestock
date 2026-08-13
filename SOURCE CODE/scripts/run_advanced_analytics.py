"""
Advanced Analytics Module for Bluestock Mutual Fund Project
============================================================
This script executes the 8 Advanced Analytics tasks cleanly using the SQLite Star Schema database
(mutual_fund_analysis.db) and existing cleaned CSV datasets.

Tasks:
1. Historical VaR & CVaR (95% Confidence)
2. Rolling 90-Day Sharpe Ratio
3. Investor Cohort Analysis
4. SIP Continuity & Churn Analysis
5. Risk-Adjusted Fund Recommender
6. Sector HHI Concentration Analysis
7. Advanced Insights & Executive Summary
8. Final Quality Validation
"""

import os
import sqlite3
import pandas as pd
import numpy as np

# Set project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'mutual_fund_analysis.db')
RAW_DATA_DIR = os.path.join(BASE_DIR, 'DATASETS', 'raw')
NOTEBOOK_PATH = os.path.join(BASE_DIR, 'SOURCE CODE', 'notebooks', '03_advanced_analytics.ipynb')

def get_db_connection():
    """Connect to SQLite star schema database."""
    return sqlite3.connect(DB_PATH)

# ==============================================================================
# TASK 1: HISTORICAL VaR + CVaR (95% Confidence)
# ==============================================================================
def calculate_historical_var_cvar(confidence_level=0.95):
    """
    Calculate 95% Historical Value at Risk (VaR) and Conditional Value at Risk (CVaR / Expected Shortfall)
    for all 40 mutual fund schemes in the dataset.
    
    Formula:
      - VaR_95 = 5th percentile of daily NAV returns
      - CVaR_95 = Average daily return for observations <= VaR_95
    """
    conn = get_db_connection()
    nav_df = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav", conn)
    fund_df = pd.read_sql_query("SELECT amfi_code, scheme_name, fund_house, category FROM dim_fund", conn)
    conn.close()
    
    # Preprocess date and calculate daily percentage returns per scheme
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    nav_df = nav_df.sort_values(['amfi_code', 'date'])
    nav_df['daily_return'] = nav_df.groupby('amfi_code')['nav'].pct_change() * 100
    
    alpha = (1 - confidence_level) * 100
    results = []
    
    for amfi_code, group in nav_df.groupby('amfi_code'):
        rets = group['daily_return'].dropna()
        if len(rets) > 0:
            var_95 = np.percentile(rets, alpha)
            cvar_95 = rets[rets <= var_95].mean()
            results.append({
                'amfi_code': amfi_code,
                'var_95_pct': round(var_95, 2),
                'cvar_95_pct': round(cvar_95, 2),
                'total_trading_days': len(rets)
            })
            
    var_df = pd.DataFrame(results)
    
    # Merge scheme metadata
    final_df = var_df.merge(fund_df, on='amfi_code', how='right')
    
    # Rank schemes from highest downside risk (most negative VaR) to lowest downside risk
    final_df = final_df.sort_values('var_95_pct', ascending=True).reset_index(drop=True)
    final_df['downside_risk_rank'] = final_df.index + 1
    
    # Rearrange columns
    col_order = ['downside_risk_rank', 'amfi_code', 'scheme_name', 'fund_house', 'category', 'var_95_pct', 'cvar_95_pct', 'total_trading_days']
    final_df = final_df[col_order]
    
    return final_df

if __name__ == '__main__':
    print("--- Executing Task 1: Historical VaR & CVaR ---")
    var_results = calculate_historical_var_cvar()
    print(f"Total schemes evaluated: {len(var_results)}")
    print("\nTop 5 Highest Downside Risk Schemes (Worst VaR 95%):")
    print(var_results.head(5).to_string(index=False))
    print("\nTop 5 Safest Downside Risk Schemes (Lowest VaR 95%):")
    print(var_results.tail(5).to_string(index=False))
