from google.oauth2.service_account import Credentials
from google.cloud import bigquery
import gspread
import pprint

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
countries = countries_sheet.get_all_values()

client = bigquery.Client.from_service_account_json('client_secrets.json')


table = client.get_table("cydtw-site.cities.cities_list")

format_str = lambda cty: cty

for city, country in cities[2:]:
    print(f"{city}")
    query = f"UPDATE `cydtw-site.cities.tap_water_with_cities`\
        SET countries_included = CONCAT(countries_included, FORMAT('%s, ', '{country}')),\
    cities_included = CONCAT(cities_included, FORMAT('%s, ', '{city}'))\
        WHERE REGEXP_CONTAINS(post_content, '{format_str(city)}')\
        OR REGEXP_CONTAINS(post_title, '{format_str(city)}')"
    print(query)
    query_job = client.query(query)
    print(query_job.num_dml_affected_rows)
    print("Done")