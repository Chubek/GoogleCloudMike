import requests
from bs4 import BeautifulSoup
import pandas as pd
import os.path
import gspread
from google.oauth2.service_account import Credentials

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    'client_secrets.json',
    scopes=scopes
)

gc = gspread.authorize(credentials)

sh = gc.open("Breezy_Urls_Shared_1")

worksheet = sh.get_worksheet(0)

urls = worksheet.get_all_values()

positions = []
locations = []
types = []
categories = []
url_names = []

for url_arr in urls[1:]:
    url = url_arr[1]
    print(f"Working on {url}")
    name = url.split("/")[-1]
    req = requests.get(url)

    soup = BeautifulSoup(req.content, 'html.parser')

    print(req.status_code)

    try:
        postings = soup.find_all('div', {"class": "positions-container"})
    except:
        print("Not positions-container. Continuing...")
        continue

    print(postings)
    print(len(postings))

    if len(postings) == 0:
        print("Url out of commission")
        continue

    for posting in postings:
        if url not in url_names:
            url_names.append(url)
            try:
                positions.append(posting.h2.get_text() or "Not Specified")
            except:
                print("Problem with positions!")
                positions.append("Not Specified!")
            try:
                locations.append(posting.find('li', {'class': 'location'}).span.get_text())
            except:
                print("Problem with locations!")
                locations.append("Not Specified")
            try:
                types.append(posting.find('li', {'class': 'type'}).span.get_text())
            except:
                print("Problem with types!")
                types.append("Not Specified")
            try:
                categories.append(posting.find('li', {'class': 'department'}).span.get_text())
            except:
                print("Problem with categories!")
                categories.append("Not Specified")

df = pd.DataFrame(
    {"Positions": positions, "Locations": locations, "Type": types, "Categories": categories, "URL Names": url_names})

df.to_csv(os.path.join("BreezyCSVs", f"whole.csv"))
print("Saved!")
