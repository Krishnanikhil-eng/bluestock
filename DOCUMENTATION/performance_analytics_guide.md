# 📊 Mutual Fund Performance Analytics Guide & Implementation Blueprint

This guide provides a step-by-step technical blueprint and financial breakdown for implementing the **Performance Analytics Module** of your mutual fund capstone project.

---

## 📁 File Organization & Folder Structure

To keep your project structured cleanly according to standard data engineering practices, save your new deliverables in the following workspace locations:

```
mutual-fund-analysis/
│
├── DATASETS/
│   ├── raw/                             # Original input datasets (01_fund_master.csv, 02_nav_history.csv, etc.)
│   └── processed/
│       ├── fund_scorecard.csv           # 🎯 DELIVERABLE 2: Composite Scorecard (0-100)
│       └── alpha_beta.csv               # 🎯 DELIVERABLE 3: Alpha, Beta & Regression Stats
│
├── DOCUMENTATION/
│   ├── data_dictionary.md
│   ├── eda_completion_report.md
│   └── performance_analytics_guide.md   # 📖 THIS GUIDE
│
├── SOURCE CODE/
│   ├── notebooks/
│   │   ├── 01_dataset_inspection.ipynb
│   │   ├── 02_exploratory_data_analysis.ipynb
│   │   └── Performance_Analytics.ipynb  # 🎯 DELIVERABLE 1: Main Analytics Notebook
│   │
│   └── reports/
│       └── images/
│           └── benchmark_comparison.png # 🎯 DELIVERABLE 4: Benchmark Comparison Plot
```

---

## 📐 Mathematical Formulas & Business Rationale

### 1. Daily Returns Calculation
* **Formula:**  
  $$R_t = \frac{\text{NAV}_t}{\text{NAV}_{t-1}} - 1$$
* **Business Rationale:** Raw NAV prices cannot be directly compared across different schemes because launch prices vary (e.g., ₹10 vs ₹500). Daily percentage returns convert price series into stationary, scale-free return distributions, enabling standardized statistical analysis.
* **Python Code:**
  ```python
  import pandas as pd

  # Pivot NAV history: rows = dates, columns = scheme AMFI codes
  nav_pivot = nav_df.pivot(index='date', columns='amfi_code', values='nav').sort_index()

  # Compute percentage change
  daily_returns = nav_pivot.pct_change().dropna()
  ```

---

### 2. Compound Annual Growth Rate (CAGR)
* **Formula:**  
  $$\text{CAGR} = \left(\frac{\text{NAV}_{\text{end}}}{\text{NAV}_{\text{start}}}\right)^{\frac{1}{N}} - 1$$
  *(where $N \in \{1, 3, 5\}$ years)*
* **Business Rationale:** Simple average annual returns overestimate performance due to compounding. CAGR provides the geometric mean growth rate, assuming the investment compounded smoothly over the holding period.
* **Python Code:**
  ```python
  import numpy as np

  def calculate_cagr(nav_series, years):
      # Assuming 252 trading days per year
      n_days = int(years * 252)
      if len(nav_series) < n_days:
          return np.nan
      start_val = nav_series.iloc[-n_days]
      end_val = nav_series.iloc[-1]
      return (end_val / start_val) ** (1.0 / years) - 1.0

  # Example usage across 1y, 3y, 5y
  cagr_1y = nav_pivot.apply(calculate_cagr, years=1)
  cagr_3y = nav_pivot.apply(calculate_cagr, years=3)
  cagr_5y = nav_pivot.apply(calculate_cagr, years=5)
  ```

---

### 3. Annualized Sharpe Ratio
* **Formula:**  
  $$\text{Sharpe Ratio} = \frac{\text{Mean}(R_p - R_f)}{\text{Std}(R_p)} \times \sqrt{252}$$
  *(where $R_f = \frac{6.5\%}{252} = \frac{0.065}{252}$ is the daily risk-free rate proxy)*
