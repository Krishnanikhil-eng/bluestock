import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

def generate_eda_assets():
    # Define directories
    base_dir = Path("c:/Users/91784/OneDrive/Desktop/bluestock/mutual-fund-analysis")
    raw_dir = base_dir / "DATASETS/raw"
    images_dir = base_dir / "SOURCE CODE/reports/images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading datasets...")
    fund_master = pd.read_csv(raw_dir / "01_fund_master.csv")
    nav_history = pd.read_csv(raw_dir / "02_nav_history.csv")
    aum_by_fh = pd.read_csv(raw_dir / "03_aum_by_fund_house.csv")
    monthly_sip = pd.read_csv(raw_dir / "04_monthly_sip_inflows.csv")
    category_inflows = pd.read_csv(raw_dir / "05_category_inflows.csv")
    folio_count = pd.read_csv(raw_dir / "06_industry_folio_count.csv")
    scheme_perf = pd.read_csv(raw_dir / "07_scheme_performance.csv")
    transactions = pd.read_csv(raw_dir / "08_investor_transactions.csv")
    portfolio_holdings = pd.read_csv(raw_dir / "09_portfolio_holdings.csv")
    benchmark_indices = pd.read_csv(raw_dir / "10_benchmark_indices.csv")
    
    # -------------------------------------------------------------
    # Task 1: NAV trend analysis (Plotly)
    # -------------------------------------------------------------
    print("Generating Task 1: NAV Trend Analysis Plotly HTML...")
    nav_history['date'] = pd.to_datetime(nav_history['date'])
    nav_merged = pd.merge(nav_history, fund_master[['amfi_code', 'scheme_name']], on='amfi_code')
    
    # Create interactive line plot for all 40 schemes
    fig1 = go.Figure()
    
    # Group by scheme name and add traces
    for scheme_name, group in nav_merged.groupby('scheme_name'):
        group_sorted = group.sort_values('date')
        fig1.add_trace(go.Scatter(
            x=group_sorted['date'],
            y=group_sorted['nav'],
            mode='lines',
            name=scheme_name,
            hovertemplate='<b>%{text}</b><br>Date: %{x|%Y-%m-%d}<br>NAV: ₹%{y:.2f}<extra></extra>',
            text=[scheme_name]*len(group_sorted),
            line=dict(width=1.5),
            visible='legendonly' if scheme_name != 'SBI Bluechip Fund - Regular Plan - Growth' else True # default show one, others can be toggled
        ))
        
    # Highlight 2023 Bull Run: Jan 2023 to Dec 2023
    fig1.add_vrect(
        x0="2023-01-01", x1="2023-12-31",
        fillcolor="rgba(46, 204, 113, 0.1)", opacity=0.5,
        layer="below", line_width=0,
        annotation_text="2023 Bull Run (~22% Rise)",
        annotation_position="top left",
        annotation_font=dict(size=12, color="green")
    )
    
    # Highlight 2024 Market Corrections: March 2024 to Nov 2024
    fig1.add_vrect(
        x0="2024-03-15", x1="2024-11-15",
        fillcolor="rgba(231, 76, 60, 0.1)", opacity=0.5,
        layer="below", line_width=0,
        annotation_text="2024 Correction (~24% Drop)",
        annotation_position="top left",
        annotation_font=dict(size=12, color="red")
    )
    
    fig1.update_layout(
        title="<b>Daily NAV Trend Analysis (2022 - 2026) for 40 Schemes</b><br><sup>Double-click legend items to isolate a scheme or single-click to toggle</sup>",
        xaxis_title="Date",
        yaxis_title="NAV (INR)",
        hovermode="closest",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            font=dict(size=9)
        ),
        margin=dict(r=250, l=80, t=80, b=80),
        height=650,
        template="plotly_white"
    )
    
    # Save as HTML
    fig1.write_html(str(images_dir / "01_nav_trend_analysis.html"))
    
    # Generate a static Matplotlib backup for the notebook display if needed
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    # Plot top 5 schemes by AUM to keep the static version clean
    top_5_amfi = scheme_perf.nlargest(5, 'aum_crore')['amfi_code']
    top_5_data = nav_merged[nav_merged['amfi_code'].isin(top_5_amfi)]
    for name, group in top_5_data.groupby('scheme_name'):
        group_sorted = group.sort_values('date')
        plt.plot(group_sorted['date'], group_sorted['nav'], label=name, alpha=0.8, linewidth=2)
    plt.axvspan(pd.to_datetime("2023-01-01"), pd.to_datetime("2023-12-31"), color='green', alpha=0.1, label='2023 Bull Run')
    plt.axvspan(pd.to_datetime("2024-03-15"), pd.to_datetime("2024-11-15"), color='red', alpha=0.1, label='2024 Correction')
    plt.title("Daily NAV Trend Analysis (Top 5 Schemes by AUM, 2022-2026)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("NAV (INR)", fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.tight_layout()
    plt.savefig(images_dir / "01_nav_trend_analysis.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 2: AUM growth bar chart (Seaborn)
    # -------------------------------------------------------------
    print("Generating Task 2: AUM Growth Bar Chart...")
    # Filter AUM data for March 31 of each year (Financial Year End)
    aum_years = aum_by_fh[aum_by_fh['date'].isin(['2022-03-31', '2023-03-31', '2024-03-31', '2025-03-31'])].copy()
    aum_years['year'] = aum_years['date'].apply(lambda x: x.split('-')[0])
    
    plt.figure(figsize=(14, 7))
    # Define custom palette
    colors = sns.color_palette("Blues_d", n_colors=4)
    # Grouped bar chart: X = fund_house, Y = aum_lakh_crore, hue = year
    ax2 = sns.barplot(
        data=aum_years, 
        x="fund_house", 
        y="aum_lakh_crore", 
        hue="year",
        palette="viridis"
    )
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.title("AUM Growth by Fund House (FY22 - FY25)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Fund House", fontsize=12)
    plt.ylabel("AUM (Lakh Crore INR)", fontsize=12)
    
    # Highlight SBI at 12.5L Cr in 2025
    # Find the bar for SBI in 2025 to annotate
    sbi_aum_2025 = 12.50
    plt.annotate(
        f"SBI Dominance: ₹12.5L Cr\n(FY25)", 
        xy=(0.2, 12.5), 
        xytext=(1.5, 11.5),
        arrowprops=dict(facecolor='darkred', shrink=0.05, width=1.5, headwidth=8),
        fontsize=11, fontweight='bold', color='darkred',
        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3, ec="darkred")
    )
    
    # Highlight SBI's bar specifically
    plt.tight_layout()
    plt.savefig(images_dir / "02_aum_growth.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 3: SIP inflow time-series (Plotly)
    # -------------------------------------------------------------
    print("Generating Task 3: SIP Inflow Time-Series...")
    monthly_sip['date'] = pd.to_datetime(monthly_sip['month'] + "-01")
    
    # Create Plotly figure
    fig3 = px.line(
        monthly_sip, 
        x="date", 
        y="sip_inflow_crore", 
        title="<b>Monthly SIP Inflow Trend (Jan 2022 - Dec 2025)</b>",
        labels={"sip_inflow_crore": "SIP Inflow (Crore INR)", "date": "Month"},
        template="plotly_white"
    )
    fig3.update_traces(line=dict(color="#1a5f7a", width=3))
    
    # Annotate the all-time high in Dec 2025
    fig3.add_annotation(
        x="2025-12-01",
        y=31002,
        text="<b>All-Time High</b><br>Dec 2025: ₹31,002 Cr",
        showarrow=True,
        arrowhead=2,
        ax=-80,
        ay=-40,
        bgcolor="rgba(26, 95, 122, 0.9)",
        font=dict(color="white", size=11),
        bordercolor="#1a5f7a",
        borderwidth=1,
        borderpad=4
    )
    
    fig3.update_layout(
        height=450,
        margin=dict(l=60, r=40, t=60, b=40)
    )
    fig3.write_html(str(images_dir / "03_sip_inflow_timeseries.html"))
    
    # Matplotlib static backup
    plt.figure(figsize=(12, 5))
    plt.plot(monthly_sip['date'], monthly_sip['sip_inflow_crore'], color="#1a5f7a", linewidth=3, marker='o', markersize=4)
    plt.title("Monthly SIP Inflow Trend (Jan 2022 - Dec 2025)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("SIP Inflow (Crore INR)", fontsize=12)
    plt.annotate(
        "All-Time High\nDec 2025: ₹31,002 Cr", 
        xy=(pd.to_datetime("2025-12-01"), 31002), 
        xytext=(pd.to_datetime("2024-06-01"), 28000),
        arrowprops=dict(facecolor='#1a5f7a', shrink=0.08, width=1.5, headwidth=8),
        fontsize=11, fontweight='bold', color='#1a5f7a',
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec="#1a5f7a")
    )
    plt.tight_layout()
    plt.savefig(images_dir / "03_sip_inflow_timeseries.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 4: Category inflow heatmap (Seaborn)
    # -------------------------------------------------------------
    print("Generating Task 4: Category Inflow Heatmap...")
    # Pivot the category inflow data
    cat_pivot = category_inflows.pivot(index='category', columns='month', values='net_inflow_crore')
    
    # Sort months chronologically
    cat_pivot = cat_pivot[sorted(cat_pivot.columns)]
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(
        cat_pivot, 
        cmap="RdYlGn", 
        annot=True, 
        fmt=".0f", 
        linewidths=0.5,
        cbar_kws={'label': 'Net Inflow (Crore INR)'},
        center=0
    )
    plt.title("Net Inflow by Fund Category (April 2024 - March 2025)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Fund Category", fontsize=12)
    plt.tight_layout()
    plt.savefig(images_dir / "04_category_inflow_heatmap.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 5: Investor demographics (Matplotlib/Seaborn multi-panel)
    # -------------------------------------------------------------
    print("Generating Task 5: Investor Demographics...")
    # Get unique investors for Age and Gender
    unique_inv = transactions.drop_duplicates(subset=['investor_id'])
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Panel A: Age Group Pie Chart
    age_dist = unique_inv['age_group'].value_counts().sort_index()
    axes[0].pie(
        age_dist, 
        labels=age_dist.index, 
        autopct='%1.1f%%', 
        startangle=140,
        colors=sns.color_palette("pastel"),
        wedgeprops=dict(width=0.6, edgecolor='white') # Donut look
    )
    axes[0].set_title("Age Group Distribution (Unique Investors)", fontsize=12, fontweight='bold')
    
    # Panel B: Gender Split Donut Chart
    gender_dist = unique_inv['gender'].value_counts()
    axes[1].pie(
        gender_dist, 
        labels=gender_dist.index, 
        autopct='%1.1f%%', 
        startangle=90,
        colors=['#3498db', '#e74c3c'],
        wedgeprops=dict(width=0.6, edgecolor='white')
    )
    axes[1].set_title("Gender Split (Unique Investors)", fontsize=12, fontweight='bold')
    
    # Panel C: SIP amount box plot by age group
    sip_transactions = transactions[transactions['transaction_type'] == 'SIP']
    sns.boxplot(
        data=sip_transactions,
        x="age_group",
        y="amount_inr",
        order=sorted(sip_transactions['age_group'].unique()),
        ax=axes[2],
        palette="Set2"
    )
    axes[2].set_title("SIP Transaction Amount by Age Group", fontsize=12, fontweight='bold')
    axes[2].set_xlabel("Age Group", fontsize=10)
    axes[2].set_ylabel("SIP Amount (INR)", fontsize=10)
    
    plt.suptitle("Investor Demographics & Transaction Behavior", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(images_dir / "05_investor_demographics.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 6: Geographic distribution (Matplotlib/Seaborn multi-panel)
    # -------------------------------------------------------------
    print("Generating Task 6: Geographic Distribution...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # SIP transactions
    sip_trans = transactions[transactions['transaction_type'] == 'SIP']
    
    # Panel A: Horizontal Bar of SIP Amount by State
    state_sip = sip_trans.groupby('state')['amount_inr'].sum().sort_values(ascending=False).reset_index()
    # Convert amounts to Crores for readability
    state_sip['amount_crore'] = state_sip['amount_inr'] / 1e7
    
    sns.barplot(
        data=state_sip,
        y="state",
        x="amount_crore",
        ax=axes[0],
        palette="viridis"
    )
    axes[0].set_title("Total SIP Inflow by State (Crore INR)", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Total SIP Amount (Crore INR)", fontsize=10)
    axes[0].set_ylabel("State", fontsize=10)
    
    # Panel B: T30 vs B30 city tier pie chart
    tier_sip = sip_trans.groupby('city_tier')['amount_inr'].sum()
    axes[1].pie(
        tier_sip,
        labels=tier_sip.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=['#2ecc71', '#e67e22'],
        wedgeprops=dict(width=0.6, edgecolor='white')
    )
    axes[1].set_title("City Tier Contribution (T30 vs B30 SIP Inflow)", fontsize=12, fontweight='bold')
    
    plt.suptitle("Geographic Distribution of Mutual Fund SIP Inflows", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(images_dir / "06_geographic_distribution.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 7: Folio count growth (Line chart with milestones)
    # -------------------------------------------------------------
    print("Generating Task 7: Folio Count Growth...")
    folio_count['date'] = pd.to_datetime(folio_count['month'] + "-01")
    folio_count = folio_count.sort_values('date')
    
    plt.figure(figsize=(12, 6))
    plt.plot(folio_count['date'], folio_count['total_folios_crore'], color="#9b59b6", linewidth=3, marker='o', markersize=6, label="Total Folios")
    plt.plot(folio_count['date'], folio_count['equity_folios_crore'], color="#3498db", linestyle="--", linewidth=2, label="Equity Folios")
    
    # Annotate key milestones
    # Jan 2022: 13.26 Cr
    plt.plot(pd.to_datetime("2022-01-01"), 13.26, 'ro', markersize=8)
    plt.annotate("Start: 13.26 Cr\n(Jan 2022)", xy=(pd.to_datetime("2022-01-01"), 13.26), xytext=(pd.to_datetime("2022-04-01"), 12.5),
                 arrowprops=dict(arrowstyle="->", color='red'))
                 
    # Apr 2023: 15.54 Cr
    plt.plot(pd.to_datetime("2023-04-01"), 15.54, 'ro', markersize=8)
    plt.annotate("Milestone: 15 Cr+\n(Apr 2023)", xy=(pd.to_datetime("2023-04-01"), 15.54), xytext=(pd.to_datetime("2023-01-01"), 17.5),
                 arrowprops=dict(arrowstyle="->", color='red'))
                 
    # Oct 2024: 21.62 Cr
    plt.plot(pd.to_datetime("2024-10-01"), 21.62, 'ro', markersize=8)
    plt.annotate("Milestone: 20 Cr+\n(Oct 2024)", xy=(pd.to_datetime("2024-10-01"), 21.62), xytext=(pd.to_datetime("2024-04-01"), 23.5),
                 arrowprops=dict(arrowstyle="->", color='red'))
                 
    # Dec 2025: 26.12 Cr
    plt.plot(pd.to_datetime("2025-12-01"), 26.12, 'ro', markersize=8)
    plt.annotate("End: 26.12 Cr\n(Dec 2025)", xy=(pd.to_datetime("2025-12-01"), 26.12), xytext=(pd.to_datetime("2025-04-01"), 26.5),
                 arrowprops=dict(arrowstyle="->", color='red'))
                 
    plt.title("Industry Folio Count Growth Trend (Jan 2022 - Dec 2025)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Folio Count (Crore)", fontsize=12)
    plt.legend(loc="upper left")
    plt.ylim(8, 29)
    plt.tight_layout()
    plt.savefig(images_dir / "07_folio_growth.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 8: NAV return correlation matrix (Seaborn heatmap)
    # -------------------------------------------------------------
    print("Generating Task 8: NAV Return Correlation Matrix...")
    nav_history['date'] = pd.to_datetime(nav_history['date'])
    nav_merged = pd.merge(nav_history, fund_master[['amfi_code', 'scheme_name', 'category']], on='amfi_code')
    
    # Let's select 10 schemes from different categories to show high correlation among equity funds and low correlation with liquid funds.
    selected_amfi_codes = [
        119551,  # SBI Bluechip Fund - Regular (Equity Large Cap)
        119598,  # SBI Small Cap Fund - Regular (Equity Small Cap)
        119092,  # HDFC Top 100 Fund - Regular (Equity Large Cap)
        118636,  # Kotak Emerging Equity Scheme - Regular (Equity Mid Cap)
        119775,  # Nippon India Small Cap Fund - Regular (Equity Small Cap)
        148567,  # ABSL Frontline Equity Fund - Regular (Equity Large Cap)
        119552,  # SBI Bluechip Fund - Direct (Equity Large Cap)
        119030,  # ICICI Prudential Bluechip Fund - Regular (Equity Large Cap)
        # Add a couple of Debt/Liquid/Benchmark indexes for contrast
        119515,  # SBI Liquid Fund - Regular (Debt Liquid)
        125497   # SBI Small Cap Fund - Direct (Equity Small Cap)
    ]
    
    # Check if these codes exist, filter and pivot
    available_data = nav_merged[nav_merged['amfi_code'].isin(selected_amfi_codes)]
    pivot_nav = available_data.pivot(index='date', columns='scheme_name', values='nav')
    pivot_nav = pivot_nav.sort_index()
    
    # Compute daily returns
    returns = pivot_nav.pct_change().dropna()
    
    # Compute correlation matrix
    corr = returns.corr()
    
    # Let's shorten scheme names for readability in heatmap labels
    short_names = {name: name.split(" - ")[0][:25] for name in corr.columns}
    corr_renamed = corr.rename(index=short_names, columns=short_names)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr_renamed, 
        cmap="coolwarm", 
        annot=True, 
        fmt=".2f", 
        linewidths=0.5,
        cbar_kws={'label': 'Correlation Coefficient'}
    )
    plt.title("Daily NAV Return Correlation Matrix (Selected 10 Funds)", fontsize=14, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.savefig(images_dir / "08_nav_correlation_matrix.png", dpi=150)
    plt.close()
    
    # -------------------------------------------------------------
    # Task 9: Sector allocation donut
    # -------------------------------------------------------------
    print("Generating Task 9: Sector Allocation Donut...")
    # Merge holdings with fund master to filter equity funds
    holdings_merged = pd.merge(portfolio_holdings, fund_master[['amfi_code', 'category']], on='amfi_code')
    equity_holdings = holdings_merged[holdings_merged['category'] == 'Equity']
    
    # Aggregate weights by sector (sum of market_value_cr)
    sector_mv = equity_holdings.groupby('sector')['market_value_cr'].sum().reset_index()
    sector_mv['weight_pct'] = (sector_mv['market_value_cr'] / sector_mv['market_value_cr'].sum()) * 100
    sector_mv = sector_mv.sort_values('weight_pct', ascending=False)
    
    # Donut chart
    plt.figure(figsize=(10, 8))
    # Combine smaller sectors into 'Others' if needed, or keep top 8 and put rest in others
    top_n = 7
    top_sectors = sector_mv.iloc[:top_n].copy()
    others_mv = sector_mv.iloc[top_n:]['market_value_cr'].sum()
    others_weight = sector_mv.iloc[top_n:]['weight_pct'].sum()
    
    # Create rows to concat using pd.DataFrame
    others_df = pd.DataFrame([{'sector': 'Others', 'market_value_cr': others_mv, 'weight_pct': others_weight}])
    donut_data = pd.concat([top_sectors, others_df], ignore_index=True)
    
    plt.pie(
        donut_data['weight_pct'], 
        labels=donut_data['sector'], 
        autopct='%1.1f%%', 
        startangle=140,
        colors=sns.color_palette("Set3", len(donut_data)),
        wedgeprops=dict(width=0.4, edgecolor='white') # Donut width
    )
    plt.title("Aggregated Sector Allocation Across Equity Mutual Funds", fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(images_dir / "09_sector_allocation.png", dpi=150)
    plt.close()
    
    print("All EDA assets generated successfully!")

if __name__ == "__main__":
    generate_eda_assets()
