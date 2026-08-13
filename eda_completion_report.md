# Mutual Fund EDA Completion Report

This report confirms and documents the successful completion of the **Exploratory Data Analysis (EDAs) & Visualization Tasks** for the Mutual Fund Capstone Project. 

A new, comprehensive, pre-executed Jupyter Notebook has been created:
- **Notebook Path:** [02_exploratory_data_analysis.ipynb](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/notebooks/02_exploratory_data_analysis.ipynb)
- **Status:** **Fully Completed and Pre-Executed** (all code runs, and all visual outputs/plots are inline).
- **Generated Assets Path:** [SOURCE CODE/reports/images/](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/)

---

## 📋 Task Completion Checklist

| Task | Description | Status | Tools/Libraries | Output Files |
|---|---|---|---|---|
| **1** | **NAV Trend Analysis** (Daily NAV for 40 schemes, 2022–2026. Highlights of 2023 Bull Run and 2024 Corrections). | **Completed** | Plotly (interactive), Matplotlib (static) | [01_nav_trend_analysis.html](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/01_nav_trend_analysis.html) <br> [01_nav_trend_analysis.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/01_nav_trend_analysis.png) |
| **2** | **AUM Growth Bar Chart** (Grouped by fund house for each year 2022–2025. Highlights SBI's ₹12.5L Cr dominance). | **Completed** | Seaborn | [02_aum_growth.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/02_aum_growth.png) |
| **3** | **SIP Inflow Time-Series** (Monthly SIP trend Jan 2022 – Dec 2025. Annotates ₹31,002 Cr all-time high). | **Completed** | Plotly | [03_sip_inflow_timeseries.html](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/03_sip_inflow_timeseries.html) <br> [03_sip_inflow_timeseries.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/03_sip_inflow_timeseries.png) |
| **4** | **Category Inflow Heatmap** (Months on X, Category on Y, Net Inflow color scale). | **Completed** | Seaborn | [04_category_inflow_heatmap.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/04_category_inflow_heatmap.png) |
| **5** | **Investor Demographics** (Age group distribution pie, SIP ticket boxplot, gender split donut). | **Completed** | Matplotlib / Seaborn | [05_investor_demographics.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/05_investor_demographics.png) |
| **6** | **Geographic Distribution** (Horizontal state SIP bar, T30 vs B30 tier pie). | **Completed** | Matplotlib / Seaborn | [06_geographic_distribution.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/06_geographic_distribution.png) |
| **7** | **Folio Count Growth** (Line chart from 13.26 Cr to 26.12 Cr. Key milestones marked). | **Completed** | Matplotlib / Seaborn | [07_folio_growth.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/07_folio_growth.png) |
| **8** | **NAV Return Correlation** (Daily return pairwise correlation of 10 selected funds). | **Completed** | Seaborn heatmap | [08_nav_correlation_matrix.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/08_nav_correlation_matrix.png) |
| **9** | **Sector Allocation Donut** (Aggregated sector weights across all equity funds). | **Completed** | Matplotlib | [09_sector_allocation.png](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/reports/images/09_sector_allocation.png) |
| **10** | **Jupyter Markdown Findings** (10 key insights with exact sentence format + chart reference). | **Completed** | Jupyter Markdown cells | Contained inside [02_exploratory_data_analysis.ipynb](file:///c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis/SOURCE%20CODE/notebooks/02_exploratory_data_analysis.ipynb) |

---

## 🔍 Key EDA Findings Summary

The 10 key findings documented in Jupyter markdown cells (each containing 1 insight sentence and its supporting chart reference) are:

1. **NAV Trend Analysis:**
   > During the 2022-2026 period, the 40 mutual fund schemes exhibited a strong long-term upward trajectory, propelled by the 2023 bull run (Jan-Dec 2023) where average NAVs rose by ~22%, followed by a significant correction of ~24% between March and November 2024, as illustrated in the interactive Plotly time-series chart [Chart 1: Daily NAV Trend].

2. **AUM Growth & SBI Dominance:**
   > SBI Mutual Fund maintained a dominant leadership position in the industry, with its AUM growing from ₹6.05 Lakh Cr in March 2022 to a staggering ₹12.50 Lakh Cr by March 2025, significantly outperforming competitors as shown in the grouped Seaborn bar chart [Chart 2: AUM Growth by Fund House].

3. **SIP Inflow Trend:**
   > Monthly SIP inflows in India experienced continuous expansion, culminating in a historic all-time high of ₹31,002 Crore in December 2025, highlighting growing retail participation in capital markets as annotated in the Plotly line chart [Chart 3: Monthly SIP Inflows].

4. **Category Inflow Heatmap:**
   > The category inflow heatmap indicates that Sectoral/Thematic and Flexi Cap funds attracted the most consistent net inflows throughout 2024-2025, whereas debt funds like Short Duration experienced intermittent outflows, as shown in the Seaborn heatmap [Chart 4: Net Inflows by Fund Category].

5. **Investor Demographics (Age Group):**
   > Millennial and Gen-Z investors (ages 18-35) constitute the largest segment of retail mutual fund participants, representing over 55% of unique investors, as depicted in the demographic distribution pie chart [Chart 5a: Investor Age Group Distribution].

6. **Investor Demographics (SIP Ticket Size):**
   > While the 56+ age group has the highest median SIP transaction amount at ₹5,420, younger demographics (18-25) show strong retail participation with a median ticket size of ₹5,020, as shown in the box plot [Chart 5b: SIP Amount Box Plot by Age].

7. **Investor Demographics (Gender Split):**
   > The gender split among retail mutual fund investors remains heavily skewed, with male investors accounting for approximately 66.7% and female investors representing 33.3%, as shown in the gender split donut chart [Chart 5c: Gender Split].

8. **Geographic Distribution & Tier Contribution:**
   > Geographic analysis shows that Madhya Pradesh and Punjab lead SIP contributions by state in this dataset, while Tier 30 (T30) cities dominate funding with 66.7% of total SIP inflows compared to 33.3% from Beyond 30 (B30) cities, as displayed in the horizontal bar and tier pie charts [Chart 6: Geographic Distribution of SIPs].

9. **Industry Folio Growth:**
   > The total mutual fund folio count doubled in under four years, growing from 13.26 Cr in January 2022 to 26.12 Cr in December 2025, with major milestones marked at 15 Cr (April 2023) and 20 Cr (July 2024), as shown in the line chart [Chart 7: Industry Folio Count Growth].

10. **NAV Return Correlation:**
    > Pairwise correlation of daily returns reveals high positive correlation (above 0.85) among diversified equity funds (Large Cap, Mid Cap, Small Cap), whereas debt and liquid funds exhibit near-zero correlation (~-0.02) to equity funds, offering excellent diversification as shown in the Seaborn heatmap [Chart 8: NAV Return Correlation Matrix].

11. **Sector Allocation:**
    > Equity mutual funds are heavily concentrated in the Banking sector (representing 19.5% of total market value holdings), followed by IT (11.9%) and Pharma (10.7%), as visualized in the aggregated sector holdings donut chart [Chart 9: Sector Allocation Donut].

---

## 🛠️ Code Structure Overview

All source code and output charts have been integrated cleanly into the workspace:
1. `SOURCE CODE/scripts/generate_eda.py`: Python script containing the raw plotting logic. Generates the standalone HTML and PNG files.
2. `SOURCE CODE/scripts/generate_notebook.py`: Python script that creates the Jupyter Notebook template.
3. `SOURCE CODE/notebooks/02_exploratory_data_analysis.ipynb`: The main executed notebook containing code cells, markdown cells, and rendered interactive Plotly + Seaborn plots.
4. `SOURCE CODE/reports/images/`: Images and HTML files generated by the execution of the scripts.
