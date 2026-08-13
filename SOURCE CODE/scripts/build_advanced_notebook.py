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

    # Save notebook
    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Notebook successfully written to {NOTEBOOK_PATH}")

if __name__ == '__main__':
    build_notebook()
