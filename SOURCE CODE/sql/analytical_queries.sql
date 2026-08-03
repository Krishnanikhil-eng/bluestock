-- Analytical SQL Queries for Mutual Fund Analysis Star Schema

-- Query 1: Top 5 funds by AUM (Scheme-level)
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

-- Query 2: Average monthly NAV per fund
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

-- Query 3: SIP Year-over-Year growth
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

-- Query 4: Transactions grouped by state
-- Business Value: Identifies the geographical distribution of investments to optimize marketing and sales strategies.
SELECT 
    state,
    COUNT(*) as transaction_count,
    SUM(amount_inr) as total_amount_inr,
    ROUND(AVG(amount_inr), 2) as avg_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- Query 5: Funds with expense ratio < 1%
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

-- Query 6: Category breakdown of total AUM and fund count
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

-- Query 7: High risk-adjusted return funds (Sharpe > 1.0, Beta < 1.0)
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

-- Query 8: Average transaction size and preference by annual income bracket
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

-- Query 9: Net transaction inflows (Purchases - Redemptions) by fund house
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

-- Query 10: Funds outperforming their 3-year benchmark (Alpha > 0 and Return > Benchmark)
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
