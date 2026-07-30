# Mutual Fund Analysis Pipeline

## Overview
This project focuses on building a robust mutual fund data analysis pipeline. It is designed to automate the batch ingestion of live Net Asset Value (NAV) data from external APIs, perform exploratory data analysis (EDA) on fund master datasets to understand scheme classifications (risk, category, sub-category), and implement clean, reusable scripts to store and process this data for downstream analytical workflows.

## Project Structure
The repository has been logically separated into the following key directories:

- **`DATASETS/`**: Contains raw and processed data files. Includes comprehensive datasets such as fund master records, historical NAVs, AUM by fund house, monthly SIP inflows, and scheme performance data.
- **`DOCUMENTATION/`**: Holds project-related documents, including the capstone project PDF (`Bluestock_MF_Capstone_Project.pdf`).
- **`SOURCE CODE/`**: The core directory housing all Python scripts, Jupyter notebooks, SQL queries, and requirements.

## Progress / What We Have Done So Far
1. **Project Reorganization**: Restructured the entire repository into a standardized layout (`DATASETS`, `DOCUMENTATION`, `SOURCE CODE`) to cleanly separate code, data, and docs.
2. **Data Ingestion & Fetching**: 
   - Implemented scripts for fetching live NAV data for specific funds (`live_nav_fetch.py`).
   - Created batch processing scripts to fetch NAV data for multiple schemes simultaneously (`batch_nav_fetch.py`).
3. **Data Validation & Exploration**:
   - Developed utility scripts to validate AMFI codes against master lists (`validate_amfi_codes.py`).
   - Created scripts and Jupyter Notebooks for initial dataset inspection and exploration of the fund master dataset (`explore_fund_master.py`, `01_dataset_inspection.ipynb`).
4. **Environment Setup**: Generated a `requirements.txt` to manage necessary dependencies for running the data pipelines and analysis.

## Setup Instructions
To set up the project locally:
1. Create and activate a Python virtual environment.
2. Navigate to the `SOURCE CODE/` directory.
3. Install the dependencies using:
   ```bash
   pip install -r requirements.txt
   ```
