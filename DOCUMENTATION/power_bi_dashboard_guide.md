# Power BI Dashboard Implementation Guide
## Bluestock Mutual Fund Data Analyst Internship Project — Option 1: Direct CSV Import

---

## 📌 1. Project Overview & Strategy Confirmation

Per project strategy, we are using **Option 1 — Direct CSV Import** as the primary approach for the Power BI dashboard (`bluestock_mf_dashboard.pbix`). 

This approach uses your pre-cleaned datasets from `DATASETS/processed/` and supporting dimension files from `DATASETS/raw/` to reconstruct the **SQLite Star-Schema Model** in Power BI Desktop without needing SQLite ODBC drivers.

---

## 📂 2. Data Mapping Matrix: Processed CSVs ➔ Power BI Star Schema

Import the following **8 core tables** into Power BI Desktop (**Get Data ➔ Text/CSV**):

| Power BI Table Name | Source File Path | Schema Type | Primary / Foreign Key | Expected Row Count | Core Columns |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`dim_fund`** | `DATASETS/raw/01_fund_master.csv` | Dimension | PK: `amfi_code` | **40** | `amfi_code`, `fund_house`, `scheme_name`, `category`, `sub_category`, `plan`, `benchmark` |
| **`dim_date`** | Calculated DAX Table *(see section 3.1)* | Date Dimension | PK: `date` | **~1,461** | `date`, `year`, `month`, `quarter`, `year_month`, `month_name` |
| **`fact_nav`** | `DATASETS/processed/nav_history.csv` | Fact Table | FK: `amfi_code`, `date` | **64,320** | `amfi_code`, `date`, `nav` |
| **`fact_transactions`** | `DATASETS/processed/investor_transactions.csv` | Fact Table | FK: `amfi_code`, `transaction_date` | **32,778** | `investor_id`, `transaction_date`, `amfi_code`, `transaction_type`, `amount_inr`, `state`, `age_group`, `city_tier` |
| **`fact_performance`** | `DATASETS/processed/scheme_performance.csv` | Fact Table | FK: `amfi_code` | **40** | `amfi_code`, `return_1yr_pct`, `return_3yr_pct`, `std_dev_ann_pct`, `aum_crore`, `sharpe_ratio`, `alpha`, `beta` |
| **`fact_aum`** | `DATASETS/raw/03_aum_by_fund_house.csv` | Fact Table | FK: `date`, `fund_house` | **90** | `date`, `fund_house`, `aum_crore`, `aum_lakh_crore` |
| **`fact_sip_inflows`** | `DATASETS/raw/04_monthly_sip_inflows.csv` | Fact Table | FK: `month` (`date`) | **48** | `month`, `sip_inflow_crore`, `active_sip_accounts_crore` |
| **`fact_category_inflows`**| `DATASETS/raw/05_category_inflows.csv` | Fact Table | FK: `month` (`date`), `category` | **144** | `month`, `category`, `net_inflow_crore` |

*Reference Table (Optional for Benchmark comparisons):*
* `fact_benchmark`: `DATASETS/raw/10_benchmark_indices.csv` (8,050 rows)

---

## 🔗 3. Data Modeling & Star Schema Relationships

### 3.1 Creating the Date Dimension (`dim_date`) in Power BI
In Power BI Desktop, navigate to **Modeling ➔ New Table** and paste this DAX snippet:

```dax
dim_date = 
VAR MinDate = DATE(2022, 1, 1)
VAR MaxDate = DATE(2025, 12, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(MinDate, MaxDate),
    "year", YEAR([Date]),
    "month", MONTH([Date]),
    "month_name", FORMAT([Date], "MMM"),
    "year_month", FORMAT([Date], "YYYY-MM"),
    "quarter", "Q" & FORMAT([Date], "Q"),
    "day_of_week", WEEKDAY([Date]),
    "is_weekend", IF(WEEKDAY([Date]) IN {1, 7}, 1, 0)
)
```

Mark this table as the official Date Table:
> **Right click `dim_date` ➔ Mark as Date Table ➔ Select `Date` column.**

---

### 3.2 Setting Up Star Schema Relationships

In **Model View**, establish the following **1-to-Many (`1:*`)** single-direction relationships:

