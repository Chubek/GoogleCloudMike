from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import json
import ast
import requests
import praw
import re
from difflib import SequenceMatcher
import pandas as pd
import time
from rake_nltk import Metric, Rake
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
from rake_nltk import Metric, Rake
import nltk
import datetime
import os
import textwrap
import itertools
import requests
import sys

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

cities = cities_sheet.get_all_values()

df = pd.read_csv("results-20200815-022620.csv")

cities_got = ["" for city in range(df.shape[0])]
countries_got = ["" for country in range(df.shape[0])]

for city, country in cities[1:]:
    print(f"Checking {city}")
    pattern_city = re.compile(rf"\b{city}\b")
    pattern_country = re.compile(rf"\b{country}\b")

    try:
        for i, par in enumerate(df.loc[:, "parahraph"]):
            print(i)
            if bool(pattern_city.search(par)):
                cities_got[i] += f"{city}, "

            if bool(pattern_country.search(par)) and country not in countries_got[i]:
                countries_got[i] += f"{country}, "
    except:
        continue

cities_polished = [city[:-1] for city in cities_got]
countries_polished = [country[:-1] for country in countries_got]

df["cities_got"] = pd.Series(cities_polished, index=df.index)
df["countries_got"] = pd.Series(countries_polished, index=df.index)


df.to_csv("polished_dataseries.csv")