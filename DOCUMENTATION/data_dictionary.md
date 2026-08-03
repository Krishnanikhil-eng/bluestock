# Mutual Fund Star Schema Data Dictionary

This data dictionary documents the database tables, fields, types, descriptions, and sources of the SQLite star schema designed for the mutual fund analysis pipeline.

---

## 1. Dimension Table: `dim_fund`
*Contains static metadata and characteristics of the mutual fund schemes.*

| Column Name | Data Type | Business Definition | Source Dataset |
| :--- | :--- | :--- | :--- |
| **amfi_code** (PK) | INTEGER | Association of Mutual Funds in India (AMFI) code; uniquely identifies a mutual fund scheme. | `01_fund_master.csv` |
| **fund_house** | VARCHAR | Name of the Asset Management Company (AMC) managing the fund (e.g. SBI Mutual Fund). | `01_fund_master.csv` |
| **scheme_name** | VARCHAR | Full name of the mutual fund scheme. | `01_fund_master.csv` |
| **category** | VARCHAR | Main asset class classification (e.g. Equity, Debt). | `01_fund_master.csv` |
| **sub_category** | VARCHAR | Specific investment mandate class (e.g. Large Cap, Gilt, Liquid, Small Cap). | `01_fund_master.csv` |
| **plan** | VARCHAR | Execution plan type (Direct Plan vs. Regular Plan). | `01_fund_master.csv` |
| **launch_date** | VARCHAR | Inception / start date of the fund scheme. | `01_fund_master.csv` |
| **benchmark** | VARCHAR | Index against which the fund's relative performance is evaluated. | `01_fund_master.csv` |
| **min_sip_amount** | REAL | Minimum allowable monthly installment amount for System Investment Plans. | `01_fund_master.csv` |
| **min_lumpsum_amount**| REAL | Minimum allowable one-time transaction amount. | `01_fund_master.csv` |
| **fund_manager** | VARCHAR | Name of the fund's primary portfolio manager. | `01_fund_master.csv` |
| **risk_category** | VARCHAR | Risk profile level of the scheme (e.g. Very High, Moderate). | `01_fund_master.csv` |
| **sebi_category_code**| VARCHAR | Standard classification code assigned by SEBI. | `01_fund_master.csv` |

---

## 2. Dimension Table: `dim_date`
*Dynamic calendar dimension generated across all unique dates in the system.*

| Column Name | Data Type | Business Definition | Source Dataset |
| :--- | :--- | :--- | :--- |
| **date** (PK) | VARCHAR | Calendar date in `YYYY-MM-DD` format. | Dynamically derived from unique dates in NAV, Transaction, and AUM tables |
| **year** | INTEGER | Calendar year (e.g. 2024). | Derived from `date` |
| **month** | INTEGER | Month number of the year (1 = January, 12 = December). | Derived from `date` |
| **day** | INTEGER | Day number of the month (1-31). | Derived from `date` |
| **quarter** | INTEGER | Quarter of the year (1 to 4). | Derived from `date` |
| **day_of_week** | INTEGER | Day index of the week (0 = Monday, 6 = Sunday). | Derived from `date` |
| **is_weekend** | INTEGER | Binary flag indicating if date is a weekend (1 = Yes, 0 = No). | Derived from `date` |

---

## 3. Fact Table: `fact_nav`
*Stores daily Net Asset Value (NAV) historical records for each mutual fund scheme.*

| Column Name | Data Type | Business Definition | Source Dataset |
| :--- | :--- | :--- | :--- |
| **amfi_code** (FK) | INTEGER | Scheme identifier linking to `dim_fund(amfi_code)`. | `02_nav_history.csv` |
| **date** (FK) | VARCHAR | Valuation date linking to `dim_date(date)`. | `02_nav_history.csv` |
| **nav** | REAL | Net Asset Value (price per unit in INR) of the scheme on that date. | `02_nav_history.csv` |

---

## 4. Fact Table: `fact_transactions`
*Records granular transactions executed by individual investors.*

| Column Name | Data Type | Business Definition | Source Dataset |
| :--- | :--- | :--- | :--- |
| **transaction_id** (PK)| INTEGER | Unique auto-incremented primary key for each transaction. | Generated dynamically |
| **investor_id** | VARCHAR | Unique identifier code for the retail investor. | `08_investor_transactions.csv` |
| **transaction_date** (FK)| VARCHAR | Date of the transaction linking to `dim_date(date)`. | `08_investor_transactions.csv` |
| **amfi_code** (FK) | INTEGER | Target fund scheme code linking to `dim_fund(amfi_code)`. | `08_investor_transactions.csv` |
| **transaction_type** | VARCHAR | Class of transaction (SIP, Lumpsum, or Redemption). | `08_investor_transactions.csv` |
| **amount_inr** | REAL | Financial size of the transaction in Indian Rupees (INR). | `08_investor_transactions.csv` |
| **state** | VARCHAR | Geography: Investor's residential state in India. | `08_investor_transactions.csv` |
| **city** | VARCHAR | Geography: Investor's residential city. | `08_investor_transactions.csv` |
| **city_tier** | VARCHAR | Categorization of the city based on size/demographics (Tier-1, Tier-2, Tier-3). | `08_investor_transactions.csv` |
| **age_group** | VARCHAR | Age demographic grouping of the investor. | `08_investor_transactions.csv` |
| **gender** | VARCHAR | Gender of the investor. | `08_investor_transactions.csv` |
| **annual_income_lakh** | REAL | Annual income of the investor in Lakh INR (1 Lakh = 100,000). | `08_investor_transactions.csv` |
| **payment_mode** | VARCHAR | Mode of funding the investment (e.g. Net Banking, UPI, Cheque). | `08_investor_transactions.csv` |
| **kyc_status** | VARCHAR | Know Your Customer validation status (Verified, Pending). | `08_investor_transactions.csv` |