```
                               ┌──────────────────────┐
                               │       dim_fund       │
                               │  (PK: amfi_code)     │
                               └──────────┬───────────┘
                                          │ 1
                     ┌────────────────────┼────────────────────┐
                   * │                  * │                  * │
        ┌────────────┴──────────┐ ┌───────┴──────────────┐ ┌────┴─────────┐
        │       fact_nav        │ │  fact_performance    │ │fact_transacti-│
        │ (FK: amfi_code, date) │ │  (FK: amfi_code)     │ │     ons       │
        └────────────┬──────────┘ └──────────────────────┘ └────┬────────┘
                   * │                                        * │
                     └────────────────────┬─────────────────────┘
                                        * │
                               ┌──────────┴───────────┐
                               │       dim_date       │
                               │    (PK: Date)        │
                               └──────────────────────┘
```

#### Detailed Relationship Rules:
1. `dim_fund[amfi_code]` **(1)** ➔ `fact_nav[amfi_code]` **(*)**
2. `dim_fund[amfi_code]` **(1)** ➔ `fact_performance[amfi_code]` **(1 or *)**
3. `dim_fund[amfi_code]` **(1)** ➔ `fact_transactions[amfi_code]` **(*)**
4. `dim_date[Date]` **(1)** ➔ `fact_nav[date]` **(*)**
5. `dim_date[Date]` **(1)** ➔ `fact_transactions[transaction_date]` **(*)**
6. `dim_date[Date]` **(1)** ➔ `fact_aum[date]` **(*)**
7. `dim_date[Date]` **(1)** ➔ `fact_sip_inflows[month]` **(*)**

---

## 🧮 4. DAX Measures Blueprint

Create a blank table named `_Measures` and add these DAX formulas:

### 4.1 Industry Overview Measures
```dax
Total AUM = 
IF(
    HASONEVALUE(fact_aum[aum_crore]),
    SUM(fact_aum[aum_crore]),
    CALCULATE(SUM(fact_performance[aum_crore]), REMOVEFILTERS(dim_date))
)

Total AUM Display = FORMAT([Total AUM] / 100000, "₹#,##0.00") & " Lakh Cr"

Total SIP Inflow = SUM(fact_sip_inflows[sip_inflow_crore])

Total SIP Inflow Display = FORMAT([Total SIP Inflow], "₹#,##0") & " Cr"

Total Folios = MAX(fact_sip_inflows[active_sip_accounts_crore]) // 26.12 Cr Industry Total
Total Folios Display = FORMAT([Total Folios], "0.00") & " Cr"

Total Schemes Count = DISTINCTCOUNT(dim_fund[amfi_code])
```

### 4.2 Fund Performance Measures
```dax
Avg 3Yr Return = AVERAGE(fact_performance[return_3yr_pct])

Avg Risk StdDev = AVERAGE(fact_performance[std_dev_ann_pct])

Latest NAV = 
VAR MaxDate = MAX(fact_nav[date])
RETURN CALCULATE(MAX(fact_nav[nav]), fact_nav[date] = MaxDate)

Sharpe Ratio Avg = AVERAGE(fact_performance[sharpe_ratio])

Fund Performance Rank = 
VAR ReturnScore = RANKX(ALLSELECTED(dim_fund), [Avg 3Yr Return], , DESC)
VAR RiskScore = RANKX(ALLSELECTED(dim_fund), [Avg Risk StdDev], , ASC)
RETURN (ReturnScore * 0.6) + (RiskScore * 0.4)
```

### 4.3 Investor Analytics Measures
```dax
Total Transaction Amount = SUM(fact_transactions[amount_inr])
Total Transaction Amount Cr = SUM(fact_transactions[amount_inr]) / 10000000

Total Transaction Count = COUNTROWS(fact_transactions)

Average SIP Amount = 
CALCULATE(
    AVERAGE(fact_transactions[amount_inr]),
    fact_transactions[transaction_type] = "SIP"
)
Average SIP Amount Display = FORMAT([Average SIP Amount], "₹#,##0")
```

