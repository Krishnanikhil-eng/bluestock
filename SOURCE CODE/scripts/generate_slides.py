"""
12-Slide Presentation PDF Generator for Bluestock Mutual Fund Analytics
========================================================================
Generates a 12-slide widescreen (16:9) executive presentation PDF in
DOCUMENTATION/Bluestock_Mutual_Fund_Analytics_Slides.pdf
"""

import os
import sys
import pandas as pd
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_SLIDES = BASE_DIR / "DOCUMENTATION" / "Bluestock_Mutual_Fund_Analytics_Slides.pdf"
ROOT_SLIDES = BASE_DIR / "Bluestock_Mutual_Fund_Analytics_Slides.pdf"
OUTPUT_SLIDES.parent.mkdir(parents=True, exist_ok=True)

# 16:9 Widescreen Page Dimensions (10 inches by 5.625 inches = 720 x 405 pt)
SLIDE_WIDTH = 10 * inch
SLIDE_HEIGHT = 5.625 * inch

class SlideCanvas(canvas.Canvas):
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
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, page_count):
        self.saveState()
        
        if self._pageNumber == 1:
            # Title slide dark background header accent
            self.setFillColor(colors.HexColor("#1B365D"))
            self.rect(0, SLIDE_HEIGHT - 12, SLIDE_WIDTH, 12, fill=True, stroke=False)
            self.setFillColor(colors.HexColor("#D4AF37"))
            self.rect(0, SLIDE_HEIGHT - 16, SLIDE_WIDTH, 4, fill=True, stroke=False)
            self.restoreState()
            return

        # Running Slide Header Bar
        self.setFillColor(colors.HexColor("#1B365D"))
        self.rect(0, SLIDE_HEIGHT - 38, SLIDE_WIDTH, 38, fill=True, stroke=False)
        self.setFillColor(colors.HexColor("#D4AF37"))
        self.rect(0, SLIDE_HEIGHT - 42, SLIDE_WIDTH, 4, fill=True, stroke=False)
        
        # Header Text
        self.setFont("Helvetica-Bold", 10)
        self.setFillColor(colors.white)
        self.drawString(36, SLIDE_HEIGHT - 26, "BLUESTOCK MUTUAL FUND ANALYTICS")
        
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#CBD5E1"))
        self.drawRightString(SLIDE_WIDTH - 36, SLIDE_HEIGHT - 26, "EXECUTIVE PRESENTATION")

        # Running Slide Footer Bar
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 28, SLIDE_WIDTH - 36, 28)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 14, "CONFIDENTIAL & PROPRIETARY — BLUESTOCK FINTECH")
        
        slide_str = f"Slide {self._pageNumber} of {page_count}"
        self.drawRightString(SLIDE_WIDTH - 36, 14, slide_str)
        
        self.restoreState()