---

## 5. Fact Table: `fact_performance`
*Contains scheme-level return statistics, volatility metrics, and risk-adjusted ratios.*

| Column Name | Data Type | Business Definition | Source Dataset |
| :--- | :--- | :--- | :--- |
| **amfi_code** (PK, FK) | INTEGER | Scheme code linking to `dim_fund(amfi_code)`. | `07_scheme_performance.csv` |
| **scheme_name** | VARCHAR | Full scheme title. | `07_scheme_performance.csv` |
| **fund_house** | VARCHAR | Asset Management Company (AMC) name. | `07_scheme_performance.csv` |
| **category** | VARCHAR | Scheme broad category (Equity, Debt). | `07_scheme_performance.csv` |
| **plan** | VARCHAR | Execution plan type (Direct vs. Regular). | `07_scheme_performance.csv` |
| **return_1yr_pct** | REAL | One-year trailing annualized return percentage. | `07_scheme_performance.csv` |
| **return_3yr_pct** | REAL | Three-year trailing annualized return percentage. | `07_scheme_performance.csv` |
| **return_5yr_pct** | REAL | Five-year trailing annualized return percentage. | `07_scheme_performance.csv` |
| **benchmark_3yr_pct** | REAL | Three-year trailing annualized return of the benchmark index. | `07_scheme_performance.csv` |
| **alpha** | REAL | Measure of excess return generated relative to the benchmark. | `07_scheme_performance.csv` |
| **beta** | REAL | Measure of systemic risk or volatility sensitivity compared to the market. | `07_scheme_performance.csv` |
| **sharpe_ratio** | REAL | Risk-adjusted return measure (Sharpe Ratio). | `07_scheme_performance.csv` |
| **sortino_ratio** | REAL | Downside risk-adjusted return measure (Sortino Ratio). | `07_scheme_performance.csv` |
| **std_dev_ann_pct** | REAL | Annualized standard deviation of returns (volatility metric). | `07_scheme_performance.csv` |
| **max_drawdown_pct** | REAL | Peak-to-trough decline percentage representing maximum drop risk. | `07_scheme_performance.csv` |
| **aum_crore** | REAL | Assets Under Management for the specific scheme in Crores INR (1 Crore = 10,000,000). | `07_scheme_performance.csv` |
| **expense_ratio_pct** | REAL | Operational cost of managing the fund as a percentage of scheme AUM. | `07_scheme_performance.csv` |
| **morningstar_rating**| INTEGER | Quality score assigned by Morningstar (from 1 to 5). | `07_scheme_performance.csv` |
| **risk_grade** | VARCHAR | Risk profile assessment grade (e.g. Above Average, High). | `07_scheme_performance.csv` |
| **is_anomaly** | INTEGER | Flag indicating if this scheme's record had clean-up anomalies (1 = Yes, 0 = No). | Derived dynamically during cleaning |
| **anomaly_reason** | VARCHAR | Detailed explanation of the flagged anomalies, if any. | Derived dynamically during cleaning |

---

## 6. Fact Table: `fact_aum`
*Quarterly reports of total Assets Under Management (AUM) at the Asset Management Company (AMC) level.*

| Column Name | Data Type | Business Definition | Source Dataset |
| :--- | :--- | :--- | :--- |
| **aum_id** (PK) | INTEGER | Unique auto-incremented primary key for each AUM entry. | Generated dynamically |
| **date** (FK) | VARCHAR | Quarter-end report date linking to `dim_date(date)`. | `03_aum_by_fund_house.csv` |
| **fund_house** | VARCHAR | AMC name (joins with `dim_fund(fund_house)`). | `03_aum_by_fund_house.csv` |
| **aum_lakh_crore** | REAL | Total assets managed by AMC in Lakh Crore INR (1 Lakh Crore = 1 Trillion). | `03_aum_by_fund_house.csv` |
| **aum_crore** | REAL | Total assets managed by AMC in Crores INR (1 Crore = 10 Million). | `03_aum_by_fund_house.csv` |
| **num_schemes** | INTEGER | Count of active fund schemes under the AMC at that report date. | `03_aum_by_fund_house.csv` |
