import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import re

def run_analytical_queries():
    base_dir = Path(__file__).resolve().parent.parent.parent
    db_file = base_dir / "mutual_fund_analysis.db"
    sql_file = base_dir / "SOURCE CODE/sql/analytical_queries.sql"
    report_file = base_dir / "SOURCE CODE/reports/query_results.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if not db_file.exists():
        print(f"Error: Database file not found at {db_file}")
        return

    # Initialize SQLite engine
    engine = create_engine(f"sqlite:///{db_file}")

    # Read and parse SQL file
    with open(sql_file, 'r') as sf:
        sql_content = sf.read()

    # Split queries by semicolon (but ignore semicolon inside comments)
    # We will separate queries based on '-- Query X:' pattern
    query_blocks = re.split(r'(-- Query \d+:[^\n]*)', sql_content)
    
    queries = []
    # Re-assemble headers with their respective queries
    i = 1
    while i < len(query_blocks):
        header = query_blocks[i].strip()
        query = query_blocks[i+1].strip()
        
        # Clean up trailing semicolons
        if query.endswith(';'):
            query = query[:-1].strip()
            
        queries.append((header, query))
        i += 2

    # Markdown report initialization
    report_md = []
    report_md.append("# Mutual Fund Data Analysis - Query Results Report\n")
    report_md.append("This report documents the results of executing 10 analytical SQL queries against the star schema database.\n")
    report_md.append("## Database File: `mutual_fund_analysis.db`\n")

    print(f"Executing {len(queries)} analytical queries...")

    for index, (header, query) in enumerate(queries, 1):
        print(f"\nRunning {header}...")
        report_md.append(f"### {header}")
        
        # Extract business value from header comments or query comments
        desc_match = re.search(r'-- Business Value: (.*)', header)
        if desc_match:
            report_md.append(f"**Business Value:** {desc_match.group(1)}\n")
        
        report_md.append("```sql\n" + query + ";\n```\n")
        
        try:
            # Execute query and load into DataFrame
            df = pd.read_sql_query(query, engine)
            
            # Format and output results
            if df.empty:
                print("No results returned.")
                report_md.append("*No results returned.*\n")
            else:
                print(df.to_string(index=False))
                # Add Markdown table to report
                report_md.append(df.to_markdown(index=False) + "\n")
        except Exception as e:
            print(f"Error executing query {index}: {e}")
            report_md.append(f"**Error executing query:** {e}\n")
        
        report_md.append("-" * 40 + "\n")

    # Write report file
    with open(report_file, 'w', encoding='utf-8') as rf:
        rf.write("\n".join(report_md))

    print(f"\nAll queries executed. Report generated at: {report_file}")

if __name__ == "__main__":
    run_analytical_queries()
