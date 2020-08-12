from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import json
import ast
import requests
import praw
import re
from difflib import SequenceMatcher
Will
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

nltk.download('stopwords')
nltk.download('punkt')


def get_google_reddit_tap_water(index_num):

    print(f"Starting at {index_num}")

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
    table = client.get_table("cydtw-site.reddit_tap_water.reddit_google_nodups")
    SEARCH_ENGINE_ID = "006168594918175601863:t8oecxasips"
    API_KEY = "AIzaSyDefw2spt4b-c8qkIqOy5O7q0otou2W9fA"
    GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google-chrome'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

    service = build("customsearch", "v1", developerKey=API_KEY)

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument('headless')
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--remote-debugging-port=9222')
    options.binary_location = GOOGLE_CHROME_PATH
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

    reddit = praw.Reddit(client_id="o-ZP_mKBAwQJRQ",
                         client_secret="KCfO1wo6DVVfP8zAKVYWOP8KHEQ",
                         password="lasvegas",
                         user_agent="Water Safety Grab by /u/OceanLinerXLL",
                         username="OceanLinerXLL")

    query_num = 13
    row_num = 0
    found_ids = []
    for city_ in cities[index_num:]:
        city = city_[0]
        city_country = city_[1]
        country = city_country

        if query_num % 5 == 0:
            time.sleep(26)
        elif query_num % 8 == 0:
            time.sleep(50)

        query = f"tap AND water AND ({city} OR {city_country})"
        print(f"Searching for {query}. Query number: {query_num}")

        try:
            the_result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID).execute()
            query_num += 1
        except:
            print(f"Skipping {city} and {country}")
            continue

        urls = []
        try:
            for item in the_result.get("items"):
                url = item.get("link").replace("www", "old")

                if url.split("/")[-4] == "comments":
                    id_found = url.split("/")[-3]
                    if id_found in found_ids:
                        print("ID already exists")
                        continue
                    urls.append(url)
                    found_ids.append(id_found)
                    print(f"url {url} with id {id_found} added")
        except:
            print("No items.")
            continue

        try:
            for url in urls:
                print(f"Operating on {url}")

                pattern_country = re.compile(rf"(?i)(?:\b{country}\b)")
                pattern_city = re.compile(rf"(?i)(?:\b{city}\b)")

                try:

                    id_ = url.split("/")[-3]

                    submission = reddit.submission(id=id_)
                    thread_id = submission.id
                    key_phrase = ""

                    try:
                        r = Rake()
                        r.extract_keywords_from_text(submission.selftext)
                        key_phrase = r.get_ranked_phrases()[0]
                        print(f"keyphrase is {key_phrase}")
                    except:
                        print("Error getting keyphrase")

                    country_contains = ""
                    city_contains = ""

                    try:
                        country_contains = country if bool(
                            pattern_country.search(submission.selftext)) else ""
                        city_contains = f"{city}, {city_country}" if bool(
                            pattern_city.search(submission.selftext)) else ""
                    except:
                        print("Failed getting city and country contains")

                    print(f"City contains {city_contains} and country contains {country_contains}")

                    row = [
                        (
                            True, str(datetime.datetime.fromtimestamp(submission.created_utc)),
                            str(submission.score),
                            str(submission.permalink), str(submission.title),
                            str(submission.selftext), str(key_phrase), str(city_contains),
                            str(country_contains),
                            str(thread_id), str(query))]

                    print(f"row is {row}")

                    error = client.insert_rows(table, row)
                    if not error:
                        print(f"Row number {row_num} inserted")
                        row_num += 1
                        del submission
                        del row
                        del error
                    else:
                        print(error)
                except:
                    print('Submission get failed. Retrying.')
                    continue
                try:
                    print(f"dirver getting {url.replace('https:', 'http:')}")
                    driver.get(url.replace("https:", "http:"))
                    print(f"Got page {driver.title}")
                    the_comment = driver.find_elements_by_css_selector(".entry.unvoted")
                    print(f"found {len(the_comment)} comments.")
                    the_iter = 0

                    try:
                        for comment in the_comment:
                            tagline = comment.find_element_by_class_name('tagline')
                            score = ""
                            time_posted = ""
                            text = ""
                            permalink = ""

                            try:
                                time_posted = tagline.find_element_by_tag_name(
                                    'time').get_attribute('title')
                            except:
                                print("Couldn't get time.")
                            else:
                                print(f"Got time {time_posted}")
                            try:
                                text = comment.find_element_by_class_name(
                                    'md').find_element_by_css_selector(
                                    'p').text
                            except:
                                print("Couldn't get text")
                            else:
                                print(f"Got text {textwrap.shorten(text, width=20)}")

                            try:
                                score = tagline.find_element_by_css_selector(".score.unvoted").text
                            except:
                                print("Couldn't get score")
                            else:
                                print(f"Got score {score}")
                            try:
                                permalink = comment.find_element_by_class_name(
                                    'bylink').get_attribute(
                                    "href")
                            except:
                                print("Couldn't get link.")
                            else:
                                print(f"Got link {permalink}")

                            key_phrase = ""

                            try:
                                r = Rake()
                                r.extract_keywords_from_text(text)
                                key_phrase = r.get_ranked_phrases()[0]
                                print(f"keyphrase {key_phrase}")
                            except:
                                print("Error getting keyphrase")

                            country_post = ""
                            city_post = ""

                            try:
                                country_post = country if bool(pattern_country.search(text)) else ""
                                city_post = f"{city}, {city_country}" if bool(
                                    pattern_city.search(text)) else ""
                            except:
                                print("Error getting city and country for post")

                            row = [(False, str(time_posted),
                                    str(score),
                                    str(permalink), "",
                                    str(text), str(key_phrase), str(city_post),
                                    str(country_post),
                                    str(url.split("/")[-3]), str(query))]

                            print(f"inner row {row}")

                            error = client.insert_rows(table, row)

                            if not error:
                                print(f"Row number {row_num} inserted.")
                                row_num += 1
                                del row
                                del error
                            else:
                                print(error)

                            del time_posted, tagline, the_comment, the_result, text, score, permalink, country_post,\
                                row, thread_id, \
                                city_post, r, error, query
                    except:
                        print("Scrape failed.")
                        continue
                except:
                    print("Url get failed")
                    continue

        except:
            print("This url failed")
            continue
        del urls
    driver.close()
    driver.quit()


if __name__ == "__main__":
    get_google_reddit_tap_water(int(sys.argv[1]))
