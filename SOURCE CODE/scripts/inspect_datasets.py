import os
import pandas as pd
from pathlib import Path

#1.path to raw dataset folder
data_dir=Path("data/raw")

#2.get list of all csv files sorted
csv_files=sorted(list(data_dir.glob("*.csv")))
print(f"Total datasets found: {len(csv_files)}\n")

#3.load and inspect each dataset
dataframes={}
for file_path in csv_files:
    file_name=file_path.name
    print("="*60)
    print(f"Dataset: {file_name}")
    print("="*60)


    #load dataset
    df=pd.read_csv(file_path)
    dataframes[file_name]=df

    #shape
    print(f" shape(rows,columns):{df.shape}")

    #data types
    print("\n column data types (.dtypes): ")
    print(df.dtypes)

    #check for missing values
    nulls=df.isnull().sum()
    nulls_detected=nulls[nulls>0]
    
    if not nulls_detected.empty:
        print("\n missing vlaues detected:")
        print(nulls_detected)
    else:
        print("\n missing vlaues:None")
    
    #display head
    print("\n first 3 rows(.head()):")
    print(df.head(3))
    print("\n" + '-' * 60 + "\n")