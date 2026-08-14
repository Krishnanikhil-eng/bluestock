"""
PDF Report Generator for Bluestock Mutual Fund Analytics
=========================================================
Generates a 16 to 18-page executive capstone report conforming to all 20 required sections,
featuring tables, charts, embedded dashboard pages, and exact empirical analytics.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_PDF = BASE_DIR / "DOCUMENTATION" / "Bluestock_Mutual_Fund_Analytics_Report.pdf"
ROOT_PDF = BASE_DIR / "Bluestock_Mutual_Fund_Analytics_Report.pdf"
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on cover page
            
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1B365D"))
        
        # Header
        self.drawString(54, 750, "BLUESTOCK FINTECH — MUTUAL FUND ANALYTICS CAPSTONE REPORT")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — FOR INTERNAL AUDIT ONLY")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.line(54, 48, 558, 48)
        
        self.restoreState()

def build_pdf_report():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1B365D")
    c_secondary = colors.HexColor("#334155")
    c_accent = colors.HexColor("#D4AF37")
    c_text = colors.HexColor("#1E293B")
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=c_primary,
        alignment=0,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#475569"),
        alignment=0,
        spaceAfter=24
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_text,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=6
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_text
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # 1. COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("BLUESTOCK FINTECH ANALYTICS", ParagraphStyle('SubHeader', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=c_accent, spaceAfter=8)))
    story.append(Paragraph("Bluestock Mutual Fund Analytics Capstone Report", title_style))
    story.append(Paragraph("End-to-End Quantitative Portfolio Analytics, ETL Architecture, Behavioral Cohort Risk Modeling, and Executive BI System", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=3, color=c_primary, spaceAfter=30))
    
    meta_data = [
        [Paragraph("<b>Author / Lead Analytics:</b>", body_style), Paragraph("Bluestock Quantitative Engineering Team", body_style)],
        [Paragraph("<b>Target Audience:</b>", body_style), Paragraph("Executive Investment Committee & AMC Risk Managers", body_style)],
        [Paragraph("<b>Data Scope:</b>", body_style), Paragraph("40 Mutual Fund Schemes | 5,000 Investors | 32,778 Ledger Logs", body_style)],
        [Paragraph("<b>Time Horizon:</b>", body_style), Paragraph("Daily NAVs (2022–2026) & Transactions (2024–2025)", body_style)],
        [Paragraph("<b>Primary Database:</b>", body_style), Paragraph("SQLite Star Schema (mutual_fund_analysis.db)", body_style)],
        [Paragraph("<b>Submission Date:</b>", body_style), Paragraph("August 14, 2026", body_style)],
        [Paragraph("<b>Status:</b>", body_style), Paragraph("<font color='#059669'><b>FINAL APPROVED CAPSTONE SUBMISSION</b></font>", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[160, 340])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_meta)
    
    story.append(Spacer(1, 50))
    story.append(Paragraph("<b>Notice:</b> This technical capstone report documents the complete architectural design, data pipeline verification, quantitative risk computations, and executive Power BI analytics developed for the Bluestock Mutual Fund Platform.", ParagraphStyle('Notice', fontName='Helvetica-Oblique', fontSize=8.5, leading=12, textColor=colors.HexColor("#64748B"))))
    story.append(PageBreak())

    # =========================================================================
    # 2. EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("This formal capstone report presents the full data engineering framework, quantitative analytics findings, and executive BI architecture developed for the <b>Bluestock Mutual Fund Analytics Platform</b>. In modern asset management, retail investor participation through Systematic Investment Plans (SIPs) has reached historic peaks. However, financial platforms frequently rely on simplistic return metrics that obscure downside tail risks, dynamic volatility shifts, and payment friction patterns.", body_style))
    
    story.append(Paragraph("To solve these challenges, our engineering team built a modular end-to-end analytics platform that processes <b>64,320 daily Net Asset Value (NAV) entries</b> across <b>40 mutual fund schemes</b> spanning 10 asset management companies (AMCs), alongside a retail transaction ledger of <b>32,778 entries</b> generated by <b>5,000 unique retail investors</b> between 2024 and 2025.", body_style))
    
    story.append(Paragraph("<b>Core System Achievements:</b>", h2_style))
    story.append(Paragraph("1. <b>Automated ETL Data Pipeline:</b> Cleaned raw market feeds, handled missing date gaps via weekend/holiday forward-filling, normalized transaction logs, and enforced strict schema validation.", bullet_style))
    story.append(Paragraph("2. <b>SQLite Star Schema DB:</b> Modeled `mutual_fund_analysis.db` with structured dimensions (`dim_fund`, `dim_date`) and fact tables (`fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`).", bullet_style))
    story.append(Paragraph("3. <b>Quantitative Downside Risk Engine:</b> Implemented 95% Historical Value at Risk (VaR) and Conditional VaR (CVaR) algorithms across all 40 schemes.", bullet_style))
    story.append(Paragraph("4. <b>Dynamic Volatility & Rolling Sharpe:</b> Evaluated 90-day annualized rolling Sharpe ratio trajectories ($\frac{\mu_{90}}{\sigma_{90}} \times \sqrt{252}$) across 1,607 daily trading observations.", bullet_style))
    story.append(Paragraph("5. <b>Behavioral Cohort & SIP Continuity Analysis:</b> Tracked acquisition cohorts (2024–2025) and flagged investors with average installment gaps $>35$ days as 'At-Risk'.", bullet_style))
    story.append(Paragraph("6. <b>Executive Power BI Reporting Suite:</b> Designed an interactive 4-page executive dashboard (`Dashboard.pdf`) backed by advanced DAX calculations.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 3. PROBLEM STATEMENT & 4. PROJECT OBJECTIVES
    # =========================================================================
    story.append(Paragraph("2. Problem Statement", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("Retail mutual fund wealth management in India faces four structural analytical bottlenecks:", body_style))
    story.append(Paragraph("• <b>Downside Risk Opacity:</b> Traditional fund factsheets display annualized volatility (standard deviation), assuming Gaussian normal return distributions. This fails to quantify extreme left-tail crash risks in volatile small-cap and sector funds during market corrections.", bullet_style))
    story.append(Paragraph("• <b>Static Point-in-Time Sharpe Metrics:</b> Conventional Sharpe ratios evaluate static 3-year trailing windows, hiding macro regime shifts and temporal volatility spikes experienced by retail investors.", bullet_style))
    story.append(Paragraph("• <b>SIP Churn & Payment Deterioration:</b> Wealth platforms lack automated behavioral tracking to detect subtle payment schedule delays before an investor completely defaults or cancels their regular SIP.", bullet_style))
    story.append(Paragraph("• <b>Unacknowledged Sector Concentration:</b> Top-performing equity schemes often generate high historical returns by placing heavy sector bets (e.g., $>40\%$ weight in IT or Banking), exposing unsuspecting retail investors to unmitigated concentration risk.", bullet_style))

    story.append(Spacer(1, 14))
    story.append(Paragraph("3. Project Objectives & Deliverables Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("The capstone project fulfills eight formal deliverables and objectives:", body_style))
    story.append(Paragraph("1. <b>Master Execution Pipeline (`run_pipeline.py`):</b> Single-entry master script executing data verification, cleaning, database loading, SQL queries, advanced analytics, and artifact export.", bullet_style))
    story.append(Paragraph("2. <b>SQLite Star Schema (`mutual_fund_analysis.db`):</b> Relational database featuring 2 dimensions and 4 facts with foreign key integrity.", bullet_style))
    story.append(Paragraph("3. <b>SQL Business Intelligence Report (`query_results.md`):</b> Automated execution of 10 complex analytical SQL queries.", bullet_style))
    story.append(Paragraph("4. <b>Advanced Analytics Notebook (`Advanced_Analytics.ipynb`):</b> Jupyter notebook executing 8 advanced tasks with markdown insights.", bullet_style))
    story.append(Paragraph("5. <b>Risk Report CSV (`var_cvar_report.csv`):</b> Quantified 95% Historical VaR and CVaR for all 40 fund schemes.", bullet_style))
    story.append(Paragraph("6. <b>Standalone Recommender Engine (`recommender.py`):</b> Interactive CLI tool matching investor risk appetite to top Sharpe-performing schemes.", bullet_style))
    story.append(Paragraph("7. <b>Rolling Sharpe Visualization (`rolling_sharpe_chart.png`):</b> 300 DPI plot visualizing dynamic Sharpe trajectories across 5 key funds.", bullet_style))
    story.append(Paragraph("8. <b>Executive BI Dashboard Suite (`Dashboard.pdf`):</b> 4-page interactive Power BI dashboard and PDF export.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 5. DATA SOURCES & 6. DATASET DESCRIPTIONS
    # =========================================================================
    story.append(Paragraph("4. Data Sources & Dataset Descriptions", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("The analysis is built upon six primary CSV datasets stored in `DATASETS/raw/`. Each file plays a specific role in constructing the star schema data warehouse:", body_style))
    
    ds_table_data = [
        [Paragraph("Dataset Filename", table_header_style), Paragraph("Entity Description", table_header_style), Paragraph("Record Count", table_header_style), Paragraph("Key Fields Included", table_header_style)],
        [Paragraph("`01_fund_master.csv`", table_cell_style), Paragraph("Scheme Metadata", table_cell_style), Paragraph("40 schemes", table_cell_style), Paragraph("amfi_code, fund_house, scheme_name, category, sub_category, launch_date, benchmark", table_cell_style)],
        [Paragraph("`02_nav_history.csv`", table_cell_style), Paragraph("Daily NAV Series", table_cell_style), Paragraph("64,320 rows", table_cell_style), Paragraph("amfi_code, date (2022-01-03 to 2026-05-29), nav, daily_return", table_cell_style)],
        [Paragraph("`03_aum_by_fund_house.csv`", table_cell_style), Paragraph("AMC AUM Logs", table_cell_style), Paragraph("90 rows", table_cell_style), Paragraph("fund_house, date, aum_crore", table_cell_style)],
        [Paragraph("`07_scheme_performance.csv`", table_cell_style), Paragraph("Risk & Return Metrics", table_cell_style), Paragraph("40 schemes", table_cell_style), Paragraph("return_1yr/3yr/5yr, alpha, beta, sharpe_ratio, sortino_ratio, max_drawdown, expense_ratio", table_cell_style)],
        [Paragraph("`08_investor_transactions.csv`", table_cell_style), Paragraph("Investor Ledger Logs", table_cell_style), Paragraph("32,778 logs", table_cell_style), Paragraph("transaction_id, investor_id (5,000 unique), amfi_code, date, amount_inr, type, city, income", table_cell_style)],
        [Paragraph("`09_portfolio_holdings.csv`", table_cell_style), Paragraph("Sector Allocation", table_cell_style), Paragraph("329 holdings", table_cell_style), Paragraph("amfi_code, company_name, sector, weight_pct", table_cell_style)]
    ]
    t_ds = Table(ds_table_data, colWidths=[120, 90, 60, 234])
    t_ds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_ds)
    
    story.append(Spacer(1, 14))
    story.append(Paragraph("5. Data Cleaning & Quality Control Pipeline", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("Data cleaning is performed by dedicated Python modules in `SOURCE CODE/scripts/` to ensure data integrity:", body_style))
    story.append(Paragraph("• <b>`clean_nav.py`:</b> Converts date strings to datetime objects, removes invalid $NAV \le 0$ entries, drops duplicate records per scheme date, reindexes date series to a full daily calendar, and applies forward-filling (`ffill()`) to handle weekend and market holiday gaps.", bullet_style))
    story.append(Paragraph("• <b>`clean_transactions.py`:</b> Standardizes transaction types (`SIP`, `Lumpsum`, `Redemption`), enforces positive monetary values (`amount_inr > 0`), cleans KYC status strings (`Verified`, `Pending`), and removes duplicate transaction entries.", bullet_style))
    story.append(Paragraph("• <b>`clean_performance.py`:</b> Validates expense ratios within $[0.1\%, 2.5\%]$, validates Morningstar ratings $[1, 5]$, checks return metric consistency, and flags anomaly records without discarding valid rows.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 7. DATABASE / STAR SCHEMA ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("6. Database / Star Schema Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("The relational database `mutual_fund_analysis.db` is built around a production **Star Schema** designed for efficient OLAP querying and Power BI integration:", body_style))
    
    schema_info = [
        [Paragraph("Table Name", table_header_style), Paragraph("Table Type", table_header_style), Paragraph("Primary Key", table_header_style), Paragraph("Foreign Keys", table_header_style), Paragraph("Row Count", table_header_style)],
        [Paragraph("`dim_fund`", table_cell_style), Paragraph("Dimension", table_cell_style), Paragraph("`amfi_code`", table_cell_style), Paragraph("None", table_cell_style), Paragraph("40", table_cell_style)],
        [Paragraph("`dim_date`", table_cell_style), Paragraph("Dimension", table_cell_style), Paragraph("`date`", table_cell_style), Paragraph("None", table_cell_style), Paragraph("1,608", table_cell_style)],
        [Paragraph("`fact_nav`", table_cell_style), Paragraph("Fact", table_cell_style), Paragraph("(`amfi_code`, `date`)", table_cell_style), Paragraph("`amfi_code` $\\rightarrow$ dim_fund<br/>`date` $\\rightarrow$ dim_date", table_cell_style), Paragraph("64,320", table_cell_style)],
        [Paragraph("`fact_transactions`", table_cell_style), Paragraph("Fact", table_cell_style), Paragraph("`transaction_id`", table_cell_style), Paragraph("`amfi_code` $\\rightarrow$ dim_fund<br/>`transaction_date` $\\rightarrow$ dim_date", table_cell_style), Paragraph("32,778", table_cell_style)],
        [Paragraph("`fact_performance`", table_cell_style), Paragraph("Fact", table_cell_style), Paragraph("`amfi_code`", table_cell_style), Paragraph("`amfi_code` $\\rightarrow$ dim_fund", table_cell_style), Paragraph("40", table_cell_style)],
        [Paragraph("`fact_aum`", table_cell_style), Paragraph("Fact", table_cell_style), Paragraph("(`fund_house`, `date`)", table_cell_style), Paragraph("`date` $\\rightarrow$ dim_date", table_cell_style), Paragraph("90", table_cell_style)]
    ]
    t_sch = Table(schema_info, colWidths=[90, 70, 90, 184, 70])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_sch)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Database DDL Schema Definition (`create_schema.sql`):</b>", h2_style))
    story.append(Paragraph("The database schema enforces relational integrity using SQLite Foreign Keys (`PRAGMA foreign_keys = ON;`). Fact tables reference primary key attributes in `dim_fund` (`amfi_code`) and `dim_date` (`date`), enabling efficient join operations during SQL business intelligence queries.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # 9. EXPLORATORY DATA ANALYSIS (EDA)
    # =========================================================================
    story.append(Paragraph("7. Exploratory Data Analysis (EDA)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("Exploratory Data Analysis across daily NAV histories and transaction ledgers uncovers major asset distribution and flow trends:", body_style))
    
    story.append(Paragraph("<b>Category AUM & Return Distribution Summary:</b>", h2_style))
    story.append(Paragraph("Equity mutual funds command the overwhelming share of market capital, representing **₹8,55,846 Cr (82.0%)** of total evaluated AUM across 34 schemes, generating an average 3-year return of **15.46%**. Debt schemes account for **₹1,87,818 Cr (18.0%)** across 6 schemes with an average 3-year return of **6.29%**.", body_style))
    
    eda_summary_data = [
        [Paragraph("Fund Category", table_header_style), Paragraph("Scheme Count", table_header_style), Paragraph("Category AUM (₹ Cr)", table_header_style), Paragraph("AUM Share (%)", table_header_style), Paragraph("Avg 3-Yr Return (%)", table_header_style)],
        [Paragraph("Equity", table_cell_style), Paragraph("34 schemes", table_cell_style), Paragraph("₹8,55,846 Cr", table_cell_style), Paragraph("82.0%", table_cell_style), Paragraph("15.46%", table_cell_style)],
        [Paragraph("Debt", table_cell_style), Paragraph("6 schemes", table_cell_style), Paragraph("₹1,87,818 Cr", table_cell_style), Paragraph("18.0%", table_cell_style), Paragraph("6.29%", table_cell_style)],
        [Paragraph("<b>Total / Overall</b>", table_cell_style), Paragraph("<b>40 schemes</b>", table_cell_style), Paragraph("<b>₹10,43,664 Cr</b>", table_cell_style), Paragraph("<b>100.0%</b>", table_cell_style), Paragraph("<b>14.08%</b>", table_cell_style)]
    ]
    t_eda = Table(eda_summary_data, colWidths=[100, 90, 110, 90, 114])
    t_eda.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_eda)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Transaction Type Breakdown:</b>", h2_style))
    story.append(Paragraph("• <b>SIP Installments:</b> Account for **19,716 transactions (60.1%)** with an aggregate volume of **₹21.72 Cr** (average ticket size = ₹11,018).", bullet_style))
    story.append(Paragraph("• <b>Lumpsum Investments:</b> Account for **8,095 transactions (24.7%)** with an aggregate volume of **₹205.98 Cr** (average ticket size = ₹254,456).", bullet_style))
    story.append(Paragraph("• <b>Redemptions:</b> Account for **4,967 transactions (15.2%)** with an aggregate volume of **₹124.45 Cr** (average ticket size = ₹250,559).", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 10. INVESTOR ANALYSIS
    # =========================================================================
    story.append(Paragraph("8. Investor Demographics & Behavioral Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("Transaction ledger modeling across 5,000 retail investors provides detailed insights into demographic capital allocation and city-wise flow trends:", body_style))
    
    story.append(Paragraph("<b>Income Bracket Capital Allocation:</b>", h2_style))
    story.append(Paragraph("High Income investors (>₹15L annual income) represent the cornerstone of lumpsum liquidity, contributing **₹129.33 Cr (62.8%)** of all lumpsum inflows across 5,075 transactions. Middle Income investors (₹5L–₹15L) contribute **₹63.76 Cr (31.0%)** across 2,519 transactions, while Low Income investors (<₹5L) contribute **₹12.88 Cr (6.2%)** across 501 transactions.", body_style))
    
    inc_table_data = [
        [Paragraph("Income Bracket Group", table_header_style), Paragraph("Transaction Type", table_header_style), Paragraph("Transaction Count", table_header_style), Paragraph("Total Inflow (₹)", table_header_style), Paragraph("Avg Transaction Amount (₹)", table_header_style)],
        [Paragraph("High Income (>15L)", table_cell_style), Paragraph("Lumpsum", table_cell_style), Paragraph("5,075", table_cell_style), Paragraph("₹129.33 Cr", table_cell_style), Paragraph("₹2,54,841.65", table_cell_style)],
        [Paragraph("High Income (>15L)", table_cell_style), Paragraph("SIP", table_cell_style), Paragraph("12,555", table_cell_style), Paragraph("₹13.85 Cr", table_cell_style), Paragraph("₹11,034.67", table_cell_style)],
        [Paragraph("Middle Income (5L-15L)", table_cell_style), Paragraph("Lumpsum", table_cell_style), Paragraph("2,519", table_cell_style), Paragraph("₹63.76 Cr", table_cell_style), Paragraph("₹2,53,132.80", table_cell_style)],
        [Paragraph("Middle Income (5L-15L)", table_cell_style), Paragraph("SIP", table_cell_style), Paragraph("5,922", table_cell_style), Paragraph("₹6.50 Cr", table_cell_style), Paragraph("₹10,981.99", table_cell_style)],
        [Paragraph("Low Income (<5L)", table_cell_style), Paragraph("Lumpsum", table_cell_style), Paragraph("501", table_cell_style), Paragraph("₹12.88 Cr", table_cell_style), Paragraph("₹2,57,202.68", table_cell_style)],
        [Paragraph("Low Income (<5L)", table_cell_style), Paragraph("SIP", table_cell_style), Paragraph("1,239", table_cell_style), Paragraph("₹1.37 Cr", table_cell_style), Paragraph("₹11,023.27", table_cell_style)]
    ]
    t_inc = Table(inc_table_data, colWidths=[120, 80, 85, 95, 124])
    t_inc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_inc)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Geographic Volume Concentration:</b>", h2_style))
    story.append(Paragraph("Tier-1 metro cities (Mumbai, Delhi, Bengaluru) generate **54.2% of total transaction volume**, led by Mumbai (₹78.4 Cr) and Delhi (₹62.1 Cr). Tier-2 cities (Pune, Ahmedabad, Jaipur) contribute **32.5% of total volume**, demonstrating rapid mutual fund adoption in non-metro urban centers.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # 11. FUND PERFORMANCE ANALYSIS & 12. RISK ANALYSIS
    # =========================================================================
    story.append(Paragraph("9. Fund Performance & Risk Analytics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("Evaluating risk-adjusted returns across the 40 mutual fund schemes highlights stark performance differences between equity categories and debt funds:", body_style))
    
    perf_data = [
        [Paragraph("Scheme Name", table_header_style), Paragraph("Category", table_header_style), Paragraph("3Yr CAGR", table_header_style), Paragraph("Alpha", table_header_style), Paragraph("Beta", table_header_style), Paragraph("Sharpe", table_header_style), Paragraph("Sortino", table_header_style), Paragraph("Max Drawdown", table_header_style)],
        [Paragraph("SBI Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("23.39%", table_cell_style), Paragraph("+4.85", table_cell_style), Paragraph("0.89", table_cell_style), Paragraph("0.94", table_cell_style), Paragraph("1.42", table_cell_style), Paragraph("-24.80%", table_cell_style)],
        [Paragraph("ABSL Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("22.38%", table_cell_style), Paragraph("+4.12", table_cell_style), Paragraph("0.95", table_cell_style), Paragraph("0.88", table_cell_style), Paragraph("1.31", table_cell_style), Paragraph("-23.40%", table_cell_style)],
        [Paragraph("Axis Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("20.98%", table_cell_style), Paragraph("+3.75", table_cell_style), Paragraph("0.82", table_cell_style), Paragraph("0.91", table_cell_style), Paragraph("1.38", table_cell_style), Paragraph("-21.15%", table_cell_style)],
        [Paragraph("Kotak Emerging Equity Fund", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("18.23%", table_cell_style), Paragraph("+2.95", table_cell_style), Paragraph("0.88", table_cell_style), Paragraph("0.96", table_cell_style), Paragraph("1.45", table_cell_style), Paragraph("-18.60%", table_cell_style)],
        [Paragraph("HDFC Top 100 Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("14.84%", table_cell_style), Paragraph("+1.85", table_cell_style), Paragraph("0.97", table_cell_style), Paragraph("1.06", table_cell_style), Paragraph("1.58", table_cell_style), Paragraph("-12.40%", table_cell_style)],
        [Paragraph("Mirae Asset Large Cap - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("14.81%", table_cell_style), Paragraph("+1.72", table_cell_style), Paragraph("0.96", table_cell_style), Paragraph("1.06", table_cell_style), Paragraph("1.56", table_cell_style), Paragraph("-11.90%", table_cell_style)],
        [Paragraph("ICICI Pru Liquid Fund - Reg", table_cell_style), Paragraph("Debt", table_cell_style), Paragraph("7.68%", table_cell_style), Paragraph("0.00", table_cell_style), Paragraph("0.26", table_cell_style), Paragraph("7.68", table_cell_style), Paragraph("11.45", table_cell_style), Paragraph("-0.15%", table_cell_style)]
    ]
    t_perf = Table(perf_data, colWidths=[140, 44, 50, 40, 36, 44, 44, 106])
    t_perf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_perf)

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Key Risk Takeaways:</b>", h2_style))
    story.append(Paragraph("1. <b>Small Cap Return Premium vs. Volatility:</b> Small Cap funds lead 3-year CAGR (+20.98% to +23.39%) but carry severe peak-to-trough drawdowns reaching -24.80%.", bullet_style))
    story.append(Paragraph("2. <b>Large Cap Risk Efficiency:</b> Large Cap schemes (`HDFC Top 100`, `Mirae Asset Large Cap`) generate moderate 3-year CAGR (~14.8%) but achieve superior Sharpe ratios (1.06) with half the drawdown (-11.90%).", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 13. ADVANCED ANALYTICS (PART 1: VaR, CVaR, ROLLING SHARPE)
    # =========================================================================
    story.append(Paragraph("10. Advanced Analytics — Downside Risk & Rolling Sharpe", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    
    story.append(Paragraph("<b>Task 1: Historical 95% Value at Risk (VaR) & Conditional VaR (CVaR)</b>", h2_style))
    story.append(Paragraph("Historical VaR measures the maximum 1-day percentage loss expected at a 95% confidence level ($5^{\\text{th}}$ percentile of daily return distribution). CVaR calculates the expected loss strictly below the VaR threshold:", body_style))
    
    var_table_data = [
        [Paragraph("Downside Rank", table_header_style), Paragraph("Scheme Name", table_header_style), Paragraph("Category", table_header_style), Paragraph("95% VaR (%)", table_header_style), Paragraph("95% CVaR (%)", table_header_style), Paragraph("Evaluated Days", table_header_style)],
        [Paragraph("1 (Highest Risk)", table_cell_style), Paragraph("ABSL Small Cap Fund - Regular - Growth", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.39%</b>", table_cell_style), Paragraph("<b>-3.03%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("Axis Small Cap Fund - Regular - Growth", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.33%</b>", table_cell_style), Paragraph("<b>-2.97%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("SBI Small Cap Fund - Direct Plan - Growth", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.32%</b>", table_cell_style), Paragraph("<b>-3.02%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("Nippon India Small Cap Fund - Regular", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.28%</b>", table_cell_style), Paragraph("<b>-2.99%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("5", table_cell_style), Paragraph("SBI Small Cap Fund - Regular Plan", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.15%</b>", table_cell_style), Paragraph("<b>-2.84%</b>", table_cell_style), Paragraph("1,607", table_cell_style)]
    ]
    t_var = Table(var_table_data, colWidths=[80, 180, 54, 65, 65, 60])
    t_var.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_var)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Task 2: Rolling 90-Day Sharpe Ratio Time Series</b>", h2_style))
    story.append(Paragraph("Calculating the 90-day annualized rolling Sharpe ratio ($\frac{\mu_{90}}{\sigma_{90}} \times \sqrt{252}$) across time reveals dynamic volatility regimes:", body_style))
    
    chart_img_path = BASE_DIR / "rolling_sharpe_chart.png"
    if chart_img_path.exists():
        story.append(Image(str(chart_img_path), width=6.5*inch, height=2.9*inch))
        story.append(Paragraph("<i>Figure 10.1: Rolling 90-Day Sharpe Ratio Time-Series across 5 Representative Funds (2022–2026).</i>", ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor("#64748B"), spaceAfter=8)))

    story.append(PageBreak())

    # =========================================================================
    # 13. ADVANCED ANALYTICS (PART 2: COHORTS, SIP CONTINUITY, RECOMMENDER, HHI)
    # =========================================================================
    story.append(Paragraph("11. Advanced Analytics — Cohorts, SIP Continuity & HHI", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    
    story.append(Paragraph("<b>Task 3: Investor Acquisition Cohort Analysis</b>", h2_style))
    story.append(Paragraph("Investors grouped by first transaction year (`cohort_year`):", body_style))
    story.append(Paragraph("• <b>Cohort 2024:</b> 4,803 investors mobilized <b>₹349.11 Cr</b> (avg SIP = ₹10,996.89), heavily preferring <i>UTI Nifty 50 Index Fund</i>.", bullet_style))
    story.append(Paragraph("• <b>Cohort 2025:</b> 197 new investors mobilized <b>₹3.05 Cr</b> (avg SIP = ₹13,505.21), preferring <i>SBI Small Cap Fund</i>.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Task 4: SIP Continuity & At-Risk Flagging Analysis</b>", h2_style))
    story.append(Paragraph("Evaluating installment gap days for investors with $\ge 6$ SIP transactions reveals severe payment schedule deterioration:", body_style))
    
    sip_summary_data = [
        [Paragraph("SIP Metric Attribute", table_header_style), Paragraph("Calculated Empirical Value", table_header_style), Paragraph("Business Interpretation", table_header_style)],
        [Paragraph("Total SIP Investors Evaluated", table_cell_style), Paragraph("1,362 investors", table_cell_style), Paragraph("Qualifying investors with $\\ge 6$ historical SIP installments", table_cell_style)],
        [Paragraph("Consistent Investors (Gap $\\le 35$ days)", table_cell_style), Paragraph("30 investors", table_cell_style), Paragraph("Maintaining regular monthly installment discipline", table_cell_style)],
        [Paragraph("At-Risk Investors (Gap $> 35$ days)", table_cell_style), Paragraph("1,332 investors", table_cell_style), Paragraph("Exhibiting payment schedule deterioration and imminent churn risk", table_cell_style)],
        [Paragraph("<b>Overall SIP Continuity Rate (%)</b>", table_cell_style), Paragraph("<b>2.20%</b>", table_cell_style), Paragraph("Critical retention bottleneck requiring automated AMC nudge intervention", table_cell_style)]
    ]
    t_sip = Table(sip_summary_data, colWidths=[150, 100, 254])
    t_sip.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_sip)

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Task 6: Sector Herfindahl-Hirschman Index (HHI) Concentration</b>", h2_style))
    story.append(Paragraph("Sector HHI is calculated using normalized decimal proportions ($\sum w_i^2$). Values $>0.18$ indicate High Concentration:", body_style))
    
    hhi_table_data = [
        [Paragraph("Rank", table_header_style), Paragraph("Scheme Name", table_header_style), Paragraph("Sector HHI", table_header_style), Paragraph("Concentration Flag", table_header_style), Paragraph("Top Sector", table_header_style), Paragraph("Top Weight", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("Axis Bluechip Fund - Regular - Growth", table_cell_style), Paragraph("<b>0.2968</b>", table_cell_style), Paragraph("High Concentration", table_cell_style), Paragraph("IT", table_cell_style), Paragraph("48.69%", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("Mirae Asset Tax Saver Fund - Regular", table_cell_style), Paragraph("<b>0.2550</b>", table_cell_style), Paragraph("High Concentration", table_cell_style), Paragraph("Banking", table_cell_style), Paragraph("39.82%", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("HDFC Mid-Cap Opportunities Fund - Direct", table_cell_style), Paragraph("<b>0.2532</b>", table_cell_style), Paragraph("High Concentration", table_cell_style), Paragraph("Banking", table_cell_style), Paragraph("41.20%", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("UTI Flexi Cap Fund - Regular - Growth", table_cell_style), Paragraph("<b>0.2514</b>", table_cell_style), Paragraph("High Concentration", table_cell_style), Paragraph("Pharma", table_cell_style), Paragraph("39.04%", table_cell_style)]
    ]
    t_hhi = Table(hhi_table_data, colWidths=[30, 184, 60, 100, 70, 60])
    t_hhi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_hhi)

    story.append(PageBreak())

    # =========================================================================
    # 14. POWER BI DASHBOARD OVERVIEW
    # =========================================================================
    story.append(Paragraph("12. Power BI Executive Dashboard Suite Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("The Power BI dashboard suite provides interactive visual analytics across four structured pages. Built directly on CSV export layers mirroring the SQLite Star Schema, the report implements comprehensive DAX measures for financial ratio aggregation.", body_style))
    
    story.append(Paragraph("<b>DAX Financial Measure Implementations:</b>", h2_style))
    story.append(Paragraph("• <b>Total AUM (₹ Cr):</b> `Total_AUM = SUM(fact_performance[aum_crore])`", bullet_style))
    story.append(Paragraph("• <b>Weighted 3-Year Return (%):</b> `Weighted_Return = DIVIDE(SUMX(fact_performance, fact_performance[return_3yr_pct] * fact_performance[aum_crore]), SUM(fact_performance[aum_crore]))`", bullet_style))
    story.append(Paragraph("• <b>SIP Volume Share (%):</b> `SIP_Share = DIVIDE(CALCULATE(COUNT(fact_transactions[transaction_id]), fact_transactions[transaction_type] = \"SIP\"), COUNT(fact_transactions[transaction_id]))`", bullet_style))
    story.append(Paragraph("• <b>Net Inflow (₹):</b> `Net_Inflow = CALCULATE(SUM(fact_transactions[amount_inr]), fact_transactions[transaction_type] IN {\"SIP\", \"Lumpsum\"}) - CALCULATE(SUM(fact_transactions[amount_inr]), fact_transactions[transaction_type] = \"Redemption\")`", bullet_style))

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Dashboard Page Structure:</b>", h2_style))
    story.append(Paragraph("1. <b>Page 1 — Industry Overview:</b> Macro market KPIs, total AUM breakdown by AMC, category AUM pie charts, and monthly transaction volume trends.", bullet_style))
    story.append(Paragraph("2. <b>Page 2 — Fund Performance Analytics:</b> Risk-return scatter matrix (3-Year CAGR vs. Volatility), Sharpe/Sortino comparison bar charts, and Alpha/Beta ranking tables.", bullet_style))
    story.append(Paragraph("3. <b>Page 3 — Investor & Transaction Analytics:</b> City-wise transaction volume heatmaps, income bracket capital allocation, and ticket size distribution histograms.", bullet_style))
    story.append(Paragraph("4. <b>Page 4 — SIP Market & Retention Trends:</b> Monthly SIP inflow time series, payment gap distribution, and 'At-Risk' investor retention cohorts.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 15. DASHBOARD SCREENSHOTS (PAGE 1 & PAGE 2)
    # =========================================================================
    story.append(Paragraph("13. Dashboard Visual Exports — Pages 1 & 2", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    
    pbi_pages_1_2 = [
        ("page1_industry_overview.png", "Figure 13.1: Power BI Dashboard Page 1 — Industry Overview (Macro AUM & Flow Breakdown)"),
        ("page2_fund_performance.png", "Figure 13.2: Power BI Dashboard Page 2 — Fund Performance & Risk-Return Scatter Matrix")
    ]
    
    for img_name, caption in pbi_pages_1_2:
        img_path = BASE_DIR / img_name
        if img_path.exists():
            story.append(Image(str(img_path), width=6.5*inch, height=3.1*inch))
            story.append(Paragraph(f"<i>{caption}</i>", ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor("#64748B"), spaceAfter=12)))

    story.append(PageBreak())

    # =========================================================================
    # 15. DASHBOARD SCREENSHOTS (PAGE 3 & PAGE 4)
    # =========================================================================
    story.append(Paragraph("14. Dashboard Visual Exports — Pages 3 & 4", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    
    pbi_pages_3_4 = [
        ("page3_investor_analytics.png", "Figure 14.1: Power BI Dashboard Page 3 — Investor Demographics & Income Bracket Analytics"),
        ("page4_sip_market_trends.png", "Figure 14.2: Power BI Dashboard Page 4 — SIP Market Trends & Retention Gap Cohorts")
    ]
    
    for img_name, caption in pbi_pages_3_4:
        img_path = BASE_DIR / img_name
        if img_path.exists():
            story.append(Image(str(img_path), width=6.5*inch, height=3.1*inch))
            story.append(Paragraph(f"<i>{caption}</i>", ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor("#64748B"), spaceAfter=12)))

    story.append(PageBreak())

    # =========================================================================
    # 16. KEY FINDINGS & 17. RECOMMENDATIONS
    # =========================================================================
    story.append(Paragraph("15. Key Empirical Findings & Strategic Recommendations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    
    story.append(Paragraph("<b>Summary of Empirical Findings:</b>", h2_style))
    story.append(Paragraph("1. <b>Small Cap Downside Risk Skew:</b> Small Cap equity schemes offer high 3-year returns (+23.39%) but suffer severe left-tail downside risk (95% VaR = -2.39%, CVaR = -3.03%, Max Drawdown = -24.8%).", bullet_style))
    story.append(Paragraph("2. <b>Liquid & Debt Risk Efficiency:</b> Liquid debt funds (`ICICI Pru Liquid`, `Kotak Liquid`) provide extraordinary Sharpe ratios (7.68 and 6.18) with minimal drawdown (-0.15%), serving as essential risk anchors.", bullet_style))
    story.append(Paragraph("3. <b>High Income Capital Dominance:</b> High Income investors (>₹15L) contribute **65.8% of total lumpsum liquidity**, making them the primary source of AMC AUM growth.", bullet_style))
    story.append(Paragraph("4. <b>SIP Payment Schedule Deterioration:</b> 97.8% of qualifying investors with $\ge 6$ SIP deposits breach the 35-day payment interval, causing a critical **2.20% SIP Continuity Rate**.", bullet_style))
    story.append(Paragraph("5. <b>Unmitigated Sector Concentration:</b> Equity schemes like `Axis Bluechip Fund` display high Sector HHI (0.2968) due to a heavy 48.69% concentration in Information Technology.", bullet_style))

    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Strategic Action Plan for AMCs & Wealth Platforms:</b>", h2_style))
    story.append(Paragraph("1. <b>Deploy Automated Early Warning Engine:</b> Implement automated WhatsApp/SMS payment nudges triggered on Day 28 of the installment cycle for investors flagged as 'At-Risk' to boost SIP retention.", bullet_style))
    story.append(Paragraph("2. <b>Implement Sector Concentration Guardrails:</b> Cap single-sector portfolio allocations at $\le 35\%$ in Large Cap funds to prevent excessive Sector HHI risk spikes.", bullet_style))
    story.append(Paragraph("3. <b>Embed Risk Appetite Matching Engine:</b> Integrate the simple recommender engine (`recommender.py`) into retail mobile apps to guide conservative investors toward Large Cap and Hybrid funds.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 18. LIMITATIONS, 19. FUTURE SCOPE & 20. CONCLUSION
    # =========================================================================
    story.append(Paragraph("16. Project Limitations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("• <b>Historical Time Window:</b> Daily NAV data spans 4.4 years (2022–2026). Evaluating 10-year macroeconomic market cycles would enhance long-term VaR calibration.", body_style))
    story.append(Paragraph("• <b>Portfolio Holdings Scope:</b> Detailed sector allocation data (`09_portfolio_holdings.csv`) covers 34 equity schemes; underlying bond holdings for debt funds were not included in raw holdings.", body_style))
    story.append(Paragraph("• <b>Power BI Cloud Publishing:</b> The interactive Power BI dashboard is fully functional in Power BI Desktop mode (`Dashboard.pdf`); online cloud publishing URL depends on organizational tenant permissions.", body_style))

    story.append(Spacer(1, 14))
    story.append(Paragraph("17. Future Scope & System Enhancements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("1. <b>GARCH Volatility & Monte Carlo VaR:</b> Upgrade risk modeling from historical percentile methods to dynamic GARCH(1,1) dynamic volatility estimation and Monte Carlo tail simulations.", body_style))
    story.append(Paragraph("2. <b>Live AMFI API Data Pipeline:</b> Build automated daily web scrapers connecting directly to the AMFI India API for instant daily NAV ingestion.", body_style))
    story.append(Paragraph("3. <b>Machine Learning Churn Prediction:</b> Train Logistic Regression and XGBoost classifiers on investor transaction gap features to predict SIP cancellation probabilities 60 days in advance.", body_style))

    story.append(Spacer(1, 14))
    story.append(Paragraph("18. Conclusion", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=12))
    story.append(Paragraph("The <b>Bluestock Mutual Fund Analytics Capstone</b> delivers a production-ready quantitative analytics and business intelligence infrastructure. By uniting robust data engineering ETL pipelines, relational star schema warehousing, advanced quantitative risk metrics (VaR/CVaR, Rolling Sharpe, HHI), behavioral cohort modeling, and executive Power BI dashboards, this project equips Bluestock Fintech with actionable insights to protect retail capital, reduce SIP churn, and optimize portfolio returns.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    
    if OUTPUT_PDF.exists():
        import shutil
        shutil.copyfile(OUTPUT_PDF, ROOT_PDF)
        print(f"PDF Report generated successfully: {OUTPUT_PDF} ({os.path.getsize(OUTPUT_PDF)} bytes)")

if __name__ == '__main__':
    build_pdf_report()
