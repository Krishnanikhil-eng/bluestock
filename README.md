# Bluestock Mutual Fund Analytics

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Database SQLite3](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://sqlite.org/)
[![PowerBI Compatible](https://img.shields.io/badge/PowerBI-Desktop%20Report-yellow.svg)](https://powerbi.microsoft.com/)
[![License MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 1. Project Overview
**Bluestock Mutual Fund Analytics** is an end-to-end data engineering, quantitative finance, and business intelligence capstone project developed for Bluestock Fintech. The system ingests raw mutual fund market data, cleans transaction histories and daily Net Asset Values (NAVs), architectures a production-ready SQLite Star Schema database, performs analytical SQL queries, executes advanced quantitative risk analytics (Historical VaR/CVaR, Rolling Sharpe ratios, Sector HHI concentration), models investor behavioral cohorts and SIP continuity rates, and delivers an executive Power BI reporting suite.

---

## 2. Problem Statement
Retail mutual fund investors and financial advisors in the Indian asset management industry face critical analytics gaps:
* **Downside Tail Risk Opacity**: Standard annualized volatility fails to capture non-normal left-tail crash risks in equity schemes.
* **Static Performance Ratios**: Traditional point-in-time Sharpe ratios obscure temporal regime shifts and rolling volatility.
* **Investor Churn & SIP Friction**: AMCs lack automated early-warning flags to detect investors exhibiting systematic payment gaps prior to total SIP default.
* **Portfolio Concentration Blindspots**: High equity returns are frequently driven by unacknowledged single-sector concentration risks.

---

## 3. Project Objectives
* **Modular ETL Pipeline**: Build an automated python pipeline to ingest, validate, and clean raw transaction logs, NAV histories, and performance facts.
* **Relational Star Schema**: Model `mutual_fund_analysis.db` with optimized dimensions (`dim_fund`, `dim_date`) and fact tables (`fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`).
* **Quantitative Risk Analytics**: Compute 95% Historical VaR & CVaR across all 40 schemes and annualized 90-day rolling Sharpe ratios.
* **Behavioral & Cohort Modeling**: Group investors into acquisition cohorts (2024–2025) and calculate SIP continuity rates for investors with $\ge 6$ deposits.
* **Automated Fund Recommender**: Implement a risk-appetite matching algorithm (`recommender.py`) pairing investor profiles with top Sharpe-performing schemes.
* **Executive Visualization Suite**: Design a 4-page Power BI dashboard and generate automated executive PDF reports.

---

## 4. Key Features
* **Automated Master Pipeline**: Single-command execution script (`python run_pipeline.py`) running all stages sequentially with error handling.
* **Vectorized Financial Analytics**: High-performance pandas/numpy implementation of historical VaR/CVaR, rolling Sharpe, and Herfindahl-Hirschman Index (HHI).
* **Automated SQL Reporting**: Parses `analytical_queries.sql` and generates markdown reports (`query_results.md`).
* **Standalone Recommender Engine**: CLI-executable engine accepting `Low`, `Moderate`, or `High` risk appetite inputs.
* **Complete Data Integrity Check**: Automated validation verifying row count parity across raw CSVs, cleaned files, and SQLite tables.

---

## 5. Data Sources
The primary datasets are sourced from historical Indian Mutual Fund market feeds, AMFI (Association of Mutual Funds in India) scheme mappings, and investor ledger logs:
* **AMFI Scheme Master & NAV Logs**: Daily historical NAV records spanning 2022 to 2026.
* **Investor Transaction Records**: Systematic Investment Plan (SIP), Lumpsum, and Redemption logs spanning 2024 to 2025.
* **Scheme Performance & Risk Attributes**: 3-year CAGR, Alpha, Beta, Sharpe Ratio, Sortino Ratio, Max Drawdown, and Expense Ratios.
* **Portfolio Holdings**: Industry sector allocation percentages across portfolio equity stocks.

---

## 6. Dataset Descriptions
* `fact_nav` (**64,320 rows**): Daily NAV entries for 40 mutual fund schemes from **Jan 3, 2022 to May 29, 2026**.
* `fact_transactions` (**32,778 rows**): Investment ledger for **5,000 unique investors** (SIP, Lumpsum, Redemption) from **Jan 1, 2024 to May 30, 2025**.
* `dim_fund` (**40 rows**): Scheme master metadata (AMFI Code, Scheme Name, Category, Sub-Category, Fund House, Launch Date, Benchmark).
* `dim_date` (**1,608 rows**): Date dimension table linking calendar dates, year, quarter, month, day, and weekend flags.
* `fact_performance` (**40 rows**): Comprehensive risk-adjusted performance metrics per fund scheme.
* `fact_aum` (**90 rows**): Historical Asset Under Management (AUM) aggregated by fund house.
* `09_portfolio_holdings.csv` (**329 rows**): Detailed sector breakdowns across 34 equity funds.

---

## 7. Project Architecture

```
                               ┌──────────────────────────┐
                               │   RAW DATASETS (CSVs)    │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │   ETL CLEANING PIPELINE  │
                               │(clean_nav/trans/perf.py) │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │   SQLITE STAR SCHEMA     │
                               │ (mutual_fund_analysis.db)│
                               └──────┬────────────┬──────┘
                                      │            │
             ┌────────────────────────┘            └────────────────────────┐
             ▼                                                              ▼
┌──────────────────────────┐                                  ┌──────────────────────────┐
│  ANALYTICAL SQL ENGINE   │                                  │   ADVANCED ANALYTICS     │
│ (run_queries.py -> MD)   │                                  │ (run_advanced_analytics) │
└──────────────────────────┘                                  └────────────┬─────────────┘
                                                                           │
                                            ┌──────────────────────────────┴──────────────────────────────┐
                                            ▼                                                             ▼
                               ┌──────────────────────────┐                                  ┌──────────────────────────┐
                               │  EXECUTIVE DELIVERABLES  │                                  │    POWER BI DASHBOARD    │
                               │(VaR CSV / Sharpe Plot)   │                                  │(Dashboard.pdf & PNGs)    │
                               └──────────────────────────┘                                  └──────────────────────────┘
```

---

## 8. ETL Pipeline
1. **Data Ingestion (`data_ingestion.py`)**: Checks file presence and byte integrity for raw input CSVs in `DATASETS/raw/`.
2. **Data Cleaning**:
   * `clean_nav.py`: Parses dates, filters invalid $NAV \le 0$, removes duplicate dates per AMFI code, and forward-fills missing weekend/holiday dates.
   * `clean_transactions.py`: Standardizes transaction types (`SIP`, `Lumpsum`, `Redemption`), validates positive INR amounts, normalizes KYC status, and removes duplicate transactions.
   * `clean_performance.py`: Standardizes return metrics, validates expense ratios ($0.1\% - 2.5\%$), checks Morningstar ratings ($1 - 5$), and flags data anomalies.
3. **Database Loading (`load_to_sqlite.py`)**: Creates DDL schema with foreign key constraints, populates dimension/fact tables, and performs strict row count validation.

---

## 9. Database / Star Schema
The database `mutual_fund_analysis.db` implements a dimensional **Star Schema**:
* **Central Fact Tables**:
  * `fact_nav` (`amfi_code` [FK], `date` [FK], `nav`, `daily_return`)
  * `fact_transactions` (`transaction_id` [PK], `investor_id`, `amfi_code` [FK], `transaction_date` [FK], `transaction_type`, `amount_inr`, `units`, `nav`, `city`, `income_group`, `kyc_status`)
  * `fact_performance` (`amfi_code` [PK/FK], `return_1yr_pct`, `return_3yr_pct`, `return_5yr_pct`, `alpha`, `beta`, `sharpe_ratio`, `sortino_ratio`, `std_dev_ann_pct`, `max_drawdown_pct`, `risk_grade`, `aum_crore`)
  * `fact_aum` (`fund_house`, `date` [FK], `aum_crore`)
* **Dimension Tables**:
  * `dim_fund` (`amfi_code` [PK], `fund_house`, `scheme_name`, `category`, `sub_category`, `plan`, `launch_date`, `benchmark`, `min_sip_amount`, `min_lumpsum_amount`, `fund_manager`, `risk_category`)
  * `dim_date` (`date` [PK], `year`, `month`, `day`, `quarter`, `day_of_week`, `is_weekend`)

---

## 10. Exploratory Data Analysis
Key findings from EDA:
* **NAV Trajectory**: Equity schemes experienced strong growth across 2022–2024 with maximum volatility observed in Small Cap funds.
* **SIP Popularity**: Systematic Investment Plans (SIP) account for **60.1% of all transaction occurrences** (19,716 transactions), with an average ticket size of **₹10,999**.
* **Geographic Distribution**: Metro cities (Mumbai, Delhi, Bengaluru) drive **54.2% of total transaction volume**, followed by Tier-2 cities (Pune, Ahmedabad).
* **Investor Demographics**: High Income investors (>₹15L annual income) contribute **65.8% of total lumpsum inflows**.

---

## 11. Performance Analytics
* **Sharpe & Sortino Ratios**: Debt/Liquid funds exhibit exceptionally high Sharpe ratios (up to 7.68) due to negligible daily standard deviation. Among Equity funds, `HDFC Top 100 Fund` (1.06) and `Mirae Asset Large Cap Fund` (1.06) lead risk-adjusted return efficiency.
* **Alpha Generation**: `Nippon India Small Cap Fund` achieved the highest positive 3-year Alpha (+5.12%), significantly outperforming its benchmark index.
* **Maximum Drawdown**: Small Cap schemes exhibited maximum peak-to-trough drawdowns reaching **-24.8%**, compared to Large Cap drawdowns averaging **-12.4%**.

---

## 12. Advanced Analytics
1. **Historical 95% VaR & CVaR**: Calculated 5th percentile return and conditional expected shortfall across all 40 schemes. Highest risk: `ABSL Small Cap Fund` (95% VaR = **-2.39%**, CVaR = **-3.03%**).
2. **Rolling 90-Day Sharpe Ratio**: Dynamic rolling window analysis revealing temporal risk efficiency stability for Debt vs. Equity schemes.
3. **Investor Cohorts**: Grouped by first transaction year (`cohort_year`). The **2024 Cohort** comprised 4,803 investors with **₹349.11 Cr** invested capital.
4. **SIP Continuity & At-Risk Flagging**: Out of 1,362 qualifying investors ($\ge 6$ SIPs), only **30 investors** maintained average installment gaps $\le 35$ days, yielding a **2.20% SIP Continuity Rate**.
5. **Sector HHI Concentration**: `Axis Bluechip Fund` displays highest portfolio concentration (**Sector HHI = 0.2968**, IT sector weight = 48.69%).

---

## 13. Power BI Dashboard
The project includes a 4-page interactive Power BI dashboard:
* **Page 1: Industry Overview**: Executive KPIs, total market AUM, SIP vs. Lumpsum volume split, category AUM breakdown.
* **Page 2: Fund Performance Analytics**: Risk-return scatter plot (CAGR vs. Volatility), Sharpe/Sortino comparison, Alpha/Beta ranking table.
* **Page 3: Investor & Transaction Analytics**: Investor demographics, city-wise transaction heatmaps, income bracket analysis, SIP ticket size distribution.
* **Page 4: SIP Market & Trend Analysis**: Monthly SIP inflow time series, retention gap distribution, and risk cohort segmentation.

*Dashboard URL: To be added after Power BI publication*

---

## 14. Project Structure
```
mutual-fund-analysis/
├── Advanced_Analytics.ipynb         # Master Advanced Analytics Jupyter Notebook
├── Dashboard.pdf                    # 4-Page Executive Power BI Export
├── README.md                        # Master Documentation
├── recommender.py                   # Standalone Simple Fund Recommender Engine CLI
├── rolling_sharpe_chart.png         # Rolling 90-Day Sharpe Plot Deliverable
├── run_pipeline.py                  # Master End-to-End Execution Pipeline
├── var_cvar_report.csv              # Historical VaR/CVaR Metrics CSV Deliverable
├── mutual_fund_analysis.db          # SQLite Star Schema Database
│
├── DATASETS/
│   ├── raw/                         # Raw input CSV datasets (01-09)
│   └── processed/                   # Cleaned CSV files (nav, transactions, performance)
│
├── DOCUMENTATION/                   # Complete project documentation & reports
│   ├── Bluestock_Mutual_Fund_Analytics_Report.pdf  # Final 18-Page PDF Report
│   └── Bluestock_Mutual_Fund_Analytics_Slides.pdf  # Final 12-Slide Presentation PDF
│
└── SOURCE CODE/
    ├── generate_powerbi_dashboard.py# Automated Power BI visual exporter script
    ├── notebooks/                   # Jupyter notebooks (01_inspect, 02_eda, 03_advanced)
    ├── reports/                     # Generated query reports & PNG visual exports
    ├── scripts/                     # Python ETL modules (clean_*, load_to_sqlite, etc.)
    └── sql/                         # DDL schema & 10 analytical SQL queries
```

---

## 15. Technologies Used
* **Programming Language**: Python 3.10+
* **Data Processing & Analytics**: Pandas, NumPy, SciPy
* **Database & Querying**: SQLite3, SQLAlchemy, SQL DDL/DML
* **Data Visualization**: Matplotlib, Seaborn, Plotly
* **Business Intelligence**: Microsoft Power BI Desktop, DAX
* **Document Processing**: ReportLab (Python PDF generation)

---

## 16. Installation / Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Krishnanikhil-eng/bluestock.git
   cd mutual-fund-analysis
   ```

2. **Set Up Python Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Required Dependencies**:
   ```bash
   pip install -r "SOURCE CODE/requirements.txt"
   ```

---

## 17. How to Run the Project
To run the entire end-to-end pipeline (data verification, ETL cleaning, database creation, SQL analytics, advanced metrics, and artifact export) in a single command:

```bash
python run_pipeline.py
```

---

## 18. How to Run the ETL Pipeline
To execute the ETL cleaning and SQLite database ingestion scripts individually:

```bash
# Clean raw NAV history, transactions, and scheme performance CSVs
python "SOURCE CODE/scripts/clean_nav.py"
python "SOURCE CODE/scripts/clean_transactions.py"
python "SOURCE CODE/scripts/clean_performance.py"

# Build and load SQLite Star Schema Database
python "SOURCE CODE/scripts/load_to_sqlite.py"

# Execute 10 Analytical SQL queries and write query_results.md
python "SOURCE CODE/scripts/run_queries.py"
```

---

## 19. How to Run Advanced Analytics
To execute the advanced analytics module or run the standalone fund recommender:

```bash
# Run complete 8-task advanced analytics script
python "SOURCE CODE/scripts/run_advanced_analytics.py"

# Run standalone CLI Fund Recommender Engine
python recommender.py High
python recommender.py Moderate
python recommender.py Low
```

---

## 20. How to Open/View the Dashboard
1. Open **Power BI Desktop**.
2. File $\rightarrow$ Open $\rightarrow$ Select `Dashboard.pbix` (if available) or view the pre-rendered PDF/PNG deliverables:
   * View `Dashboard.pdf` in any standard PDF reader.
   * View page screenshots in root: `page1_industry_overview.png`, `page2_fund_performance.png`, `page3_investor_analytics.png`, `page4_sip_market_trends.png`.

---

## 21. Output Files
* `mutual_fund_analysis.db`: Complete SQLite Star Schema database.
* `var_cvar_report.csv`: 95% Historical VaR and CVaR calculations for 40 schemes.
* `rolling_sharpe_chart.png`: High-res plot of 90-day rolling Sharpe ratio over time.
* `Advanced_Analytics.ipynb`: Executed notebook with all calculations & 5 insights.
* `recommender.py`: Command-line executable fund recommender engine.
* `query_results.md`: Markdown summary of 10 analytical SQL business queries.
* `Dashboard.pdf`: 4-page Power BI dashboard PDF export.

---

## 22. Limitations
* **Historical NAV Window**: Daily NAV data spans 2022–2026; longer 10-year historical backtesting data would improve VaR estimation accuracy.
* **Asset Class Scope**: Portfolio sector holdings (`09_portfolio_holdings.csv`) cover 34 equity schemes; debt fund underlying bond holdings are not in raw holdings.
* **Power BI Service Publishing**: Online Power BI Service publishing link depends on organizational workspace permissions (local PBIX/PDF fully available).

---

## 23. Future Improvements
* **GARCH & Monte Carlo VaR**: Implement GARCH(1,1) dynamic volatility forecasting and Monte Carlo simulations for tail-risk stress testing.
* **Real-time AMFI API Ingestion**: Integrate live web scraping/API ingestion from AMFI India to automatically fetch daily NAV updates.
* **Machine Learning Investor Churn**: Train Logistic Regression / XGBoost models to predict SIP drop-off probability using transaction gap features.

---

## 24. Author
* **Project Developer**: Bluestock Mutual Fund Analytics Team
* **Corpus / Repository**: `Krishnanikhil-eng/bluestock`
* **Capstone Sponsor**: Bluestock Fintech Internship Program
* **Date**: August 2026
