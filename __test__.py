from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import gspread

scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

credentials = Credentials.from_service_account_file(
        'client_secrets.json',
        scopes=scopes
    )

gc = gspread.authorize(credentials)

sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Eg5cF8BCjwZe7rUu5U8m6qckkbCaZHF-jsbk7whTWfI/")

cities_sheet = sh.worksheet("Cities")
countries_sheet = sh.worksheet("Countries")

cities = cities_sheet.get_all_values()

client = bigquery.Client.from_service_account_json('client_secrets.json')


table = client.get_table("cydtw-site.cities.cities_list")

for city in cities[2:]:
    city = city[0]
    print(f"{city}")

    query = f"UPDATE `cydtw-site.cities.tap_water_with_cities`\
        SET post_cities = CONCAT(post_cities, '{city}')\
        WHERE REGEXP_CONTAINS(post_content, FORMAT('\b%s\b', '{city}'))\
        OR REGEXP_CONTAINS(post_title, FORMAT('\b%s\b', '{city}'))"
    query_job = client.query(query)
    print("Done")