### 4.4 Market Trends Measures
```dax
Total Category Inflow = SUM(fact_category_inflows[net_inflow_crore])

// Quarterly Aggregated Category Net Inflow
Quarterly Category Inflow = 
CALCULATE(
    SUM(fact_category_inflows[net_inflow_crore]),
    ALLEXCEPT(fact_category_inflows, dim_date[fiscal_quarter], dim_fund[category])
)

Top 5 Category Inflow FY25 = 
CALCULATE(
    SUM(fact_category_inflows[net_inflow_crore]),
    KEEPFILTERS(TOPN(5, ALL(fact_category_inflows[category]), SUM(fact_category_inflows[net_inflow_crore]), DESC))
)

Top 5 Category Share % = 
VAR CatInflow = SUM(fact_category_inflows[net_inflow_crore])
VAR TotalTop5Inflow = CALCULATE(SUM(fact_category_inflows[net_inflow_crore]), ALLSELECTED(fact_category_inflows[category]))
RETURN DIVIDE(CatInflow, TotalTop5Inflow, 0)
```

---

## 🎨 5. Dashboard Pages & Visual Configurations

### 📄 Page 1: Industry Overview
* **KPI Cards (Top):** Total AUM (₹81.50L Cr), SIP Inflows (₹31K Cr), Folios (26.12 Cr), Active Schemes (1,908).
* **Line Chart:** Industry AUM Trend (2022–2025).
* **Bar Chart:** AUM by AMC / Fund House (Sorted descending).

### 📄 Page 2: Fund Performance
* **Slicers:** Fund House, Category, Plan.
* **Scatter Plot:** X-axis = `Avg 3Yr Return`, Y-axis = `Avg Risk StdDev`, Bubble Size = `Total AUM`.
* **Scorecard Table:** Scheme Name, AMC, Category, Plan, Latest NAV, 3Yr Return, StdDev, AUM, Fund Score.
* **Line Chart:** NAV vs Benchmark comparison.

### 📄 Page 3: Investor Analytics
* **Slicers:** State, Age Group, City Tier.
* **Bar Chart:** Transaction Amount by State (Sorted descending).
* **Donut Chart:** Transaction Type Split (SIP vs Lumpsum vs Redemption).
* **Column Chart:** Age Group vs Average SIP Amount.
* **Line Chart:** Monthly Transaction Volume.

### 📄 Page 4: SIP & Market Trends
* **KPI Cards (Top):** Latest Monthly SIP (₹31,002 Cr), Total SIP AUM (₹15.90 Lakh Cr - 19.5% of AUM), Top Equity Category Inflow (Sectoral/Thematic ₹1,03,829 Cr), Benchmark Nifty 50 (24,250 Pts).
* **Combo Chart:** Monthly SIP Inflows (Columns) + Nifty 50 Index (Line on Secondary Y-Axis) (CY24–CY25 24-Month Horizon).
* **Heatmap Matrix:** Quarterly Category Net Inflows across FY25 Quarters (Q1–Q4 FY25).
* **Bar Chart:** Top Categories by Net Inflow FY25 (With exact ₹ Cr values, % Share of Top 5, and Institutional Treasury Callout Box).

### 📄 Drill-Through Page: NAV Detail
* Target Field: `dim_fund[amfi_code]`.
* Displays historical NAV trend, benchmark comparison, return/risk breakdown, and Back button.

---

## 🛈 6. Bluestock Visual Styling Tokens

* **Primary Blue:** `#0052CC` / `#1E3A8A`
* **Teal Accent:** `#00B8D9` / `#06B6D4`
* **Canvas Background:** `#F8FAFC`
* **Font:** Segoe UI / Inter (Bold headers, clean numeric formatting)

---

## 🚀 7. Incremental Git Commit Schedule

After completing each milestone, run the corresponding command in your shell:

```bash
# 1. Load CSVs & Build Relationships
git add .
git commit -m "feat: import processed csv datasets and recreate star schema model"

# 2. Page 1
git add .
git commit -m "feat: add industry overview dashboard page"

# 3. Page 2
git add .
git commit -m "feat: add fund performance dashboard page with risk return scatter plot"

# 4. Page 3
git add .
git commit -m "feat: add investor analytics dashboard with state and demographic split"

# 5. Page 4
git add .
git commit -m "feat: add sip and market trends dashboard page"

# 6. Interactivity & Theme
git add .
git commit -m "feat: add drillthrough page and apply bluestock visual theme"

# 7. Documentation & Final Deliverables
git add .
git commit -m "docs: add power bi implementation guide for direct csv import strategy"
```

---

## 📦 8. Final Deliverables

Export the completed files to the root workspace:
1. `bluestock_mf_dashboard.pbix`
2. `Dashboard.pdf`
3. `page1_industry_overview.png`
4. `page2_fund_performance.png`
5. `page3_investor_analytics.png`
6. `page4_sip_market_trends.png`
