import pandas as pd
import requests
from bs4 import BeautifulSoup

req = requests.get("https://sustainablesources.com/resources/country-abbreviations/")

soup = BeautifulSoup(req.content, 'html.parser')

table = soup.find_all('table')[0]

trs = table.find_all('tr')

country_abbv = {tds[0].get_text().strip(): tds[1].get_text().strip() for tds in [tr.find_all('td') for tr in trs] if len(tds) > 1}

df_lat = pd.read_csv("/home/chubak/Downloads/worldcitiespop.csv", low_memory=False)
df_posts = pd.read_csv("/home/chubak/Downloads/Posts-Export-2020-August-16-2001.csv")

df_lat["City"] = df_lat["City"].str.capitalize()

df_lat["Country"] = df_lat["Country"].map(country_abbv)

print(df_lat["Country"])

inner = pd.merge(df_posts, df_lat.loc[:, ("City", "Country", "Latitude", "Longitude")],
                 left_on=['City name', 'Categories'],
                 right_on=['City', 'Country'], how='inner')

inner = inner.drop(["City", "Country"], axis=1)

inner.to_csv("joined_table.csv")
