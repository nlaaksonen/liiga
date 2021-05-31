"""
In this script we show how to use the LiigaScraper class
to retrieve data from multiple years from liiga.fi.
"""
import pandas as pd
from liiga_scraper import LiigaScraper
from importlib import reload
import pickle
import datetime

years = range(1980, 2020)
yearly_data = []
type = ""

for year in years:
    # series:
    # url = f"https://www.liiga.fi/fi/tilastot/{year}-{year+1}/runkosarja/joukkueet/"
    # players:
    # url = f"https://www.liiga.fi/fi/tilastot/{year}-{year+1}/runkosarja/pelaajat/"
    # games:
    url = f"https://liiga.fi/fi/ottelut/{year}-{year+1}/runkosarja/"

    ls = LiigaScraper(url=url)
    type = ls.type
    yearly_data.append(ls.getStats())

df = pd.concat(yearly_data)

fname = (f"liiga_stats_{type}_"
         +f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")

with open(fname, 'wb') as f:
    pickle.dump(df, f)

print(f"Successfully wrote {len(df)} rows to {fname}.")
