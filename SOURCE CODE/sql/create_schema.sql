-- SQLite Star Schema DDL definitions for Mutual Fund Analysis

-- 1. Date Dimension Table
CREATE TABLE IF NOT EXISTS dim_date (
    date VARCHAR PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL
);

-- 2. Fund Dimension Table
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house VARCHAR NOT NULL,
    scheme_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    sub_category VARCHAR,
    plan VARCHAR,
    launch_date VARCHAR,
    benchmark VARCHAR,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager VARCHAR,
    risk_category VARCHAR,
    sebi_category_code VARCHAR
);

-- 3. NAV Fact Table
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER,
    date VARCHAR,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 4. Transactions Fact Table
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id VARCHAR NOT NULL,
    transaction_date VARCHAR NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type VARCHAR NOT NULL,
    amount_inr REAL NOT NULL,
    state VARCHAR,
    city VARCHAR,
    city_tier VARCHAR,
    age_group VARCHAR,
    gender VARCHAR,
    annual_income_lakh REAL,
    payment_mode VARCHAR,
    kyc_status VARCHAR,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
);

-- 5. Performance Fact Table
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name VARCHAR,
    fund_house VARCHAR,
    category VARCHAR,
    plan VARCHAR,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade VARCHAR,
    is_anomaly INTEGER,
    anomaly_reason VARCHAR,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 6. AUM Fact Table
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date VARCHAR NOT NULL,
    fund_house VARCHAR NOT NULL,
    aum_lakh_crore REAL NOT NULL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER NOT NULL,
    FOREIGN KEY (date) REFERENCES dim_date(date)
);
