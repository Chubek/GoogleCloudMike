import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import re
import time

import pandas as pd

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
urls = []
data = []
SEARCH_ENGINE_ID = "8038b946b9a62a518"
API_KEY = "AIzaSyC0Mh-ZCUXyK8z0kdMor8viJRmMLSYo67I"
service = build("customsearch", "v1", developerKey=API_KEY)

for city, country in cities[1:30]:

    for i in range(0, 100, 10):
        query = f"(tap AND water) AND ({city} OR {country})"
        the_result = service.cse().siterestrict().list(q=query,
                                                       start=i,
                                                       cx=SEARCH_ENGINE_ID).execute()

        print("Waiting...")
        time.sleep(20)
        print("Wait done...")

        pattern = re.compile(rf"(tap.water).(.*{city})|(.quality|.safety)")

        try:
            for item in the_result.get("items"):
                if bool(pattern.search(item.get('link'))):
                    data.append({"link": item.get("link"), "matches": True})
                else:
                    data.append({"link": item.get("link"), "matches": False})
        except:
            continue

df = pd.DataFrame.from_records(data)

df.to_csv("data_regex.csv")