def build_presentation_slides():
    doc = SimpleDocTemplate(
        str(OUTPUT_SLIDES),
        pagesize=(SLIDE_WIDTH, SLIDE_HEIGHT),
        leftMargin=36,
        rightMargin=36,
        topMargin=50,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#1B365D")
    c_accent = colors.HexColor("#D4AF37")
    c_text = colors.HexColor("#1E293B")
    
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=c_primary,
        spaceBefore=0,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=c_primary,
        alignment=1
    )
    
    card_value_style = ParagraphStyle(
        'CardValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=18,
        textColor=c_accent,
        alignment=1
    )
    
    table_cell_style = ParagraphStyle(
        'SlideTableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=c_text
    )

    table_header_style = ParagraphStyle(
        'SlideTableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("BLUESTOCK MUTUAL FUND ANALYTICS", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=c_accent, spaceAfter=8)))
    story.append(Paragraph("Executive Capstone Presentation", ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=c_primary, spaceAfter=10)))
    story.append(Paragraph("End-to-End Quantitative Risk Analytics, ETL Star Schema Architecture, Behavioral Cohort Modeling, and Power BI BI System", ParagraphStyle('Sub2', fontName='Helvetica', fontSize=11, leading=15, textColor=colors.HexColor("#475569"), spaceAfter=20)))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceAfter=20))
    
    meta_data = [
        [Paragraph("<b>Presenter:</b> Bluestock Quant Team", body_style), Paragraph("<b>Target:</b> Executive Committee & Risk Managers", body_style)],
        [Paragraph("<b>Data Scope:</b> 40 Schemes | 5,000 Investors | 32,778 Logs", body_style), Paragraph("<b>Status:</b> Final Approved Capstone Submission", body_style)]
    ]
    t_m = Table(meta_data, colWidths=[320, 320])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0"))
    ]))
    story.append(t_m)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("1. Executive Summary & Core Achievements", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    # 4 Key Stat Callout Cards
    cards_data = [
        [
            Paragraph("Evaluated AUM", card_title_style),
            Paragraph("Historical NAVs", card_title_style),
            Paragraph("Retail Investors", card_title_style),
            Paragraph("SIP Continuity", card_title_style)
        ],
        [
            Paragraph("₹10,43,664 Cr", card_value_style),
            Paragraph("64,320 Logs", card_value_style),
            Paragraph("5,000 Users", card_value_style),
            Paragraph("2.20%", card_value_style)
        ]
    ]
    t_cards = Table(cards_data, colWidths=[160, 160, 160, 160])
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("• <b>Automated Data Pipeline:</b> Robust ETL scripts ingesting and validating 46k raw NAV records into 64,320 clean entries.", bullet_style))
    story.append(Paragraph("• <b>Relational Star Schema:</b> Production SQLite database (`mutual_fund_analysis.db`) housing 2 dimensions and 4 fact tables.", bullet_style))
    story.append(Paragraph("• <b>Quantitative Downside Risk Engine:</b> 95% Historical VaR & CVaR computed for all 40 schemes (Small Cap VaR = -2.39%).", bullet_style))
    story.append(Paragraph("• <b>Dynamic Volatility & Rolling Sharpe:</b> 90-day annualized rolling Sharpe ratio trajectories evaluated across 1,607 trading days.", bullet_style))
    story.append(Paragraph("• <b>Behavioral Retention Alert:</b> Identified a critical 2.20% SIP Continuity Rate among qualifying investors ($\ge 6$ SIPs).", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT & OBJECTIVES
    # =========================================================================
    story.append(Paragraph("2. Problem Statement & Strategic Objectives", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    col1 = [
        Paragraph("<b>Industry Friction Points:</b>", ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, spaceAfter=4)),
        Paragraph("1. <b>Downside Risk Opacity:</b> Factsheets rely on standard deviation, missing non-normal left-tail crash risk.", bullet_style),
        Paragraph("2. <b>Static Sharpe Ratios:</b> Point-in-time metrics hide temporary market volatility regimes.", bullet_style),
        Paragraph("3. <b>SIP Churn Deterioration:</b> Platforms lack automated alerts for payment schedule gaps before cancellation.", bullet_style),
        Paragraph("4. <b>Sector Concentration:</b> Top funds often carry hidden $>40\%$ single-sector bets.", bullet_style)
    ]
    
    col2 = [
        Paragraph("<b>Core Strategic Objectives:</b>", ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, spaceAfter=4)),
        Paragraph("1. <b>Automate End-to-End Pipeline:</b> `run_pipeline.py` master execution with zero manual steps.", bullet_style),
        Paragraph("2. <b>Quantify Downside Tail Risk:</b> Compute 95% Historical VaR/CVaR and 90-day Rolling Sharpe.", bullet_style),
        Paragraph("3. <b>Model Investor Behavioral Cohorts:</b> Track 2024–2025 acquisition cohorts and SIP gap days.", bullet_style),
        Paragraph("4. <b>Deliver Executive Dashboard:</b> 4-page Power BI dashboard suite (`Dashboard.pdf`).", bullet_style)
    ]
    
    t_prob = Table([[col1, col2]], colWidths=[315, 325])
    t_prob.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(t_prob)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: DATA ENGINEERING & ETL ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("3. Data Engineering & ETL Pipeline Design", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    story.append(Paragraph("The ETL architecture ensures zero data loss, schema validation, and complete reproducibility:", body_style))
    
    etl_steps = [
        [Paragraph("Pipeline Module", table_header_style), Paragraph("Input File & Raw Size", table_header_style), Paragraph("Core Cleaning Logic Applied", table_header_style), Paragraph("Output Cleaned Result", table_header_style)],
        [Paragraph("`clean_nav.py`", table_cell_style), Paragraph("`02_nav_history.csv`<br/>(46,000 raw rows)", table_cell_style), Paragraph("Date parsing, drops $NAV \le 0$, removes duplicate scheme dates, reindexes calendar with forward-fill (`ffill()`).", table_cell_style), Paragraph("`nav_history.csv`<br/>(64,320 clean rows)", table_cell_style)],
        [Paragraph("`clean_transactions.py`", table_cell_style), Paragraph("`08_investor_transactions.csv`<br/>(32,778 raw rows)", table_cell_style), Paragraph("Standardizes types (`SIP`, `Lumpsum`, `Redemption`), validates `amount_inr > 0`, normalizes KYC status, drops duplicates.", table_cell_style), Paragraph("`investor_transactions.csv`<br/>(32,778 clean rows)", table_cell_style)],
        [Paragraph("`clean_performance.py`", table_cell_style), Paragraph("`07_scheme_performance.csv`<br/>(40 raw schemes)", table_cell_style), Paragraph("Validates expense ratios $[0.1\%, 2.5\%]$, checks Morningstar ratings $[1, 5]$, flags anomalies without losing valid rows.", table_cell_style), Paragraph("`scheme_performance.csv`<br/>(40 clean schemes)", table_cell_style)]
    ]
    t_etl = Table(etl_steps, colWidths=[100, 130, 280, 130])
    t_etl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_etl)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: STAR SCHEMA DATABASE DESIGN
    # =========================================================================
    story.append(Paragraph("4. SQLite Star Schema Data Warehouse Design", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    schema_info = [
        [Paragraph("Table Name", table_header_style), Paragraph("Table Role", table_header_style), Paragraph("Primary Key", table_header_style), Paragraph("Foreign Key Relationships", table_header_style), Paragraph("Row Count", table_header_style)],
        [Paragraph("`dim_fund`", table_cell_style), Paragraph("Dimension", table_cell_style), Paragraph("`amfi_code`", table_cell_style), Paragraph("None", table_cell_style), Paragraph("40", table_cell_style)],
        [Paragraph("`dim_date`", table_cell_style), Paragraph("Dimension", table_cell_style), Paragraph("`date`", table_cell_style), Paragraph("None", table_cell_style), Paragraph("1,608", table_cell_style)],
        [Paragraph("`fact_nav`", table_cell_style), Paragraph("Fact Table", table_cell_style), Paragraph("Composite", table_cell_style), Paragraph("`amfi_code` $\\rightarrow$ dim_fund | `date` $\\rightarrow$ dim_date", table_cell_style), Paragraph("64,320", table_cell_style)],
        [Paragraph("`fact_transactions`", table_cell_style), Paragraph("Fact Table", table_cell_style), Paragraph("`transaction_id`", table_cell_style), Paragraph("`amfi_code` $\\rightarrow$ dim_fund | `transaction_date` $\\rightarrow$ dim_date", table_cell_style), Paragraph("32,778", table_cell_style)],
        [Paragraph("`fact_performance`", table_cell_style), Paragraph("Fact Table", table_cell_style), Paragraph("`amfi_code`", table_cell_style), Paragraph("`amfi_code` $\\rightarrow$ dim_fund", table_cell_style), Paragraph("40", table_cell_style)],
        [Paragraph("`fact_aum`", table_cell_style), Paragraph("Fact Table", table_cell_style), Paragraph("Composite", table_cell_style), Paragraph("`date` $\\rightarrow$ dim_date", table_cell_style), Paragraph("90", table_cell_style)]
    ]
    t_sch = Table(schema_info, colWidths=[90, 70, 80, 230, 70])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_sch)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Integrity Enforcement:</b> Database enforces `PRAGMA foreign_keys = ON;` and includes automated row count parity verification comparing raw CSV records against SQLite tables during build.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: CATEGORY AUM & RETURN OVERVIEW
    # =========================================================================
    story.append(Paragraph("5. Category AUM & Transaction Type Distribution", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    t_eda = Table([
        [Paragraph("Fund Category", table_header_style), Paragraph("Scheme Count", table_header_style), Paragraph("Total AUM (₹ Cr)", table_header_style), Paragraph("AUM Share (%)", table_header_style), Paragraph("Avg 3-Yr CAGR (%)", table_header_style)],
        [Paragraph("Equity Funds", table_cell_style), Paragraph("34 schemes", table_cell_style), Paragraph("₹8,55,846 Cr", table_cell_style), Paragraph("82.0%", table_cell_style), Paragraph("15.46%", table_cell_style)],
        [Paragraph("Debt Funds", table_cell_style), Paragraph("6 schemes", table_cell_style), Paragraph("₹1,87,818 Cr", table_cell_style), Paragraph("18.0%", table_cell_style), Paragraph("6.29%", table_cell_style)],
        [Paragraph("<b>Total Market</b>", table_cell_style), Paragraph("<b>40 schemes</b>", table_cell_style), Paragraph("<b>₹10,43,664 Cr</b>", table_cell_style), Paragraph("<b>100.0%</b>", table_cell_style), Paragraph("<b>14.08%</b>", table_cell_style)]
    ], colWidths=[120, 100, 140, 110, 170])
    t_eda.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_eda)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Transaction Ledger Distribution (32,778 Logs):</b>", ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, spaceAfter=4)))
    story.append(Paragraph("• <b>SIP Installments:</b> 19,716 transactions (60.1%) | Total Volume: ₹21.72 Cr | Avg Ticket: ₹11,018", bullet_style))
    story.append(Paragraph("• <b>Lumpsum Inflows:</b> 8,095 transactions (24.7%) | Total Volume: ₹205.98 Cr | Avg Ticket: ₹254,456", bullet_style))
    story.append(Paragraph("• <b>Redemptions:</b> 4,967 transactions (15.2%) | Total Volume: ₹124.45 Cr | Avg Ticket: ₹250,559", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: RISK-ADJUSTED FUND PERFORMANCE
    # =========================================================================
    story.append(Paragraph("6. Risk-Adjusted Fund Performance Leaderboard", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    perf_data = [
        [Paragraph("Scheme Name", table_header_style), Paragraph("Category", table_header_style), Paragraph("3Yr CAGR", table_header_style), Paragraph("Alpha", table_header_style), Paragraph("Beta", table_header_style), Paragraph("Sharpe", table_header_style), Paragraph("Sortino", table_header_style), Paragraph("Max Drawdown", table_header_style)],
        [Paragraph("SBI Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("23.39%", table_cell_style), Paragraph("+4.85", table_cell_style), Paragraph("0.89", table_cell_style), Paragraph("0.94", table_cell_style), Paragraph("1.42", table_cell_style), Paragraph("-24.80%", table_cell_style)],
        [Paragraph("ABSL Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("22.38%", table_cell_style), Paragraph("+4.12", table_cell_style), Paragraph("0.95", table_cell_style), Paragraph("0.88", table_cell_style), Paragraph("1.31", table_cell_style), Paragraph("-23.40%", table_cell_style)],
        [Paragraph("Axis Small Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("20.98%", table_cell_style), Paragraph("+3.75", table_cell_style), Paragraph("0.82", table_cell_style), Paragraph("0.91", table_cell_style), Paragraph("1.38", table_cell_style), Paragraph("-21.15%", table_cell_style)],
        [Paragraph("HDFC Top 100 Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("14.84%", table_cell_style), Paragraph("+1.85", table_cell_style), Paragraph("0.97", table_cell_style), Paragraph("1.06", table_cell_style), Paragraph("1.58", table_cell_style), Paragraph("-12.40%", table_cell_style)],
        [Paragraph("Mirae Asset Large Cap - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("14.81%", table_cell_style), Paragraph("+1.72", table_cell_style), Paragraph("0.96", table_cell_style), Paragraph("1.06", table_cell_style), Paragraph("1.56", table_cell_style), Paragraph("-11.90%", table_cell_style)],
        [Paragraph("ICICI Pru Liquid Fund - Reg", table_cell_style), Paragraph("Debt", table_cell_style), Paragraph("7.68%", table_cell_style), Paragraph("0.00", table_cell_style), Paragraph("0.26", table_cell_style), Paragraph("7.68", table_cell_style), Paragraph("11.45", table_cell_style), Paragraph("-0.15%", table_cell_style)]
    ]
    t_perf = Table(perf_data, colWidths=[150, 50, 60, 50, 44, 50, 50, 186])
    t_perf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_perf)
    story.append(Spacer(1, 8))
    story.append(Paragraph("• <b>Small Cap Tradeoff:</b> Small cap funds deliver highest 3yr returns (+23.39%) but suffer max drawdowns of -24.80%.", bullet_style))
    story.append(Paragraph("• <b>Large Cap Efficiency:</b> Large cap funds achieve higher Sharpe ratios (1.06 vs 0.94) with half the drawdown (-11.90%).", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: ADVANCED DOWNSIDE RISK ANALYTICS (VaR & CVaR)
    # =========================================================================
    story.append(Paragraph("7. Advanced Downside Tail Risk (95% VaR & CVaR)", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    story.append(Paragraph("Historical 95% Value at Risk (5th percentile) and CVaR (expected shortfall below VaR) across 1,607 trading days:", body_style))
    
    var_table_data = [
        [Paragraph("Downside Rank", table_header_style), Paragraph("Scheme Name", table_header_style), Paragraph("Category", table_header_style), Paragraph("95% VaR (%)", table_header_style), Paragraph("95% CVaR (%)", table_header_style), Paragraph("Evaluated Days", table_header_style)],
        [Paragraph("1 (Highest Risk)", table_cell_style), Paragraph("ABSL Small Cap Fund - Regular - Growth", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.39%</b>", table_cell_style), Paragraph("<b>-3.03%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("Axis Small Cap Fund - Regular - Growth", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.33%</b>", table_cell_style), Paragraph("<b>-2.97%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("SBI Small Cap Fund - Direct Plan - Growth", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.32%</b>", table_cell_style), Paragraph("<b>-3.02%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("Nippon India Small Cap Fund - Regular", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.28%</b>", table_cell_style), Paragraph("<b>-2.99%</b>", table_cell_style), Paragraph("1,607", table_cell_style)],
        [Paragraph("5", table_cell_style), Paragraph("SBI Small Cap Fund - Regular Plan", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("<b>-2.15%</b>", table_cell_style), Paragraph("<b>-2.84%</b>", table_cell_style), Paragraph("1,607", table_cell_style)]
    ]
    t_var = Table(var_table_data, colWidths=[90, 220, 60, 90, 90, 90])
    t_var.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_var)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Insight:</b> Small Cap funds exhibit the steepest downside tail volatility, confirming that high CAGR comes with significant tail-risk exposure during market shocks.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: ROLLING SHARPE & DYNAMIC VOLATILITY
    # =========================================================================
    story.append(Paragraph("8. Dynamic Volatility & Rolling 90-Day Sharpe Ratio", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    chart_img_path = BASE_DIR / "rolling_sharpe_chart.png"
    if chart_img_path.exists():
        story.append(Image(str(chart_img_path), width=6.5*inch, height=2.8*inch))
        story.append(Paragraph("<i>Figure 9.1: 90-Day Annualized Rolling Sharpe Ratio Trajectory across 5 Representative Funds.</i>", ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor("#64748B"), spaceAfter=4)))
    
    story.append(Paragraph("• <b>Regime Shift Tracking:</b> Equity Sharpe ratios fluctuate dynamically between -2.73 and +7.61 depending on market momentum.", bullet_style))
    story.append(Paragraph("• <b>Liquid Stability:</b> Liquid debt funds maintain flat, high Sharpe trajectories (mean Sharpe = 10.40).", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: INVESTOR COHORTS & SIP CONTINUITY
    # =========================================================================
    story.append(Paragraph("9. Investor Cohorts & SIP Continuity Analysis", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    t_sip = Table([
        [Paragraph("SIP Retention Metric", table_header_style), Paragraph("Calculated Value", table_header_style), Paragraph("Strategic Business Context", table_header_style)],
        [Paragraph("Qualifying SIP Investors ($\ge 6$ SIPs)", table_cell_style), Paragraph("1,362 investors", table_cell_style), Paragraph("Base active retail investors evaluated for continuity", table_cell_style)],
        [Paragraph("Consistent Investors (Gap $\le 35$ days)", table_cell_style), Paragraph("30 investors", table_cell_style), Paragraph("Investors maintaining regular monthly installment schedule", table_cell_style)],
        [Paragraph("At-Risk Investors (Gap $> 35$ days)", table_cell_style), Paragraph("1,332 investors", table_cell_style), Paragraph("Investors exhibiting payment gaps and imminent default risk", table_cell_style)],
        [Paragraph("<b>SIP Continuity Rate (%)</b>", table_cell_style), Paragraph("<b>2.20%</b>", table_cell_style), Paragraph("<b>Critical retention friction requiring automated AMC nudge engine</b>", table_cell_style)]
    ], colWidths=[180, 110, 350])
    t_sip.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_sip)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>Acquisition Cohorts:</b> Cohort 2024 comprises 4,803 investors who invested ₹349.11 Cr capital, while Cohort 2025 comprises 197 investors with ₹3.05 Cr capital.", body_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 11: POWER BI DASHBOARD HIGHLIGHTS
    # =========================================================================
    story.append(Paragraph("10. Power BI Executive Dashboard Suite", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    pbi_path = BASE_DIR / "page1_industry_overview.png"
    if pbi_path.exists():
        story.append(Image(str(pbi_path), width=6.5*inch, height=2.8*inch))
        story.append(Paragraph("<i>Figure 10.1: Executive Power BI Dashboard Page 1 — Industry Overview.</i>", ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor("#64748B"), spaceAfter=4)))
    
    story.append(Paragraph("• <b>4-Page Interactive Suite:</b> Industry Overview, Fund Performance Scatter, Investor Demographics, and SIP Market Trends.", bullet_style))
    story.append(Paragraph("• <b>Financial DAX Engine:</b> Custom DAX measures computing weighted returns, net inflows, and category AUM splits.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 12: STRATEGIC RECOMMENDATIONS & CONCLUSION
    # =========================================================================
    story.append(Paragraph("11. Strategic Recommendations & Conclusion", slide_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=8))
    
    story.append(Paragraph("<b>Strategic Recommendations for Bluestock & AMCs:</b>", ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, spaceAfter=4)))
    story.append(Paragraph("1. <b>Automated Retention Nudge Engine:</b> Trigger automated SMS/WhatsApp alerts on Day 28 for 'At-Risk' investors to boost the 2.20% SIP continuity rate.", bullet_style))
    story.append(Paragraph("2. <b>Sector Concentration Caps:</b> Enforce a 35% single-sector allocation ceiling in Large Cap equity funds to mitigate high Sector HHI risk.", bullet_style))
    story.append(Paragraph("3. <b>Embed Risk Recommender Engine:</b> Integrate `recommender.py` into mobile trading apps to steer retail users toward optimal Sharpe-performing schemes.", bullet_style))
    
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Conclusion:</b> The Bluestock Mutual Fund Analytics Platform delivers a complete quantitative risk engine, relational star schema data warehouse, and executive dashboard suite—empowering wealth managers to protect retail capital and drive sustainable AUM growth.", body_style))

    doc.build(story, canvasmaker=SlideCanvas)
    
    if OUTPUT_SLIDES.exists():
        import shutil
        shutil.copyfile(OUTPUT_SLIDES, ROOT_SLIDES)
        print(f"Presentation PDF generated successfully: {OUTPUT_SLIDES} ({os.path.getsize(OUTPUT_SLIDES)} bytes)")

if __name__ == '__main__':
    build_presentation_slides()
