"""
Script to build 03_advanced_analytics.ipynb programmatically using nbformat.
"""

import os
import nbformat as nbf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTEBOOK_PATH = os.path.join(BASE_DIR, 'SOURCE CODE', 'notebooks', '03_advanced_analytics.ipynb')

def build_notebook():
    nb = nbf.v4.new_notebook()
    nb.cells = []
    
    # Title
    nb.cells.append(nbf.v4.new_markdown_cell("""# Bluestock Mutual Fund - Advanced Portfolio Analytics

**Project Phase:** Advanced Portfolio & Investor Behavioral Analytics  
**Database Source:** `mutual_fund_analysis.db` (SQLite Star Schema)  
**Scope:** Historical Risk (VaR/CVaR), Rolling Performance (Sharpe), Investor Cohort LTV/Retention, SIP Continuity & Churn, Risk-Adjusted Fund Recommendation Engine, and Sector Concentration (HHI).

---

## 1. Project Setup
Initialize environment, connect to SQLite database, and load core analytical modules.
"""))
    
    nb.cells.append(nbf.v4.new_code_cell("""import sqlite3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visual styling
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 120

# Database path
DB_PATH = '../../mutual_fund_analysis.db'
RAW_DATA_DIR = '../../DATASETS/raw'

print(f"Connected to database at: {DB_PATH}")
"""))
    
    # Section 2: Load Data
    nb.cells.append(nbf.v4.new_markdown_cell("""## 2. Load Data
Retrieve star schema tables (`dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`) from the SQLite database.
"""))
    
    nb.cells.append(nbf.v4.new_code_cell("""conn = sqlite3.connect(DB_PATH)

dim_fund = pd.read_sql_query("SELECT * FROM dim_fund", conn)
dim_date = pd.read_sql_query("SELECT * FROM dim_date", conn)
fact_nav = pd.read_sql_query("SELECT * FROM fact_nav", conn)
fact_transactions = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
fact_performance = pd.read_sql_query("SELECT * FROM fact_performance", conn)
fact_aum = pd.read_sql_query("SELECT * FROM fact_aum", conn)

conn.close()

print(f"Loaded {len(dim_fund)} funds, {len(fact_nav)} NAV records, and {len(fact_transactions)} transaction records.")
"""))

    # Section 3: Data Preparation
    nb.cells.append(nbf.v4.new_markdown_cell("""## 3. Data Preparation
Format dates, verify data integrity across all 40 schemes, and calculate daily NAV percentage returns.
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# Preprocess NAV dates & sort
fact_nav['date'] = pd.to_datetime(fact_nav['date'])
fact_nav = fact_nav.sort_values(['amfi_code', 'date'])

# Calculate daily return per scheme
fact_nav['daily_return'] = fact_nav.groupby('amfi_code')['nav'].pct_change() * 100

# Preprocess transactions
fact_transactions['transaction_date'] = pd.to_datetime(fact_transactions['transaction_date'])

print(f"Data prep complete. Evaluated date range: {fact_nav['date'].min().strftime('%Y-%m-%d')} to {fact_nav['date'].max().strftime('%Y-%m-%d')}")
"""))

    # Section 4: Task 1 - Historical VaR & CVaR
    nb.cells.append(nbf.v4.new_markdown_cell("""## 4. Historical VaR & CVaR (95% Confidence)

### Financial Methodology & Interpretation:
1. **Historical Value at Risk (VaR 95%)**: Measures the maximum expected loss over a 1-day holding period at a 95% confidence level ($5^{\\text{th}}$ percentile of daily returns).
   - *Interpretation of Negative VaR*: A 95% VaR of **-1.85%** means that 95% of trading days experienced daily returns better than -1.85%, while on 5% of trading days (worst-case tail), losses equaled or exceeded 1.85%.
2. **Conditional Value at Risk (CVaR 95% / Expected Shortfall)**: Quantifies tail risk by taking the average of all daily returns that fall at or below the 95% VaR threshold.
   - *Interpretation of Negative CVaR*: A 95% CVaR of **-2.45%** represents the expected average daily loss on extreme market downturn days.
3. **Downside Risk Ranking**: Schemes are ordered from **highest downside risk** (most negative VaR/CVaR values, typical of Small Cap equity funds) to **lowest downside risk** (least negative values, typical of Liquid/Gilt funds).
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# Calculate 95% VaR & CVaR for all schemes
var_results = []
alpha_95 = 5.0  # 5th percentile for 95% confidence

for amfi_code, group in fact_nav.groupby('amfi_code'):
    rets = group['daily_return'].dropna()
    if len(rets) > 0:
        var_95 = np.percentile(rets, alpha_95)
        cvar_95 = rets[rets <= var_95].mean()
        var_results.append({
            'amfi_code': amfi_code,
            'var_95_pct': round(var_95, 2),
            'cvar_95_pct': round(cvar_95, 2),
            'total_trading_days': len(rets)
        })

var_df = pd.DataFrame(var_results)

# Merge metadata from dim_fund
var_df = var_df.merge(dim_fund[['amfi_code', 'scheme_name', 'fund_house', 'category']], on='amfi_code', how='right')

# Rank from highest downside risk (most negative VaR) to lowest downside risk
var_df = var_df.sort_values('var_95_pct', ascending=True).reset_index(drop=True)
var_df['downside_risk_rank'] = var_df.index + 1

# Select final clean columns
var_summary_table = var_df[['downside_risk_rank', 'amfi_code', 'scheme_name', 'fund_house', 'category', 'var_95_pct', 'cvar_95_pct', 'total_trading_days']]

# Validation check
print(f"Coverage Validation: {len(var_summary_table)} / 40 schemes evaluated. Missing data count: {var_summary_table['var_95_pct'].isna().sum()}")

# Display top 10 highest downside risk schemes
var_summary_table.head(10)
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# Display top 5 safest (lowest downside risk) schemes
var_summary_table.tail(5)
"""))

    # Section 5: Task 2 - Rolling 90-Day Sharpe
    nb.cells.append(nbf.v4.new_markdown_cell("""## 5. Rolling 90-Day Sharpe Ratio

### Methodology:
1. **Primary Rolling Sharpe Formula**:
   $$\\text{Rolling Sharpe} = \\frac{\\text{returns.rolling(90).mean()}}{\\text{returns.rolling(90).std()}} \\times \\sqrt{252}$$
   - *Note*: Per project specification, the primary calculation evaluates return-to-volatility ratio directly without subtracting risk-free rate.
2. **Optional Risk-Free Rate Adjusted Formula** (Shown separately for comparison):
   $$\\text{Rolling Sharpe}_{rf} = \\frac{\\text{returns.rolling(90).mean()} - r_{f,\\text{daily}}}{\\text{returns.rolling(90).std()}} \\times \\sqrt{252}$$
   - Where $r_{f,\\text{annual}} = 6.5\\% \\implies r_{f,\\text{daily}} = \\frac{6.5\\%}{252} \\approx 0.0258\\%$.
3. **Consistency & Stability Metrics**: Evaluates `mean`, `std`, `min`, `max`, and `latest` rolling 90-day Sharpe ratios to separate consistently performing funds from volatile/unstable funds.
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# Calculate 90-day rolling Sharpe metrics per scheme
window = 90
sharpe_results = []

for amfi_code, group in fact_nav.groupby('amfi_code'):
    rets = group['daily_return']
    r_mean = rets.rolling(window).mean()
    r_std = rets.rolling(window).std()
    
    # Primary formula
    r_sharpe = (r_mean / r_std) * np.sqrt(252)
    r_sharpe_clean = r_sharpe.dropna()
    
    # Optional RF adjusted formula
    daily_rf = 6.5 / 252
    r_sharpe_rf = ((r_mean - daily_rf) / r_std) * np.sqrt(252)
    r_sharpe_rf_clean = r_sharpe_rf.dropna()
    
    if len(r_sharpe_clean) > 0:
        sharpe_results.append({
            'amfi_code': amfi_code,
            'mean_rolling_sharpe': round(r_sharpe_clean.mean(), 2),
            'std_rolling_sharpe': round(r_sharpe_clean.std(), 2),
            'min_rolling_sharpe': round(r_sharpe_clean.min(), 2),
            'max_rolling_sharpe': round(r_sharpe_clean.max(), 2),
            'latest_rolling_sharpe': round(r_sharpe_clean.iloc[-1], 2),
            'mean_rolling_sharpe_rf_adj': round(r_sharpe_rf_clean.mean(), 2) if len(r_sharpe_rf_clean) > 0 else np.nan,
            'rolling_windows_evaluated': len(r_sharpe_clean)
        })

sharpe_summary_table = pd.DataFrame(sharpe_results).merge(dim_fund[['amfi_code', 'scheme_name', 'category']], on='amfi_code', how='right')
sharpe_summary_table = sharpe_summary_table.sort_values('mean_rolling_sharpe', ascending=False).reset_index(drop=True)
sharpe_summary_table['rank'] = sharpe_summary_table.index + 1

cols = ['rank', 'amfi_code', 'scheme_name', 'category', 'mean_rolling_sharpe', 'std_rolling_sharpe', 'min_rolling_sharpe', 'max_rolling_sharpe', 'latest_rolling_sharpe', 'mean_rolling_sharpe_rf_adj']
sharpe_summary_table = sharpe_summary_table[cols]

# Display Top 10 Funds by Mean 90-Day Rolling Sharpe Ratio
sharpe_summary_table.head(10)
"""))

    # Section 6: Task 3 - Investor Cohort Analysis
    nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Investor Cohort Analysis

