import pandas as pd
df=pd.read_csv("data/raw/01_fund_master.csv")

# unique fund houses
print("unique fund houses:",df['fund_house'].unique())

#unique categories
print("unique categories:",df['category'].unique())
print("unique sub categories:",df['sub_category'].unique())
print("unique risk grades:",df['risk_category'].unique())
print(df[['amfi_code','scheme_name','fund_house','sebi_category_code']].head())
