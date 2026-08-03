# Mutual Fund Data Analysis - Query Results Report

This report documents the results of executing 10 analytical SQL queries against the star schema database.

## Database File: `mutual_fund_analysis.db`

### -- Query 1: Top 5 funds by AUM (Scheme-level)
```sql
-- Business Value: Helps identify the largest and most popular funds by asset size.
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;
```

|   amfi_code | scheme_name                                           | fund_house        |   aum_crore |
|------------:|:------------------------------------------------------|:------------------|------------:|
|      148568 | Mirae Asset Emerging Bluechip Fund - Regular - Growth | Mirae Asset MF    |       49046 |
|      120842 | Kotak Emerging Equity Fund - Regular - Growth         | Kotak Mahindra MF |       47469 |
|      118634 | Nippon India Small Cap Fund - Regular - Growth        | Nippon India MF   |       43630 |
|      149322 | DSP Top 100 Equity Fund - Regular - Growth            | DSP Mutual Fund   |       41828 |
|      102886 | UTI Mid Cap Fund - Regular - Growth                   | UTI Mutual Fund   |       41728 |

----------------------------------------

### -- Query 2: Average monthly NAV per fund
```sql
-- Business Value: Shows the price trend and performance stability of NAV on a month-to-month basis.
SELECT 
    f.scheme_name,
    d.year,
    d.month,
    ROUND(AVG(n.nav), 4) as avg_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date = d.date
GROUP BY n.amfi_code, d.year, d.month
ORDER BY f.scheme_name, d.year, d.month
LIMIT 20;
```

| scheme_name                                   |   year |   month |   avg_nav |
|:----------------------------------------------|-------:|--------:|----------:|
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       1 |   309.998 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       2 |   311.278 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       3 |   306.012 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       4 |   307.198 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       5 |   306.249 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       6 |   315.593 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       7 |   325.435 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       8 |   329.515 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |       9 |   320.802 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |      10 |   310.121 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |      11 |   329.758 |
| ABSL Frontline Equity Fund - Regular - Growth |   2022 |      12 |   341.369 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       1 |   346.108 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       2 |   353.315 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       3 |   350.918 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       4 |   359.247 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       5 |   364.095 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       6 |   339.068 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       7 |   336.394 |
| ABSL Frontline Equity Fund - Regular - Growth |   2023 |       8 |   343.64  |

----------------------------------------

### -- Query 3: SIP Year-over-Year growth
```sql
-- Business Value: Calculates the annual growth of SIP investment volumes to assess long-term recurring inflow trends.
WITH sip_annual AS (
    SELECT 
        d.year,
        SUM(t.amount_inr) as total_sip_amount
    FROM fact_transactions t
    JOIN dim_date d ON t.transaction_date = d.date
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year
)
SELECT 
    year,
    total_sip_amount,
    LAG(total_sip_amount) OVER (ORDER BY year) as prev_year_sip_amount,
    ROUND(
        (total_sip_amount - LAG(total_sip_amount) OVER (ORDER BY year)) * 100.0 / LAG(total_sip_amount) OVER (ORDER BY year), 
        2
    ) as yoy_growth_pct
FROM sip_annual;
```

|   year |   total_sip_amount |   prev_year_sip_amount |   yoy_growth_pct |
|-------:|-------------------:|-----------------------:|-----------------:|
|   2024 |        1.53233e+08 |          nan           |           nan    |
|   2025 |        6.40004e+07 |            1.53233e+08 |           -58.23 |

----------------------------------------

### -- Query 4: Transactions grouped by state
```sql
-- Business Value: Identifies the geographical distribution of investments to optimize marketing and sales strategies.
SELECT 
    state,
    COUNT(*) as transaction_count,
    SUM(amount_inr) as total_amount_inr,
    ROUND(AVG(amount_inr), 2) as avg_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;
```

| state          |   transaction_count |   total_amount_inr |   avg_amount_inr |
|:---------------|--------------------:|-------------------:|-----------------:|
| Punjab         |                2965 |        3.1578e+08  |           106503 |
| Tamil Nadu     |                2806 |        3.15177e+08 |           112323 |
| Madhya Pradesh |                2931 |        3.08312e+08 |           105190 |
| Rajasthan      |                2577 |        2.98646e+08 |           115889 |
| Gujarat        |                2780 |        2.98359e+08 |           107323 |
| West Bengal    |                2748 |        2.97183e+08 |           108145 |
| Telangana      |                2718 |        2.90219e+08 |           106777 |
| Delhi          |                2677 |        2.89633e+08 |           108193 |
| Uttar Pradesh  |                2695 |        2.85369e+08 |           105888 |
| Haryana        |                2736 |        2.79634e+08 |           102206 |
| Karnataka      |                2621 |        2.73754e+08 |           104446 |
| Maharashtra    |                2524 |        2.69513e+08 |           106780 |

