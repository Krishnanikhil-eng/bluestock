import requests
import pandas as pd
from pathlib import Path

schemes = {
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip"
}

headers = {"User-Agent": "Mozilla/5.0"}
all_dfs = []

for code, short_name in schemes.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"Fetching NAV for {short_name} ({code})...")

    res=requests.get(url,headers=headers, timeout=30)
    if res.status_code==200:
        payload =res.json()
        meta=payload.get("meta",{})
        nav_list=payload.get("data",[])

        if nav_list:
            df = pd.DataFrame(nav_list)
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y").dt.strftime('%Y-%m-%d')
            df.insert(0, 'scheme_code', code)
            df.insert(1, 'scheme_name', meta.get('scheme_name', short_name))

            all_dfs.append(df)
            print(f"  -> Successfully fetched {len(df)} records.")
        else:
            print(f"  -> No data found for scheme {code}")
    else:
        print(f"  -> Failed to fetch {code}, HTTP status: {res.status_code}")

# Combine into one master DataFrame 
if all_dfs:
    combined_df = pd.concat(all_dfs, ignore_index=True)
    output_path = Path("data/raw/batch_5_schemes_nav.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_path, index=False)
    print(f"\nSaved {len(combined_df)} total records to {output_path}")
else:
    print("No data collected.")
