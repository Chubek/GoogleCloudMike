import requests
from bs4 import BeautifulSoup
import pandas as pd
import os.path

urls = [url.strip() for url in open("urls.txt", "r").readlines()]

positions = []
locations = []
categories = []
url_names = []

for url in urls:
    print(f"Working on {url}")
    name = url.split("/")[-1]
    req = requests.get(url)

    soup = BeautifulSoup(req.content, 'html.parser')

    print(req.status_code)

    postings = soup.find_all('div', {"class": "posting"})

    print(postings)
    print(len(postings))

    if len(postings) == 0:
        print("Url out of commission")
        continue

    for posting in postings:
        positions.append(posting.h5.get_text())
        url_names.append(url)
        spans = posting.find_all('span')
        if len(spans) > 0:
            locations.append(spans[0].get_text())
            if len(spans) >= 2:
                categories.append(spans[1].get_text())
            else:
                categories.append("Not Specified")

df = pd.DataFrame(
    {"Positions": positions, "Locations": locations, "Categories": categories, "URL Names": url_names})
df.to_csv(os.path.join("Lever_CSVs", f"whole.csv"))
print("Saved!")