----------------------------------------

### -- Query 5: Funds with expense ratio < 1%
```sql
-- Business Value: Finds low-cost mutual funds, which are highly attractive to fee-sensitive retail investors.
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.category,
    p.expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC;
```

|   amfi_code | scheme_name                                          | category   |   expense_ratio_pct |
|------------:|:-----------------------------------------------------|:-----------|--------------------:|
|      118636 | Nippon India Gilt Securities Fund - Regular - Growth | Debt       |                0.55 |
|      100025 | HDFC Short Term Debt Fund - Regular - Growth         | Debt       |                0.56 |
|      120844 | Kotak Liquid Fund - Regular - Growth                 | Debt       |                0.6  |
|      119552 | SBI Bluechip Fund - Direct Plan - Growth             | Equity     |                0.66 |
|      118633 | Nippon India Large Cap Fund - Direct - Growth        | Equity     |                0.72 |
|      119599 | SBI Small Cap Fund - Direct Plan - Growth            | Equity     |                0.72 |
|      120507 | ICICI Pru Liquid Fund - Regular - Growth             | Debt       |                0.74 |
|      119093 | Axis Bluechip Fund - Direct - Growth                 | Equity     |                0.75 |
|      119120 | SBI Magnum Gilt Fund - Regular Plan - Growth         | Debt       |                0.77 |
|      125498 | HDFC Mid-Cap Opportunities Fund - Direct - Growth    | Equity     |                0.78 |
|      101208 | ABSL Liquid Fund - Regular - Growth                  | Debt       |                0.79 |
|      120504 | ICICI Pru Bluechip Fund - Direct - Growth            | Equity     |                0.8  |
|      118635 | Nippon India ETF Nifty 50 BeES                       | Equity     |                0.89 |
|      125497 | HDFC Top 100 Fund - Direct Plan - Growth             | Equity     |                0.92 |

----------------------------------------

### -- Query 6: Category breakdown of total AUM and fund count
```sql
-- Business Value: Highlights which product categories (e.g. Small Cap, Liquid, Bluechip) dominate the assets under management.
SELECT 
    f.category,
    COUNT(DISTINCT f.amfi_code) as num_funds,
    SUM(p.aum_crore) as category_aum_crore,
    ROUND(AVG(p.return_3yr_pct), 2) as avg_3yr_return_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY category_aum_crore DESC;
```

| category   |   num_funds |   category_aum_crore |   avg_3yr_return_pct |
|:-----------|------------:|---------------------:|---------------------:|
| Equity     |          34 |               855846 |                15.46 |
| Debt       |           6 |               187818 |                 6.29 |

----------------------------------------

### -- Query 7: High risk-adjusted return funds (Sharpe > 1.0, Beta < 1.0)
```sql
-- Business Value: Identifies funds that deliver superior returns relative to their volatility and outperform the broader market with lower risk.
SELECT 
    f.scheme_name,
    f.category,
    p.sharpe_ratio,
    p.beta,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio > 1.0 AND p.beta < 1.0
ORDER BY p.sharpe_ratio DESC;
```

| scheme_name                                          | category   |   sharpe_ratio |   beta |   return_3yr_pct |
|:-----------------------------------------------------|:-----------|---------------:|-------:|-----------------:|
| ICICI Pru Liquid Fund - Regular - Growth             | Debt       |           7.68 |   0.26 |             7.68 |
| Kotak Liquid Fund - Regular - Growth                 | Debt       |           6.18 |   0.47 |             6.18 |
| ABSL Liquid Fund - Regular - Growth                  | Debt       |           5.14 |   0.43 |             5.14 |
| HDFC Short Term Debt Fund - Regular - Growth         | Debt       |           1.84 |   0.44 |             7.37 |
| SBI Magnum Gilt Fund - Regular Plan - Growth         | Debt       |           1.52 |   0.22 |             6.07 |
| Nippon India Gilt Securities Fund - Regular - Growth | Debt       |           1.33 |   0.37 |             5.31 |
| HDFC Top 100 Fund - Regular Plan - Growth            | Equity     |           1.06 |   0.97 |            14.84 |
| Mirae Asset Large Cap Fund - Regular - Growth        | Equity     |           1.06 |   0.96 |            14.81 |

