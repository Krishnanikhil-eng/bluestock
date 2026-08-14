"""
Simple Fund Recommender Engine
================================
Inputs: risk appetite ('Low' | 'Moderate' | 'High')
Outputs: Top 3 mutual fund recommendations by Sharpe Ratio within matching risk grade.

Usage:
  python recommender.py [Low|Moderate|High]
"""

import sys
import os
import sqlite3
import pandas as pd

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, 'mutual_fund_analysis.db'),
        os.path.join(base_dir, '..', 'mutual_fund_analysis.db'),
        os.path.join(base_dir, '..', '..', 'mutual_fund_analysis.db')
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return 'mutual_fund_analysis.db'

def recommend_funds(risk_appetite='Moderate', top_n=3):
    """
    Recommend top funds based on user's risk appetite.
    
    Parameters:
        risk_appetite (str): 'Low', 'Moderate', or 'High'
        top_n (int): Number of funds to recommend (default: 3)
        
    Returns:
        pd.DataFrame: Formatted table with Rank, Fund Name, Risk Grade, and Sharpe Ratio
    """
    risk_str = str(risk_appetite).strip().title()
    valid_inputs = ['Low', 'Moderate', 'High']
    if risk_str not in valid_inputs:
        raise ValueError(f"Invalid risk appetite '{risk_appetite}'. Must be one of {valid_inputs}")
        
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    sp = pd.read_sql_query("SELECT amfi_code, scheme_name, risk_grade, sharpe_ratio FROM fact_performance", conn)
    conn.close()
    
    if risk_str == 'Low':
        match_grades = ['Low', 'Below Average', 'Low to Moderate']
    elif risk_str == 'High':
        match_grades = ['High', 'Very High']
    else:  # Moderate
        match_grades = ['Moderate', 'Moderately High', 'Average']
        
    filtered = sp[sp['risk_grade'].isin(match_grades)].copy()
    if len(filtered) == 0:
        filtered = sp.copy()
        
    recs = filtered.sort_values('sharpe_ratio', ascending=False).head(top_n).copy()
    recs['Rank'] = range(1, len(recs) + 1)
    recs = recs.rename(columns={
        'scheme_name': 'Fund Name',
        'risk_grade': 'Risk Grade',
        'sharpe_ratio': 'Sharpe Ratio'
    })
    
    return recs[['Rank', 'Fund Name', 'Risk Grade', 'Sharpe Ratio']]

if __name__ == '__main__':
    risk_input = sys.argv[1] if len(sys.argv) > 1 else 'Moderate'
    print(f"\n==================================================")
    print(f" MUTUAL FUND RECOMMENDER (Risk Appetite: '{risk_input.title()}')")
    print(f"==================================================\n")
    try:
        recommendations = recommend_funds(risk_input)
        print(recommendations.to_string(index=False))
        print("\n* Note: Recommender is for analytical demonstration; not financial advice.")
    except Exception as e:
        print(f"Error: {e}")
