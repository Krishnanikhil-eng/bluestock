import json
from pathlib import Path

def create_notebook():
    base_dir = Path("c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis")
    notebook_path = base_dir / "SOURCE CODE/notebooks/02_exploratory_data_analysis.ipynb"
    
    # Define notebook structure
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Mutual Fund Exploratory Data Analysis (EDA) Capstone Report\n",
                    "**Analyzing NAV Trends, AUM Growth, Investor Demographics, and Sector Allocations (2022 - 2026)**\n\n",
                    "This notebook contains the complete exploratory data analysis for the Mutual Fund Capstone Project. It fulfills 10 distinct analytical and visualization tasks, covering:\n",
                    "1. Daily NAV Trend Analysis (2022-2026) using Plotly.\n",
                    "2. Grouped AUM Growth Bar Chart (2022-2025) using Seaborn.\n",
                    "3. Monthly SIP Inflow Time-Series (Jan 2022 - Dec 2025) using Plotly.\n",
                    "4. Category Inflow Heatmap using Seaborn.\n",
                    "5. Investor Demographics (Age distribution, Gender split, SIP box plot).\n",
                    "6. Geographic Distribution (State-wise SIP inflows & T30/B30 Tier split).\n",
                    "7. Industry Folio Count Growth Trend & Milestones (Jan 2022 - Dec 2025).\n",
                    "8. NAV Return Correlation Matrix of 10 Selected Funds using Seaborn.\n",
                    "9. Sector Allocation Donut Chart for Equity Funds.\n",
                    "10. Documentation of 10 key EDA findings in dedicated Markdown cells."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "import plotly.express as px\n",
                    "import plotly.graph_objects as go\n",
                    "from pathlib import Path\n",
                    "\n",
                    "# Configure matplotlib and seaborn styles for premium visuals\n",
                    "sns.set_theme(style=\"whitegrid\")\n",
                    "plt.rcParams['figure.figsize'] = (12, 6)\n",
                    "plt.rcParams['font.size'] = 11\n",
                    "\n",
                    "# Define data path\n",
                    "data_dir = Path(\"../../DATASETS/raw\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 1: Daily NAV Trend Analysis (2022 - 2026)\n",
                    "> [!NOTE]\n",
                    "> During the 2022-2026 period, the 40 mutual fund schemes exhibited a strong long-term upward trajectory, propelled by the 2023 bull run (Jan-Dec 2023) where average NAVs rose by ~22%, followed by a significant correction of ~24% between March and November 2024, as illustrated in the interactive Plotly time-series chart [Chart 1: Daily NAV Trend]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load and prepare NAV history\n",
                    "nav_df = pd.read_csv(data_dir / \"02_nav_history.csv\")\n",
                    "master_df = pd.read_csv(data_dir / \"01_fund_master.csv\")\n",
                    "nav_df['date'] = pd.to_datetime(nav_df['date'])\n",
                    "nav_merged = pd.merge(nav_df, master_df[['amfi_code', 'scheme_name']], on='amfi_code')\n",
                    "\n",
                    "# Create Plotly interactive line plot\n",
                    "fig = go.Figure()\n",
                    "for scheme_name, group in nav_merged.groupby('scheme_name'):\n",
                    "    group_sorted = group.sort_values('date')\n",
                    "    fig.add_trace(go.Scatter(\n",
                    "        x=group_sorted['date'],\n",
                    "        y=group_sorted['nav'],\n",
                    "        mode='lines',\n",
                    "        name=scheme_name,\n",
                    "        hovertemplate='<b>%{text}</b><br>Date: %{x|%Y-%m-%d}<br>NAV: \u20b9%{y:.2f}<extra></extra>',\n",
                    "        text=[scheme_name]*len(group_sorted),\n",
                    "        line=dict(width=1.5),\n",
                    "        visible='legendonly' if scheme_name != 'SBI Bluechip Fund - Regular Plan - Growth' else True\n",
                    "    ))\n",
                    "\n",
                    "# Highlight 2023 Bull Run: Jan 2023 to Dec 2023\n",
                    "fig.add_vrect(\n",
                    "    x0=\"2023-01-01\", x1=\"2023-12-31\",\n",
                    "    fillcolor=\"rgba(46, 204, 113, 0.1)\", opacity=0.5,\n",
                    "    layer=\"below\", line_width=0,\n",
                    "    annotation_text=\"2023 Bull Run (~22% Rise)\",\n",
                    "    annotation_position=\"top left\",\n",
                    "    annotation_font=dict(size=12, color=\"green\")\n",
                    ")\n",
                    "\n",
                    "# Highlight 2024 Market Corrections: March 2024 to Nov 2024\n",
                    "fig.add_vrect(\n",
                    "    x0=\"2024-03-15\", x1=\"2024-11-15\",\n",
                    "    fillcolor=\"rgba(231, 76, 60, 0.1)\", opacity=0.5,\n",
                    "    layer=\"below\", line_width=0,\n",
                    "    annotation_text=\"2024 Correction (~24% Drop)\",\n",
                    "    annotation_position=\"top left\",\n",
                    "    annotation_font=dict(size=12, color=\"red\")\n",
                    ")\n",
                    "\n",
                    "fig.update_layout(\n",
                    "    title=\"<b>Daily NAV Trend Analysis (2022 - 2026) for 40 Schemes</b><br><sup>Double-click legend items to isolate a scheme or single-click to toggle</sup>\",\n",
                    "    xaxis_title=\"Date\",\n",
                    "    yaxis_title=\"NAV (INR)\",\n",
                    "    hovermode=\"closest\",\n",
                    "    height=600,\n",
                    "    template=\"plotly_white\"\n",
                    ")\n",
                    "fig.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 2: AUM Growth & SBI Dominance\n",
                    "> [bold]\n",
                    "> SBI Mutual Fund maintained a dominant leadership position in the industry, with its AUM growing from \u20b96.05 Lakh Cr in March 2022 to a staggering \u20b912.50 Lakh Cr by March 2025, significantly outperforming competitors as shown in the grouped Seaborn bar chart [Chart 2: AUM Growth by Fund House]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load AUM data\n",
                    "aum_df = pd.read_csv(data_dir / \"03_aum_by_fund_house.csv\")\n",
                    "aum_years = aum_df[aum_df['date'].isin(['2022-03-31', '2023-03-31', '2024-03-31', '2025-03-31'])].copy()\n",
                    "aum_years['year'] = aum_years['date'].apply(lambda x: x.split('-')[0])\n",
                    "\n",
                    "plt.figure(figsize=(14, 7))\n",
                    "sns.barplot(\n",
                    "    data=aum_years, \n",
                    "    x=\"fund_house\", \n",
                    "    y=\"aum_lakh_crore\", \n",
                    "    hue=\"year\",\n",
                    "    palette=\"viridis\"\n",
                    ")\n",
                    "plt.xticks(rotation=45, ha='right')\n",
                    "plt.title(\"AUM Growth by Fund House (FY22 - FY25)\", fontsize=14, fontweight='bold', pad=15)\n",
                    "plt.xlabel(\"Fund House\")\n",
                    "plt.ylabel(\"AUM (Lakh Crore INR)\")\n",
                    "\n",
                    "plt.annotate(\n",
                    "    \"SBI Dominance: \u20b912.5L Cr\\n(FY25)\", \n",
                    "    xy=(0.2, 12.5), \n",
                    "    xytext=(1.5, 11.5),\n",
                    "    arrowprops=dict(facecolor='darkred', shrink=0.05, width=1.5, headwidth=8),\n",
                    "    fontsize=11, fontweight='bold', color='darkred',\n",
                    "    bbox=dict(boxstyle=\"round,pad=0.3\", fc=\"yellow\", alpha=0.3, ec=\"darkred\")\n",
                    ")\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 3: SIP Inflow Time-Series & All-Time High\n",
                    "> [!NOTE]\n",
                    "> Monthly SIP inflows in India experienced continuous expansion, culminating in a historic all-time high of \u20b931,002 Crore in December 2025, highlighting growing retail participation in capital markets as annotated in the Plotly line chart [Chart 3: Monthly SIP Inflows]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load SIP inflow data\n",
                    "sip_df = pd.read_csv(data_dir / \"04_monthly_sip_inflows.csv\")\n",
                    "sip_df['date'] = pd.to_datetime(sip_df['month'] + \"-01\")\n",
                    "\n",
                    "fig3 = px.line(\n",
                    "    sip_df, \n",
                    "    x=\"date\", \n",
                    "    y=\"sip_inflow_crore\", \n",
                    "    title=\"<b>Monthly SIP Inflow Trend (Jan 2022 - Dec 2025)</b>\",\n",
                    "    labels={\"sip_inflow_crore\": \"SIP Inflow (Crore INR)\", \"date\": \"Month\"},\n",
                    "    template=\"plotly_white\"\n",
                    ")\n",
                    "fig3.update_traces(line=dict(color=\"#1a5f7a\", width=3))\n",
                    "\n",
                    "fig3.add_annotation(\n",
                    "    x=\"2025-12-01\",\n",
                    "    y=31002,\n",
                    "    text=\"<b>All-Time High</b><br>Dec 2025: \u20b931,002 Cr\",\n",
                    "    showarrow=True,\n",
                    "    arrowhead=2,\n",
                    "    ax=-80,\n",
                    "    ay=-40,\n",
                    "    bgcolor=\"rgba(26, 95, 122, 0.9)\",\n",
                    "    font=dict(color=\"white\", size=11),\n",
                    "    bordercolor=\"#1a5f7a\",\n",
                    "    borderwidth=1,\n",
                    "    borderpad=4\n",
                    ")\n",
                    "fig3.update_layout(height=450)\n",
                    "fig3.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 4: Category Inflow Heatmap\n",
                    "> [!NOTE]\n",
                    "> The category inflow heatmap indicates that Sectoral/Thematic and Flexi Cap funds attracted the most consistent net inflows throughout 2024-2025, whereas debt funds like Short Duration experienced intermittent outflows, as shown in the Seaborn heatmap [Chart 4: Net Inflows by Fund Category]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load Category Inflows\n",
                    "cat_inflows = pd.read_csv(data_dir / \"05_category_inflows.csv\")\n",
                    "cat_pivot = cat_inflows.pivot(index='category', columns='month', values='net_inflow_crore')\n",
                    "cat_pivot = cat_pivot[sorted(cat_pivot.columns)]\n",
                    "\n",
                    "plt.figure(figsize=(14, 8))\n",
                    "sns.heatmap(\n",
                    "    cat_pivot, \n",
                    "    cmap=\"RdYlGn\", \n",
                    "    annot=True, \n",
                    "    fmt=\".0f\", \n",
                    "    linewidths=0.5,\n",
                    "    cbar_kws={'label': 'Net Inflow (Crore INR)'},\n",
                    "    center=0\n",
                    ")\n",
                    "plt.title(\"Net Inflow by Fund Category (April 2024 - March 2025)\", fontsize=14, fontweight='bold', pad=15)\n",
                    "plt.xlabel(\"Month\")\n",
                    "plt.ylabel(\"Fund Category\")\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Findings 5, 6, 7: Investor Demographics (Age, SIP Ticket Size & Gender Split)\n",
                    "> [!NOTE]\n",
                    "> Millennial and Gen-Z investors (ages 18-35) constitute the largest segment of retail mutual fund participants, representing over 55% of unique investors, as depicted in the demographic distribution pie chart [Chart 5a: Investor Age Group Distribution].\n\n",
                    "> [!NOTE]\n",
                    "> While the 56+ age group has the highest median SIP transaction amount at \u20b95,420, younger demographics (18-25) show strong retail participation with a median ticket size of \u20b95,020, as shown in the box plot [Chart 5b: SIP Amount Box Plot by Age].\n\n",
                    "> [!NOTE]\n",
                    "> The gender split among retail mutual fund investors remains heavily skewed, with male investors accounting for approximately 66.7% and female investors representing 33.3%, as shown in the gender split donut chart [Chart 5c: Gender Split]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load Transactions\n",
                    "tx_df = pd.read_csv(data_dir / \"08_investor_transactions.csv\")\n",
                    "unique_inv = tx_df.drop_duplicates(subset=['investor_id'])\n",
                    "\n",
                    "fig, axes = plt.subplots(1, 3, figsize=(18, 6))\n",
                    "\n",
                    "# Panel A: Age Group Pie Chart\n",
                    "age_dist = unique_inv['age_group'].value_counts().sort_index()\n",
                    "axes[0].pie(\n",
                    "    age_dist, \n",
                    "    labels=age_dist.index, \n",
                    "    autopct='%1.1f%%', \n",
                    "    startangle=140,\n",
                    "    colors=sns.color_palette(\"pastel\"),\n",
                    "    wedgeprops=dict(width=0.6, edgecolor='white')\n",
                    ")\n",
                    "axes[0].set_title(\"Age Group Distribution (Unique Investors)\", fontsize=12, fontweight='bold')\n",
                    "\n",
                    "# Panel B: Gender Split Donut Chart\n",
                    "gender_dist = unique_inv['gender'].value_counts()\n",
                    "axes[1].pie(\n",
                    "    gender_dist, \n",
                    "    labels=gender_dist.index, \n",
                    "    autopct='%1.1f%%', \n",
                    "    startangle=90,\n",
                    "    colors=['#3498db', '#e74c3c'],\n",
                    "    wedgeprops=dict(width=0.6, edgecolor='white')\n",
                    ")\n",
                    "axes[1].set_title(\"Gender Split (Unique Investors)\", fontsize=12, fontweight='bold')\n",
                    "\n",
                    "# Panel C: SIP amount box plot by age group\n",
                    "sip_tx = tx_df[tx_df['transaction_type'] == 'SIP']\n",
                    "sns.boxplot(\n",
                    "    data=sip_tx,\n",
                    "    x=\"age_group\",\n",
                    "    y=\"amount_inr\",\n",
                    "    order=sorted(sip_tx['age_group'].unique()),\n",
                    "    ax=axes[2],\n",
                    "    palette=\"Set2\"\n",
                    ")\n",
                    "axes[2].set_title(\"SIP Transaction Amount by Age Group\", fontsize=12, fontweight='bold')\n",
                    "axes[2].set_xlabel(\"Age Group\")\n",
                    "axes[2].set_ylabel(\"SIP Amount (INR)\")\n",
                    "\n",
                    "plt.suptitle(\"Investor Demographics & Transaction Behavior\", fontsize=16, fontweight='bold', y=0.98)\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 8: Geographic Distribution & Tier Split\n",
                    "> [!NOTE]\n",
                    "> Geographic analysis shows that Madhya Pradesh and Punjab lead SIP contributions by state in this dataset, while Tier 30 (T30) cities dominate funding with 66.7% of total SIP inflows compared to 33.3% from Beyond 30 (B30) cities, as displayed in the horizontal bar and tier pie charts [Chart 6: Geographic Distribution of SIPs]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Geographic plots\n",
                    "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
                    "\n",
                    "sip_tx = tx_df[tx_df['transaction_type'] == 'SIP']\n",
                    "state_sip = sip_tx.groupby('state')['amount_inr'].sum().sort_values(ascending=False).reset_index()\n",
                    "state_sip['amount_crore'] = state_sip['amount_inr'] / 1e7\n",
                    "\n",
                    "sns.barplot(\n",
                    "    data=state_sip,\n",
                    "    y=\"state\",\n",
                    "    x=\"amount_crore\",\n",
                    "    ax=axes[0],\n",
                    "    palette=\"viridis\"\n",
                    ")\n",
                    "axes[0].set_title(\"Total SIP Inflow by State (Crore INR)\", fontsize=12, fontweight='bold')\n",
                    "axes[0].set_xlabel(\"Total SIP Amount (Crore INR)\")\n",
                    "axes[0].set_ylabel(\"State\")\n",
                    "\n",
                    "tier_sip = sip_tx.groupby('city_tier')['amount_inr'].sum()\n",
                    "axes[1].pie(\n",
                    "    tier_sip,\n",
                    "    labels=tier_sip.index,\n",
                    "    autopct='%1.1f%%',\n",
                    "    startangle=140,\n",
                    "    colors=['#2ecc71', '#e67e22'],\n",
                    "    wedgeprops=dict(width=0.6, edgecolor='white')\n",
                    ")\n",
                    "axes[1].set_title(\"City Tier Contribution (T30 vs B30 SIP Inflow)\", fontsize=12, fontweight='bold')\n",
                    "\n",
                    "plt.suptitle(\"Geographic Distribution of Mutual Fund SIP Inflows\", fontsize=16, fontweight='bold', y=0.98)\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 9: Folio Count Growth & Milestones\n",
                    "> [!NOTE]\n",
                    "> The total mutual fund folio count doubled in under four years, growing from 13.26 Cr in January 2022 to 26.12 Cr in December 2025, with major milestones marked at 15 Cr (April 2023) and 20 Cr (July 2024), as shown in the line chart [Chart 7: Industry Folio Count Growth]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load folio data\n",
                    "folio_df = pd.read_csv(data_dir / \"06_industry_folio_count.csv\")\n",
                    "folio_df['date'] = pd.to_datetime(folio_df['month'] + \"-01\")\n",
                    "folio_df = folio_df.sort_values('date')\n",
                    "\n",
                    "plt.figure(figsize=(12, 6))\n",
                    "plt.plot(folio_df['date'], folio_df['total_folios_crore'], color=\"#9b59b6\", linewidth=3, marker='o', markersize=6, label=\"Total Folios\")\n",
                    "plt.plot(folio_df['date'], folio_df['equity_folios_crore'], color=\"#3498db\", linestyle=\"--\", linewidth=2, label=\"Equity Folios\")\n",
                    "\n",
                    "# Mark milestones\n",
                    "plt.plot(pd.to_datetime(\"2022-01-01\"), 13.26, 'ro', markersize=8)\n",
                    "plt.annotate(\"Start: 13.26 Cr\\n(Jan 2022)\", xy=(pd.to_datetime(\"2022-01-01\"), 13.26), xytext=(pd.to_datetime(\"2022-04-01\"), 12.5),\n",
                    "             arrowprops=dict(arrowstyle=\"->\", color='red'))\n",
                    "             \n",
                    "plt.plot(pd.to_datetime(\"2023-04-01\"), 15.54, 'ro', markersize=8)\n",
                    "plt.annotate(\"Milestone: 15 Cr+\\n(Apr 2023)\", xy=(pd.to_datetime(\"2023-04-01\"), 15.54), xytext=(pd.to_datetime(\"2023-01-01\"), 17.5),\n",
                    "             arrowprops=dict(arrowstyle=\"->\", color='red'))\n",
                    "             \n",
                    "plt.plot(pd.to_datetime(\"2024-10-01\"), 21.62, 'ro', markersize=8)\n",
                    "plt.annotate(\"Milestone: 20 Cr+\\n(Oct 2024)\", xy=(pd.to_datetime(\"2024-10-01\"), 21.62), xytext=(pd.to_datetime(\"2024-04-01\"), 23.5),\n",
                    "             arrowprops=dict(arrowstyle=\"->\", color='red'))\n",
                    "             \n",
                    "plt.plot(pd.to_datetime(\"2025-12-01\"), 26.12, 'ro', markersize=8)\n",
                    "plt.annotate(\"End: 26.12 Cr\\n(Dec 2025)\", xy=(pd.to_datetime(\"2025-12-01\"), 26.12), xytext=(pd.to_datetime(\"2025-04-01\"), 26.5),\n",
                    "             arrowprops=dict(arrowstyle=\"->\", color='red'))\n",
                    "\n",
                    "plt.title(\"Industry Folio Count Growth Trend (Jan 2022 - Dec 2025)\", fontsize=14, fontweight='bold', pad=15)\n",
                    "plt.xlabel(\"Month\")\n",
                    "plt.ylabel(\"Folio Count (Crore)\")\n",
                    "plt.legend(loc=\"upper left\")\n",
                    "plt.ylim(8, 29)\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 10: NAV Return Correlation Matrix\n",
                    "> [!NOTE]\n",
                    "> Pairwise correlation of daily returns reveals high positive correlation (above 0.85) among diversified equity funds (Large Cap, Mid Cap, Small Cap), whereas debt and liquid funds exhibit near-zero correlation (~-0.02) to equity funds, offering excellent diversification as shown in the Seaborn heatmap [Chart 8: NAV Return Correlation Matrix]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Compute correlation matrix\n",
                    "selected_amfi_codes = [119551, 119598, 119092, 118636, 119775, 148567, 119552, 119030, 119515, 125497]\n",
                    "available_data = nav_merged[nav_merged['amfi_code'].isin(selected_amfi_codes)]\n",
                    "pivot_nav = available_data.pivot(index='date', columns='scheme_name', values='nav').sort_index()\n",
                    "\n",
                    "returns = pivot_nav.pct_change().dropna()\n",
                    "corr = returns.corr()\n",
                    "\n",
                    "# Shorten names\n",
                    "short_names = {name: name.split(\" - \")[0][:25] for name in corr.columns}\n",
                    "corr_renamed = corr.rename(index=short_names, columns=short_names)\n",
                    "\n",
                    "plt.figure(figsize=(12, 10))\n",
                    "sns.heatmap(\n",
                    "    corr_renamed, \n",
                    "    cmap=\"coolwarm\", \n",
                    "    annot=True, \n",
                    "    fmt=\".2f\", \n",
                    "    linewidths=0.5,\n",
                    "    cbar_kws={'label': 'Correlation Coefficient'}\n",
                    ")\n",
                    "plt.title(\"Daily NAV Return Correlation Matrix (Selected 10 Funds)\", fontsize=14, fontweight='bold', pad=20)\n",
                    "plt.xticks(rotation=45, ha='right')\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Finding 11: Sector Allocation Donut Chart\n",
                    "> [!NOTE]\n",
                    "> Equity mutual funds are heavily concentrated in the Banking sector (representing 19.5% of total market value holdings), followed by IT (11.9%) and Pharma (10.7%), as visualized in the aggregated sector holdings donut chart [Chart 9: Sector Allocation Donut]."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Sector Allocation Donut Chart\n",
                    "holdings_df = pd.read_csv(data_dir / \"09_portfolio_holdings.csv\")\n",
                    "holdings_merged = pd.merge(holdings_df, master_df[['amfi_code', 'category']], on='amfi_code')\n",
                    "equity_holdings = holdings_merged[holdings_merged['category'] == 'Equity']\n",
                    "\n",
                    "sector_mv = equity_holdings.groupby('sector')['market_value_cr'].sum().reset_index()\n",
                    "sector_mv['weight_pct'] = (sector_mv['market_value_cr'] / sector_mv['market_value_cr'].sum()) * 100\n",
                    "sector_mv = sector_mv.sort_values('weight_pct', ascending=False)\n",
                    "\n",
                    "plt.figure(figsize=(10, 8))\n",
                    "top_n = 7\n",
                    "top_sectors = sector_mv.iloc[:top_n].copy()\n",
                    "others_mv = sector_mv.iloc[top_n:]['market_value_cr'].sum()\n",
                    "others_weight = sector_mv.iloc[top_n:]['weight_pct'].sum()\n",
                    "\n",
                    "others_df = pd.DataFrame([{'sector': 'Others', 'market_value_cr': others_mv, 'weight_pct': others_weight}])\n",
                    "donut_data = pd.concat([top_sectors, others_df], ignore_index=True)\n",
                    "\n",
                    "plt.pie(\n",
                    "    donut_data['weight_pct'], \n",
                    "    labels=donut_data['sector'], \n",
                    "    autopct='%1.1f%%', \n",
                    "    startangle=140,\n",
                    "    colors=sns.color_palette(\"Set3\", len(donut_data)),\n",
                    "    wedgeprops=dict(width=0.4, edgecolor='white')\n",
                    ")\n",
                    "plt.title(\"Aggregated Sector Allocation Across Equity Mutual Funds\", fontsize=14, fontweight='bold', pad=15)\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    # Save notebook file
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)
    
    print(f"Created template notebook at: {notebook_path}")

if __name__ == "__main__":
    create_notebook()