----------------------------------------

### -- Query 8: Average transaction size and preference by annual income bracket
```sql
-- Business Value: Segments investors by income level and transaction type to target products based on purchasing power.
SELECT 
    CASE 
        WHEN annual_income_lakh < 5.0 THEN 'Low Income (<5L)'
        WHEN annual_income_lakh BETWEEN 5.0 AND 15.0 THEN 'Middle Income (5L-15L)'
        ELSE 'High Income (>15L)'
    END as income_group,
    transaction_type,
    COUNT(*) as num_transactions,
    SUM(amount_inr) as total_volume_inr,
    ROUND(AVG(amount_inr), 2) as avg_transaction_amount
FROM fact_transactions
GROUP BY income_group, transaction_type
ORDER BY income_group, total_volume_inr DESC;
```

| income_group           | transaction_type   |   num_transactions |   total_volume_inr |   avg_transaction_amount |
|:-----------------------|:-------------------|-------------------:|-------------------:|-------------------------:|
| High Income (>15L)     | Lumpsum            |               5075 |        1.29332e+09 |                 254842   |
| High Income (>15L)     | Redemption         |               3161 |        7.9303e+08  |                 250879   |
| High Income (>15L)     | SIP                |              12555 |        1.3854e+08  |                  11034.7 |
| Low Income (<5L)       | Lumpsum            |                501 |        1.28859e+08 |                 257203   |
| Low Income (<5L)       | Redemption         |                329 |        8.23626e+07 |                 250342   |
| Low Income (<5L)       | SIP                |               1239 |        1.36578e+07 |                  11023.3 |
| Middle Income (5L-15L) | Lumpsum            |               2519 |        6.37642e+08 |                 253133   |
| Middle Income (5L-15L) | Redemption         |               1477 |        3.69133e+08 |                 249921   |
| Middle Income (5L-15L) | SIP                |               5922 |        6.50354e+07 |                  10982   |

----------------------------------------

### -- Query 9: Net transaction inflows (Purchases - Redemptions) by fund house
```sql
-- Business Value: Shows net positive/negative cash flows for each AMC, indicating investor trust and market share growth.
SELECT 
    f.fund_house,
    SUM(CASE WHEN t.transaction_type IN ('SIP', 'Lumpsum') THEN t.amount_inr ELSE 0 END) as total_purchases,
    SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount_inr ELSE 0 END) as total_redemptions,
    SUM(CASE WHEN t.transaction_type IN ('SIP', 'Lumpsum') THEN t.amount_inr ELSE -t.amount_inr END) as net_inflow_inr
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
GROUP BY f.fund_house
ORDER BY net_inflow_inr DESC;
```

| fund_house               |   total_purchases |   total_redemptions |   net_inflow_inr |
|:-------------------------|------------------:|--------------------:|-----------------:|
| SBI Mutual Fund          |       2.87742e+08 |         1.44635e+08 |      1.43108e+08 |
| ICICI Prudential MF      |       2.83337e+08 |         1.52439e+08 |      1.30898e+08 |
| Nippon India MF          |       2.77869e+08 |         1.51927e+08 |      1.25942e+08 |
| HDFC Mutual Fund         |       2.83905e+08 |         1.63227e+08 |      1.20678e+08 |
| Axis Mutual Fund         |       2.37442e+08 |         1.23419e+08 |      1.14024e+08 |
| UTI Mutual Fund          |       1.88074e+08 |         9.56e+07    |      9.24736e+07 |
| Kotak Mahindra MF        |       2.20197e+08 |         1.30189e+08 |      9.00073e+07 |
| DSP Mutual Fund          |       1.61448e+08 |         8.76481e+07 |      7.37995e+07 |
| Aditya Birla Sun Life MF |       1.69069e+08 |         9.61404e+07 |      7.29282e+07 |
| Mirae Asset MF           |       1.67973e+08 |         9.9302e+07  |      6.86712e+07 |

----------------------------------------

### -- Query 10: Funds outperforming their 3-year benchmark (Alpha > 0 and Return > Benchmark)
```sql
-- Business Value: Evaluates fund manager skill by filtering for funds that successfully generated positive alpha.
SELECT 
    f.scheme_name,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    p.alpha
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.alpha > 0.0 AND p.return_3yr_pct > p.benchmark_3yr_pct
ORDER BY p.alpha DESC;
```

