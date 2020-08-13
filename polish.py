import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread_formatting.dataframe import format_with_dataframe
import re
from google.cloud import bigquery

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    'client_secrets.json',
    scopes=scopes
)

gc = gspread.authorize(credentials)

sh_fin = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/1fT48B-9E3HnCp5sOEfHgumx1OTz4wD30_c_2M5wmcYM")
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Eg5cF8BCjwZe7rUu5U8m6qckkbCaZHF-jsbk7whTWfI/")

cities_sheet = sh.worksheet("Cities")
countries_sheet = sh.worksheet("Countries")

cities = cities_sheet.get_all_values()
countries = countries_sheet.get_all_values()

df = pd.read_csv("results-20200812-202830.csv")

titles = df["Title"].values
links = df["Link"].values

client = bigquery.Client.from_service_account_json('client_secrets.json')

table = client.get_table("cydtw-site.reddit_tap_water.polished_table")

done_links = []

for city, country in cities[1:]:

    pattern_city = re.compile(rf"\b{city}\b|\b{city.lower()}\b")
    pattern_country = re.compile(rf"\b{country}\b|\b{country.lower()}\b")

    for i, content, title in zip(range(df.shape[0]), df["Content"].values, df["Title"].values):
        print(i)

        if df.loc[i, "Link"] in done_links:
            print("Already parsed...")
            continue

        done_links.append(df.loc[i, "Link"])

        link = df.loc[i, "Link"]

        job = client.query(
            f"SELECT Cities, Countries FROM `cydtw-site.reddit_tap_water.polished_table` WHERE Link = '{link}'  LIMIT 1")

        job.result()

        row_num = 0

        city_str = ""
        country_str = ""

        for row in job:
            row_num += 1
            city_str = row[0]
            country_str = row[1]

        if row_num == 0:
            print("Query returned zero. Creating...")
            client.insert_rows(table, [(link, title, "", "")])

        print(f"Query returned {city_str} and {country_str}")

        if bool(pattern_city.search(str(content))):
            if city not in city_str.split(", "):
                city_str += city + ", "

        if bool(pattern_city.search(str(title))):
            if city not in city_str.split(", "):
                city_str += city + ", "

        if bool(pattern_country.search(str(content))):
            if country not in country_str.split(", "):
                country_str += country + ", "

        if bool(pattern_country.search(str(title))):
            if country not in country_str.split(", "):
                country_str += country + ", "

        client.query(f"UPDATE `cydtw-site.reddit_tap_water.polished_table` SET Cities = {city_str[:-2]},"
                     f" Countries = {country_str[:-2]} WHERE LINK = '{link}'")