### Business Methodology:
1. **Acquisition Cohort Definition**: Group investors by the calendar month of their first transaction (`cohort_month`).
2. **Cohort Index**: Calculate relative period indices ($0, 1, 2, \\dots, 16$) measuring elapsed months since acquisition.
3. **Retention Rate (%)**: Active unique investors in Month $N$ divided by initial cohort size in Month 0.
4. **Cumulative Investor LTV (INR)**: Cumulative transaction value generated by the cohort divided by initial investor count.
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# 1. Map cohort month and index
tx_prep = fact_transactions.copy()
tx_prep['tx_month'] = tx_prep['transaction_date'].dt.to_period('M')

first_tx = tx_prep.groupby('investor_id')['tx_month'].min().rename('cohort_month')
tx_prep = tx_prep.merge(first_tx, on='investor_id')

tx_prep['cohort_index'] = (tx_prep['tx_month'].dt.year - tx_prep['cohort_month'].dt.year) * 12 + (tx_prep['tx_month'].dt.month - tx_prep['cohort_month'].dt.month)

# 2. Build Retention Matrix (%)
cohort_counts = tx_prep.groupby(['cohort_month', 'cohort_index'])['investor_id'].nunique().unstack()
cohort_sizes = cohort_counts[0]
retention_matrix = cohort_counts.divide(cohort_sizes, axis=0) * 100

