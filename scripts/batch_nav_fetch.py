import requests
import pandas as pd
from pathlib import Path
schemes={1199551:"SBI Bluechip",
        1230503: "ICICI bluechip",
        118632: "Nippon large cap",
        119092: "Axis bluechip",
        120841: "Kotak bluechip"}

headers={"User-Agent":"Mozilla.5.0"}
all_dfs=[]
for code,short_name in schemes.items():
    url=f"https://api.mfapi.in/mf/{code}"
    print(f"fetching nav for {short_name} ({code})..")

    res=requests.get(url,headers=headers, timeout=30)
    if res.status_code==200:
        payload =res.json()
        meta=payload.get("meta",{})
        nav_list=payload.get("data",[])

        df=pd.DataFrame(nav_list)
        df['nav']=pd.to_numeric(df['nav'],errors='coerce')
        df['date']=pd.to_datetime(df['date'],format="%d-%m-%Y").dt.strftime('%Y-%m-%d')
        df.insert(0,'scheme_code',code)
        df.insert(1,'scheme_name',meta.get('scheme_name',short_name))

        all_dfs.append(df)
#Cobine into one master DataFrame 
combined_df=pd.concat(all_dfs,ignore_index=True)
output_path=Path("data/raw/batch_5_schemes_nav.csv")
output_path.parent.mkdir(parents=True,exist_ok=True)
combined_df.to_csv(output_path,index=False)
print(f"Saved{len(combined_df)} total records to {output_path}")