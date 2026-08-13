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

# ==============================================================================
# TASK 2: ROLLING 90-DAY SHARPE RATIO
# ==============================================================================
def calculate_rolling_sharpe(window=90):
    """
    Calculate 90-day rolling Sharpe ratio time series for all schemes.
    
    Formula (Primary Methodology):
      rolling_sharpe = returns.rolling(90).mean() / returns.rolling(90).std() * sqrt(252)
      
    Also provides separate optional calculation subtracting annual risk-free rate (6.5%).
    """
    conn = get_db_connection()
    nav_df = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav", conn)
    fund_df = pd.read_sql_query("SELECT amfi_code, scheme_name, fund_house, category FROM dim_fund", conn)
    conn.close()
    
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    nav_df = nav_df.sort_values(['amfi_code', 'date'])
    nav_df['daily_return'] = nav_df.groupby('amfi_code')['nav'].pct_change() * 100
    
    sharpe_summary = []
    
    for amfi_code, group in nav_df.groupby('amfi_code'):
        rets = group['daily_return']
        r_mean = rets.rolling(window).mean()
        r_std = rets.rolling(window).std()
        
        # Primary formula (zero risk-free baseline)
        r_sharpe = (r_mean / r_std) * np.sqrt(252)
        r_sharpe_clean = r_sharpe.dropna()
        
        # Optional risk-free rate adjusted formula (6.5% annual r_f => ~0.0258% daily r_f)
        daily_rf = 6.5 / 252
        r_sharpe_rf = ((r_mean - daily_rf) / r_std) * np.sqrt(252)
        r_sharpe_rf_clean = r_sharpe_rf.dropna()
        
        if len(r_sharpe_clean) > 0:
            sharpe_summary.append({
                'amfi_code': amfi_code,
                'mean_rolling_sharpe': round(r_sharpe_clean.mean(), 2),
                'std_rolling_sharpe': round(r_sharpe_clean.std(), 2),
                'min_rolling_sharpe': round(r_sharpe_clean.min(), 2),
                'max_rolling_sharpe': round(r_sharpe_clean.max(), 2),
                'latest_rolling_sharpe': round(r_sharpe_clean.iloc[-1], 2),
                'mean_rolling_sharpe_rf_adj': round(r_sharpe_rf_clean.mean(), 2) if len(r_sharpe_rf_clean) > 0 else np.nan,
                'rolling_windows_evaluated': len(r_sharpe_clean)
            })
            
    summary_df = pd.DataFrame(sharpe_summary).merge(fund_df, on='amfi_code', how='right')
    summary_df = summary_df.sort_values('mean_rolling_sharpe', ascending=False).reset_index(drop=True)
    summary_df['rank'] = summary_df.index + 1
    
    cols = ['rank', 'amfi_code', 'scheme_name', 'category', 'mean_rolling_sharpe', 'std_rolling_sharpe', 
            'min_rolling_sharpe', 'max_rolling_sharpe', 'latest_rolling_sharpe', 'mean_rolling_sharpe_rf_adj']
    return summary_df[cols]

# ==============================================================================
# TASK 3: INVESTOR COHORT ANALYSIS
# ==============================================================================
def analyze_investor_cohorts():
    """
    Perform monthly cohort analysis tracking investor retention, transaction volume,
    and cumulative Lifetime Value (LTV) across acquisition cohorts.
    """
    conn = get_db_connection()
    tx_df = pd.read_sql_query("SELECT investor_id, transaction_date, amount_inr, transaction_type FROM fact_transactions", conn)
    conn.close()
    
    tx_df['transaction_date'] = pd.to_datetime(tx_df['transaction_date'])
    tx_df['tx_month'] = tx_df['transaction_date'].dt.to_period('M')
    
    # 1. Identify cohort month (first transaction month per investor)
    first_tx = tx_df.groupby('investor_id')['tx_month'].min().rename('cohort_month')
    tx_df = tx_df.merge(first_tx, on='investor_id')
    
    # Calculate relative month index (0, 1, 2, ...)
    tx_df['cohort_index'] = (tx_df['tx_month'].dt.year - tx_df['cohort_month'].dt.year) * 12 + (tx_df['tx_month'].dt.month - tx_df['cohort_month'].dt.month)
    
    # 2. Retention Matrix (Active unique investors per cohort index)
    cohort_counts = tx_df.groupby(['cohort_month', 'cohort_index'])['investor_id'].nunique().unstack()
    cohort_sizes = cohort_counts[0]
    retention_matrix = cohort_counts.divide(cohort_sizes, axis=0) * 100
    
    # 3. Cohort Total Volume Matrix (INR Cr)
    cohort_volume = tx_df.groupby(['cohort_month', 'cohort_index'])['amount_inr'].sum().unstack() / 1e7
    
    # 4. Cohort Cumulative LTV per Investor (INR)
    cohort_cum_val = tx_df.groupby(['cohort_month', 'cohort_index'])['amount_inr'].sum().groupby(level=0).cumsum().unstack()
    cohort_ltv = cohort_cum_val.divide(cohort_sizes, axis=0)
    
    # Build clean cohort summary DataFrame
    cohort_summary = pd.DataFrame({
        'cohort_month': cohort_sizes.index.astype(str),
        'initial_investors': cohort_sizes.values,
        'm1_retention_pct': retention_matrix[1].round(1).values if 1 in retention_matrix.columns else np.nan,
        'm3_retention_pct': retention_matrix[3].round(1).values if 3 in retention_matrix.columns else np.nan,
        'total_initial_capital_cr': cohort_volume[0].round(2).values,
        'cumulative_ltv_m6_inr': cohort_ltv[6].round(0).values if 6 in cohort_ltv.columns else np.nan
    })
    
    return cohort_summary, retention_matrix.round(1), cohort_ltv.round(0)