# 3. Build Cumulative LTV Matrix (INR per Investor)
cohort_cum_val = tx_prep.groupby(['cohort_month', 'cohort_index'])['amount_inr'].sum().groupby(level=0).cumsum().unstack()
cohort_ltv_matrix = cohort_cum_val.divide(cohort_sizes, axis=0)

# Build Clean Cohort Summary Table
cohort_summary_table = pd.DataFrame({
    'cohort_month': cohort_sizes.index.astype(str),
    'initial_investors': cohort_sizes.values,
    'm1_retention_pct': retention_matrix[1].round(1).values if 1 in retention_matrix.columns else np.nan,
    'm3_retention_pct': retention_matrix[3].round(1).values if 3 in retention_matrix.columns else np.nan,
    'm6_retention_pct': retention_matrix[6].round(1).values if 6 in retention_matrix.columns else np.nan,
    'cumulative_ltv_m6_inr': cohort_ltv_matrix[6].round(0).values if 6 in cohort_ltv_matrix.columns else np.nan
})

# Display Cohort Summary Table
cohort_summary_table
"""))

    # Section 7: Task 4 - SIP Continuity Analysis
    nb.cells.append(nbf.v4.new_markdown_cell("""## 7. SIP Continuity & Churn Analysis

### Methodology & Business Metrics:
1. **SIP Filtering**: Standardize `transaction_type == 'SIP'` records across 32,778 transaction logs.
2. **SIP Active Tenure**: Unique calendar months of active SIP deposits per investor.
3. **SIP Churn Condition**: Investors whose last SIP installment occurred > 60 days prior to the maximum dataset date (`2025-05-31`).
4. **Tenure Segmentation**: Categorized into `1 Month` (Immediate Churn), `2-5 Months`, `6-11 Months`, and `12+ Months` (Loyal Investors).
"""))

    nb.cells.append(nbf.v4.new_code_cell("""# Execute SIP Continuity & Churn Analytics
sip_txs = fact_transactions[fact_transactions['transaction_type'] == 'SIP'].copy()
sip_txs['tx_month'] = sip_txs['transaction_date'].dt.to_period('M')

total_sip_users = sip_txs['investor_id'].nunique()
total_sip_txs = len(sip_txs)
total_sip_val = sip_txs['amount_inr'].sum() / 1e7

investor_tenure_months = sip_txs.groupby('investor_id')['tx_month'].nunique()

max_dataset_date = fact_transactions['transaction_date'].max()
last_sip_date = sip_txs.groupby('investor_id')['transaction_date'].max()
lapsed_days = (max_dataset_date - last_sip_date).dt.days

churned_users = (lapsed_days > 60).sum()
churn_rate = (churned_users / total_sip_users) * 100

sip_kpi_summary = pd.DataFrame([
    {'Metric': 'Total Unique SIP Investors', 'Value': f"{total_sip_users:,}"},
    {'Metric': 'Total SIP Transactions Executed', 'Value': f"{total_sip_txs:,}"},
    {'Metric': 'Total SIP Capital Mobilized', 'Value': f"₹{total_sip_val:,.2f} Cr"},
    {'Metric': 'Average SIP Tenure per Investor', 'Value': f"{investor_tenure_months.mean():.2f} Months"},
    {'Metric': 'Active SIP Investors (Last 60 Days)', 'Value': f"{(total_sip_users - churned_users):,} ({(100 - churn_rate):.1f}%)"},
    {'Metric': 'Churned SIP Investors (>60 Days Inactive)', 'Value': f"{churned_users:,} ({churn_rate:.1f}%)"},
    {'Metric': '1-Month Immediate Churn Count', 'Value': f"{(investor_tenure_months == 1).sum():,} ({(investor_tenure_months == 1).sum()/total_sip_users*100:.1f}%)"},
    {'Metric': '12+ Month Loyal SIP Investors', 'Value': f"{(investor_tenure_months >= 12).sum():,} ({(investor_tenure_months >= 12).sum()/total_sip_users*100:.1f}%)"}
])

sip_kpi_summary
"""))

    # Save notebook
    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Notebook successfully written to {NOTEBOOK_PATH}")

if __name__ == '__main__':
    build_notebook()
