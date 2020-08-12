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

df_fin = pd.DataFrame(columns=["Permalink", "Title", "Cities", "Countries"])

fin_i = 0

client = bigquery.Client.from_service_account_json('client_secrets.json')


table = client.get_table("cydtw-site.reddit_tap_water.polished_table")


for i, content, title in zip(range(df.shape[0]), df["Content"].values, df["Title"].values):
    print(i)

    inserted = False
    appended = False

    for city, country in cities[1:]:
        print(f"Looking for city {city} and country {country}")

        pattern_city = re.compile(rf"\b{city}\b|\b{city.lower()}\b")
        pattern_country = re.compile(rf"\b{country}\b|\b{country.lower()}\b")

        try:
            city_exists = True if city not in df_fin.loc[fin_i, "Cities"] else False
            country_exists = True if country not in df_fin.loc[fin_i, "Countries"] else False
        except:
            city_exists = False
            country_exists = False

        if bool(pattern_city.search(str(content))):
            if not city_exists:
                df_fin = df_fin.append({'Permalink': links[i], 'Title': titles[i], 'Cities': '', 'Countries': ''},
                                       ignore_index=True)
                print("Appended")
                appended = True
                df_fin.loc[fin_i, "Cities"] = city + "," + df_fin.loc[fin_i, "Cities"]
                inserted = True
                print("Got city in content")
        if bool(pattern_country.search(str(content))):
            if not country_exists:
                if not appended:
                    df_fin = df_fin.append({'Permalink': links[i], 'Title': titles[i], 'Cities': '', 'Countries': ''},
                                           ignore_index=True)
                    print("Appended")
                    appended = True
                df_fin.loc[fin_i, "Countries"] = country + "," + df_fin.loc[fin_i, "Countries"]
                inserted = True
            print("Got country in content")
        if bool(pattern_city.search(str(title))):
            if not city_exists:
                if not appended:
                    df_fin = df_fin.append({'Permalink': links[i], 'Title': titles[i], 'Cities': '', 'Countries': ''},
                                           ignore_index=True)
                    print("Appended")
                    appended = True
                    df_fin.loc[fin_i, "Cities"] = city + "," + df_fin.loc[fin_i, "Cities"]
                    inserted = True
                    print("Got city in title")
        if bool(pattern_country.search(str(title))):
            if not country_exists:
                if not appended:
                    df_fin = df_fin.append({'Permalink': links[i], 'Title': titles[i], 'Cities': '', 'Countries': ''},
                                           ignore_index=True)
                    print("Appended")
                    appended = True
                df_fin.loc[fin_i, "Countries"] = country + "," + df_fin.loc[fin_i, "Countries"]
                inserted = True
                print("Got country in title")

    if inserted and appended:
        client.insert_rows(table, [df_fin.loc[fin_i, "Permalink"], df_fin.loc[fin_i, "Title"],
                                   df_fin.loc[fin_i, "Cities"], df_fin[fin_i, "Countries"]])
        fin_i += 1

    print(f"fin_i: {fin_i}")

    df_fin.to_csv("df_fin.csv")

worksheet_fin = sh_fin.get_worksheet(1)
set_with_dataframe(worksheet_fin, df_fin)
format_with_dataframe(worksheet_fin, df_fin, include_column_header=True)