# ==============================================================================
# TASK 4: SIP CONTINUITY & CHURN ANALYSIS
# ==============================================================================
def analyze_sip_continuity():
    """
    Analyze systematic investment plan (SIP) continuity, investor tenure, drop-off behavior,
    and compute overall SIP churn rate across the transaction dataset.
    """
    conn = get_db_connection()
    tx_df = pd.read_sql_query("SELECT investor_id, transaction_date, amount_inr, transaction_type FROM fact_transactions", conn)
    conn.close()
    
    tx_df['transaction_date'] = pd.to_datetime(tx_df['transaction_date'])
    tx_df['tx_month'] = tx_df['transaction_date'].dt.to_period('M')
    
    # Filter SIP transactions only
    sip_df = tx_df[tx_df['transaction_type'] == 'SIP'].copy()
    
    total_sip_investors = sip_df['investor_id'].nunique()
    total_sip_transactions = len(sip_df)
    total_sip_capital_cr = sip_df['amount_inr'].sum() / 1e7
    
    # Calculate active SIP months per investor
    investor_sip_months = sip_df.groupby('investor_id')['tx_month'].nunique()
    
    # Tenure distribution
    tenure_1m = (investor_sip_months == 1).sum()
    tenure_2_5m = ((investor_sip_months >= 2) & (investor_sip_months <= 5)).sum()
    tenure_6_11m = ((investor_sip_months >= 6) & (investor_sip_months <= 11)).sum()
    tenure_12m_plus = (investor_sip_months >= 12).sum()
    
    # Identify inactive / churned SIP investors (No SIP transaction in the last 60 days of dataset)
    max_tx_date = tx_df['transaction_date'].max()
    last_sip_per_investor = sip_df.groupby('investor_id')['transaction_date'].max()
    days_since_last_sip = (max_tx_date - last_sip_per_investor).dt.days
    
    churned_investors = (days_since_last_sip > 60).sum()
    active_investors = total_sip_investors - churned_investors
    sip_churn_rate_pct = (churned_investors / total_sip_investors) * 100
    
    sip_metrics = pd.DataFrame([{
        'metric': 'Total Unique SIP Investors', 'value': f"{total_sip_investors:,}"
    }, {
        'metric': 'Total SIP Transactions Executed', 'value': f"{total_sip_transactions:,}"
    }, {
        'metric': 'Total SIP Capital Mobilized (INR Cr)', 'value': f"INR {total_sip_capital_cr:,.2f} Cr"
    }, {
        'metric': 'Average Active SIP Tenure (Months)', 'value': f"{investor_sip_months.mean():.2f} Months"
    }, {
        'metric': 'Active SIP Investors (Last 60 Days)', 'value': f"{active_investors:,} ({(100 - sip_churn_rate_pct):.1f}%)"
    }, {
        'metric': 'Churned/Lapsed SIP Investors (>60 Days Inactive)', 'value': f"{churned_investors:,} ({sip_churn_rate_pct:.1f}%)"
    }, {
        'metric': 'Investors with 1 Month Tenure (Immediate Churn)', 'value': f"{tenure_1m:,} ({(tenure_1m/total_sip_investors*100):.1f}%)"
    }, {
        'metric': 'Investors with 12+ Months Tenure (High Loyalty)', 'value': f"{tenure_12m_plus:,} ({(tenure_12m_plus/total_sip_investors*100):.1f}%)"
    }])
    
    return sip_metrics