* **Business Rationale:** High returns are unimpressive if achieved through excessive risk. The Sharpe ratio evaluates risk-adjusted return by measuring excess return generated per unit of total volatility.
* **Python Code:**
  ```python
  rf_annual = 0.065
  rf_daily = rf_annual / 252.0

  excess_returns = daily_returns - rf_daily
  sharpe_ratios = (excess_returns.mean() / daily_returns.std()) * np.sqrt(252)
  ```

---

### 4. Annualized Sortino Ratio
* **Formula:**  
  $$\text{Sortino Ratio} = \frac{\text{Mean}(R_p - R_f)}{\sigma_{\text{downside}} \times \sqrt{252}}$$
  $$\sigma_{\text{downside}} = \sqrt{\frac{1}{M} \sum_{R_t < R_f} (R_t - R_f)^2}$$
* **Business Rationale:** The Sharpe ratio unfairly penalizes upside volatility (sudden price surges). Sortino only penalizes negative volatility (downside losses), offering a realistic metric for risk-averse investors.
* **Python Code:**
  ```python
  def calculate_sortino(returns_series, rf_daily=0.065/252):
      excess = returns_series - rf_daily
      downside = excess[excess < 0]
      downside_std = np.sqrt(np.mean(downside**2))
      if downside_std == 0 or np.isnan(downside_std):
          return np.nan
      return (excess.mean() / downside_std) * np.sqrt(252)

  sortino_ratios = daily_returns.apply(calculate_sortino)
  ```

---

### 5. Alpha ($\alpha$) & Beta ($\beta$) via OLS Regression
* **Formula:**  
  $$R_{\text{fund}, t} = \alpha_{\text{daily}} + \beta \times R_{\text{Nifty100}, t} + \epsilon_t$$
  $$\text{Annualized Alpha} = \alpha_{\text{daily}} \times 252$$
* **Business Rationale:** Beta measures systematic market risk (sensitivity to Nifty 100 movements). Alpha measures the fund manager's stock-picking ability to generate outperformance independent of market movements.
* **Python Code:**
  ```python
  from scipy import stats

  # Load Nifty 100 benchmark returns
  nifty100_returns = benchmark_returns['NIFTY100']

  alpha_beta_list = []
  for amfi_code in daily_returns.columns:
      fund_ret = daily_returns[amfi_code]
      # Align dates
      aligned = pd.concat([fund_ret, nifty100_returns], axis=1, join='inner').dropna()
      
      slope, intercept, r_value, p_value, std_err = stats.linregress(aligned.iloc[:, 1], aligned.iloc[:, 0])
      
      alpha_annual = intercept * 252.0
      beta = slope
      r_squared = r_value ** 2
      
      alpha_beta_list.append({
          'amfi_code': amfi_code,
          'alpha': alpha_annual,
          'beta': beta,
          'r_squared': r_squared,
          'p_value': p_value
      })

  df_alpha_beta = pd.DataFrame(alpha_beta_list)
  ```

---

### 6. Maximum Drawdown (MDD) & Date Range
* **Formula:**  
  $$\text{Drawdown}_t = \frac{\text{NAV}_t}{\max_{0 \le s \le t}(\text{NAV}_s)} - 1$$
  $$\text{MDD} = \min_t(\text{Drawdown}_t)$$
* **Business Rationale:** Represents the worst peak-to-trough capital loss an investor would experience during the holding period. Critical for evaluating stress behavior.
* **Python Code:**
  ```python
  def get_max_drawdown_info(nav_series):
      running_max = nav_series.cummax()
      drawdowns = (nav_series / running_max) - 1.0
      
      mdd = drawdowns.min()
      trough_date = drawdowns.idxmin()
      peak_date = nav_series.loc[:trough_date].idxmax()
      
      return pd.Series({
          'max_drawdown': mdd,
          'peak_date': peak_date,
          'trough_date': trough_date
      })

  mdd_summary = nav_pivot.apply(get_max_drawdown_info).T
  ```

---

