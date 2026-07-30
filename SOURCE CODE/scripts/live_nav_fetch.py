import requests
import pandas as pd
from pathlib import Path

#fetch data from api endpoint 
scheme_code=125497
url = f"https://api.mfapi.in/mf/{scheme_code}"

print(f"fetching data from : {url}")
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers, timeout=30)


#check HTTP status (200 ok)
if response.status_code !=200:
    raise Exception(f"API request faild with status: {response.status_code}")


#parse JSON & extract fields
payload =response.json()
meta_info=payload.get("meta",{})
nav_data=payload.get("data",[])
print(f"scheme name: {meta_info.get('scheme_name')}")
print(f"Total NAV records : {len(nav_data)}")

#transform to dataframe & format data types
df = pd.DataFrame(nav_data)

#convert string nav data into float number
df['nav']=pd.to_numeric(df['nav'],errors='coerce')

#reformat date string dd-mm-yyyy to yyyy -mm - dd
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')

#prepend scheme details
df.insert(0, 'scheme_code', meta_info.get('scheme_code'))
df.insert(1,'scheme_name',meta_info.get('scheme_name'))
print("\nData Preview:")
print(df.head())
print(df.head())

# save to raw csv
raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

output_file = raw_dir / "live_nav_125497.csv"
df.to_csv(output_file, index=False)
print(f"Successfully saved to: {output_file}")