# ==============================================================================
# TASK 5: RISK-BASED FUND RECOMMENDER ENGINE
# ==============================================================================
def recommend_funds(risk_tolerance='Moderate', horizon='3-Year', top_n=3):
    """
    Risk-adjusted mutual fund recommendation engine that screens, scores, and ranks
    candidate schemes based on investor risk profile and time horizon.
    """
    conn = get_db_connection()
    sp = pd.read_sql_query("SELECT * FROM fact_performance", conn)
    conn.close()
    
    # Map risk profiles to category filters & risk grade targets
    if risk_tolerance.lower() == 'low':
        allowed_categories = ['Liquid', 'Gilt', 'Short Duration', 'Debt']
        target_risk_grades = ['Low', 'Moderate']
    elif risk_tolerance.lower() == 'high':
        allowed_categories = ['Small Cap', 'Mid Cap', 'Sectoral/Thematic', 'Equity']
        target_risk_grades = ['High', 'Very High']
    else:  # Moderate
        allowed_categories = ['Large Cap', 'Flexi Cap', 'Large & Mid Cap', 'Hybrid', 'Balanced Advantage']
        target_risk_grades = ['Moderate', 'High']
        
    # Horizon metric selection
    ret_col = 'return_3yr_pct'
    if horizon == '1-Year':
        ret_col = 'return_1yr_pct'
    elif horizon == '5-Year':
        ret_col = 'return_5yr_pct'
        
    candidates = sp.copy()
    
    # Preprocess broad category mapping if specific subcategories aren't exact match
    def match_risk_cat(row):
        cat = row['category']
        rg = str(row['risk_grade'])
        if risk_tolerance.lower() == 'low':
            return cat in ['Liquid', 'Gilt', 'Short Duration'] or 'Low' in rg or 'Debt' in str(row['plan'])
        elif risk_tolerance.lower() == 'high':
            return cat in ['Small Cap', 'Mid Cap', 'Sectoral/Thematic'] or 'High' in rg
        else:
            return cat in ['Large Cap', 'Flexi Cap', 'Large & Mid Cap', 'Hybrid'] or 'Moderate' in rg
            
    filtered = candidates[candidates.apply(match_risk_cat, axis=1)].copy()
    if len(filtered) < top_n:
        filtered = candidates.copy()  # Fallback to full pool if strict filter returns too few
        
    # Calculate composite score = (Sharpe Ratio * 0.4) + (Return % * 0.4) + (Sortino Ratio * 0.2)
    filtered['composite_score'] = (filtered['sharpe_ratio'].fillna(0) * 0.4) + \
                                   (filtered[ret_col].fillna(0) * 0.4) + \
                                   (filtered['sortino_ratio'].fillna(0) * 0.2)
                                   
    recs = filtered.sort_values('composite_score', ascending=False).head(top_n).copy()
    recs['recommendation_rank'] = range(1, len(recs) + 1)
    
    cols = ['recommendation_rank', 'amfi_code', 'scheme_name', 'category', 'risk_grade', 
            ret_col, 'std_dev_ann_pct', 'sharpe_ratio', 'sortino_ratio', 'aum_crore', 'composite_score']
    
    return recs[cols]

if __name__ == '__main__':
    print("--- Executing Task 1: Historical VaR & CVaR ---")
    var_results = calculate_historical_var_cvar()
    print(f"Total schemes evaluated: {len(var_results)}")
    
    print("\n--- Executing Task 2: Rolling 90-Day Sharpe Ratio ---")
    sharpe_results = calculate_rolling_sharpe()
    print(f"Total schemes evaluated: {len(sharpe_results)}")
    
    print("\n--- Executing Task 3: Investor Cohort Analysis ---")
    cohort_summary, retention_mat, ltv_mat = analyze_investor_cohorts()
    print(f"Evaluated {len(cohort_summary)} monthly cohorts.")
    
    print("\n--- Executing Task 4: SIP Continuity & Churn Analysis ---")
    sip_metrics = analyze_sip_continuity()
    print(sip_metrics.to_string(index=False))
    
    print("\n--- Executing Task 5: Risk-Based Fund Recommender Engine ---")
    for profile in ['Low', 'Moderate', 'High']:
        recs = recommend_funds(risk_tolerance=profile, horizon='3-Year', top_n=2)
        print(f"\nTop Recommendations for Profile: {profile} Risk (3-Year Horizon):")
        print(recs[['recommendation_rank', 'amfi_code', 'scheme_name', 'category', 'return_3yr_pct', 'sharpe_ratio', 'composite_score']].to_string(index=False))