| scheme_name                                           |   return_3yr_pct |   benchmark_3yr_pct |   alpha |
|:------------------------------------------------------|-----------------:|--------------------:|--------:|
| HDFC Short Term Debt Fund - Regular - Growth          |             7.37 |                5.39 |    1.98 |
| Kotak Emerging Equity Fund - Regular - Growth         |            18.23 |               16.32 |    1.91 |
| ICICI Pru Liquid Fund - Regular - Growth              |             7.68 |                5.83 |    1.85 |
| Kotak Flexicap Fund - Regular - Growth                |            15.65 |               13.8  |    1.85 |
| ABSL Small Cap Fund - Regular - Growth                |            22.38 |               20.54 |    1.84 |
| DSP Top 100 Equity Fund - Regular - Growth            |            12.82 |               11    |    1.82 |
| Nippon India ETF Nifty 50 BeES                        |            11.77 |                9.97 |    1.8  |
| UTI Flexi Cap Fund - Regular - Growth                 |            15.34 |               13.55 |    1.79 |
| SBI Bluechip Fund - Direct Plan - Growth              |            11.3  |                9.52 |    1.78 |
| Nippon India Large Cap Fund - Direct - Growth         |            12.33 |               10.63 |    1.7  |
| Mirae Asset Emerging Bluechip Fund - Regular - Growth |            14.56 |               12.86 |    1.7  |
| Mirae Asset Large Cap Fund - Regular - Growth         |            14.81 |               13.19 |    1.62 |
| SBI Magnum Gilt Fund - Regular Plan - Growth          |             6.07 |                4.47 |    1.6  |
| Kotak Liquid Fund - Regular - Growth                  |             6.18 |                4.66 |    1.52 |
| Axis Bluechip Fund - Direct - Growth                  |            12.14 |               10.71 |    1.43 |
| Axis Midcap Fund - Regular - Growth                   |            15.18 |               13.76 |    1.42 |
| Axis Bluechip Fund - Regular - Growth                 |            11.84 |               10.43 |    1.41 |
| ABSL Frontline Equity Fund - Regular - Growth         |            13.78 |               12.44 |    1.34 |
| Kotak Bluechip Fund - Regular - Growth                |            12.25 |               10.98 |    1.27 |
| SBI Small Cap Fund - Regular Plan - Growth            |            23.39 |               22.16 |    1.23 |
| ABSL Liquid Fund - Regular - Growth                   |             5.14 |                3.96 |    1.18 |
| SBI Small Cap Fund - Direct Plan - Growth             |            23.14 |               22.01 |    1.13 |
| HDFC Top 100 Fund - Direct Plan - Growth              |            13.38 |               12.25 |    1.13 |
| UTI Mid Cap Fund - Regular - Growth                   |            15.61 |               14.49 |    1.12 |
| DSP Midcap Fund - Regular - Growth                    |            17.16 |               16.14 |    1.02 |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth    |            16.58 |               15.63 |    0.95 |
| UTI Nifty 50 Index Fund - Regular - Growth            |            12.1  |               11.17 |    0.93 |
| HDFC Mid-Cap Opportunities Fund - Direct - Growth     |            15.29 |               14.39 |    0.9  |
| Nippon India Gilt Securities Fund - Regular - Growth  |             5.31 |                4.42 |    0.89 |
| ICICI Pru Midcap Fund - Regular - Growth              |            18.08 |               17.19 |    0.89 |
| ICICI Pru Bluechip Fund - Direct - Growth             |            14.41 |               13.53 |    0.88 |
| SBI Bluechip Fund - Regular Plan - Growth             |            12.36 |               11.49 |    0.87 |
| Nippon India Large Cap Fund - Regular - Growth        |            14    |               13.14 |    0.86 |
| Nippon India Small Cap Fund - Regular - Growth        |            20.15 |               19.35 |    0.8  |
| HDFC Top 100 Fund - Regular Plan - Growth             |            14.84 |               14.06 |    0.78 |
| DSP Small Cap Fund - Regular - Growth                 |            20.08 |               19.39 |    0.69 |
| ICICI Pru Bluechip Fund - Regular - Growth            |            11.54 |               10.88 |    0.66 |
| ICICI Pru Value Discovery Fund - Regular - Growth     |            14.76 |               14.21 |    0.55 |
| Mirae Asset Tax Saver Fund - Regular - Growth         |            13.58 |               13.04 |    0.54 |
| Axis Small Cap Fund - Regular - Growth                |            20.98 |               20.47 |    0.51 |

----------------------------------------