### 7. Composite Fund Scorecard (0–100)
* **Weights:**
  - `30%` × 3-Year CAGR Rank
  - `25%` × Sharpe Ratio Rank
  - `20%` × Alpha Rank
  - `15%` × Expense Ratio Rank *(Inverse: lower ratio = higher percentile)*
  - `10%` × Max Drawdown Rank *(Inverse: smaller loss = higher percentile)*
* **Business Rationale:** Combines return potential, risk-adjusted performance, manager skill, cost efficiency, and capital protection into a unified, balanced metric for fund selection.
* **Python Code:**
  ```python
  # Percentile ranking (0 to 100)
  scorecard = pd.DataFrame(index=fund_master['amfi_code'])

  scorecard['rank_3yr'] = cagr_3y.rank(pct=True) * 100
  scorecard['rank_sharpe'] = sharpe_ratios.rank(pct=True) * 100
  scorecard['rank_alpha'] = df_alpha_beta.set_index('amfi_code')['alpha'].rank(pct=True) * 100
  scorecard['rank_expense'] = fund_master.set_index('amfi_code')['expense_ratio_pct'].rank(pct=True, ascending=False) * 100
  scorecard['rank_mdd'] = mdd_summary['max_drawdown'].rank(pct=True, ascending=False) * 100

  # Weighted Score Calculation
  scorecard['final_score'] = (
      0.30 * scorecard['rank_3yr'] +
      0.25 * scorecard['rank_sharpe'] +
      0.20 * scorecard['rank_alpha'] +
      0.15 * scorecard['rank_expense'] +
      0.10 * scorecard['rank_mdd']
  )

  scorecard = scorecard.sort_values('final_score', ascending=False)
  ```

---

### 8. Benchmark Comparison & Tracking Error
* **Formula:**  
  $$\text{Tracking Error (TE)} = \text{Std}(R_{\text{fund}} - R_{\text{benchmark}}) \times \sqrt{252}$$
* **Business Rationale:** Measures how closely an active fund tracks or deviates from its benchmark index over time.
* **Python Code:**
  ```python
  import matplotlib.pyplot as plt

  # Select Top 5 funds by final score
  top_5_codes = scorecard.head(5).index

  # Calculate cumulative returns over 3 years
  cum_returns = (1 + daily_returns[top_5_codes]).cumprod()
  bench_cum = (1 + benchmark_returns[['NIFTY50', 'NIFTY100']]).cumprod()

  plt.figure(figsize=(12, 6))
  for code in top_5_codes:
      name = fund_master_dict[code]
      plt.plot(cum_returns.index, cum_returns[code], label=f"Fund: {name}")

  plt.plot(bench_cum.index, bench_cum['NIFTY50'], label="Benchmark: NIFTY 50", linestyle="--", color="black")
  plt.plot(bench_cum.index, bench_cum['NIFTY100'], label="Benchmark: NIFTY 100", linestyle=":", color="red")

  plt.title("Top 5 Funds vs Benchmarks (3-Year Cumulative Growth)", fontweight='bold')
  plt.ylabel("Growth Factor (1.0 = Initial)")
  plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
  plt.tight_layout()
  plt.savefig("../../SOURCE CODE/reports/images/benchmark_comparison.png", dpi=150)
  ```

---

## 🎯 Exporting Deliverables Checklist

When building your notebook, export the output files using these exact calls:

1. **`Performance_Analytics.ipynb`** → Save in `SOURCE CODE/notebooks/Performance_Analytics.ipynb`
2. **`fund_scorecard.csv`** → Save in `DATASETS/processed/fund_scorecard.csv`  
   `scorecard.to_csv("../../DATASETS/processed/fund_scorecard.csv")`
3. **`alpha_beta.csv`** → Save in `DATASETS/processed/alpha_beta.csv`  
   `df_alpha_beta.to_csv("../../DATASETS/processed/alpha_beta.csv", index=False)`
4. **`benchmark_comparison.png`** → Save in `SOURCE CODE/reports/images/benchmark_comparison.png`  
   `plt.savefig("../../SOURCE CODE/reports/images/benchmark_comparison.png", dpi=150)`
