from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import json
import ast
import requests
import praw
import re
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

nltk.download('stopwords')
nltk.download('punkt')


def get_google_reddit_tap_water():
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
    table = client.get_table("cydtw-site.reddit_tap_water.reddit_google_tap_water")
    SEARCH_ENGINE_ID = "006168594918175601863:t8oecxasips"
    API_KEY = "AIzaSyANjD56fSSSu8kc3YRWkW1OV6QyR9ZFwVA"
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

    query_num = 0
    row_num = 0
    for city_, country in itertools.zip_longest(cities[50:], countries[150:]):
        city = city_[0]
        city_country = city_[1]

        country = ""

        try:
            country = country[0]
        except:
            print("Country is None")

        query = f"tap AND water AND ({city} OR {country})"
        print(f"Searching for {query}. Query number: {query_num}")

        the_result = None

        for i in range(20):
            try:
                the_result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID).execute()
                query_num += 1
            except:
                print(f"Search failed. Retrying {i}/20")
            else:
                print(f"Skipping {city} and {country}")
                continue

        urls = []
        url_pattern = re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
        try:
            for item in the_result.get("items"):
                url = item.get("link").replace("www", "old")
                if bool(url_pattern.search(url)):
                    urls.append(url)
                    print(f"url {url} added")
        except:
            print("No items.")
            continue

        for i in range(10):
            try:
                for url in urls:
                    print(f"Operating on {url}")
                    driver.get(url)

                    print(f"Page title: {driver.title}")

                    pattern_country = re.compile(rf"(?i)(?:\b{country}\b)")
                    pattern_city = re.compile(rf"(?i)(?:\b{city}\b)")

                    try:
                        submission = reddit.submission(url=url.replace("old", "www"))
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
                                submission.permalink, submission.title,
                                submission.selftext, key_phrase, city_contains,
                                country_contains,
                                thread_id, query)]

                        print(f"row is {row}")

                        error = client.insert_rows(table, row)
                        if not error:
                            print(f"Row number {row_num} inserted")
                            row_num += 1
                        else:
                            print(error)

                        the_comment = driver.find_elements_by_css_selector(".entry.unvoted")
                        print(f"found {len(the_comment)} comments.")
                        the_iter = 0

                        for n in range(submission.num_comments):
                            i_iter = 0
                            try:
                                for j, comment in enumerate(the_comment[the_iter:]):
                                    i_iter = j

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

                                    print(f"Got time {time_posted}")
                                    try:
                                        text = comment.find_element_by_class_name(
                                            'md').find_element_by_css_selector(
                                            'p').text
                                    except:
                                        print("Couldn't get text")

                                    print(f"Got text {textwrap.shorten(text, width=20)}")

                                    try:
                                        score = tagline.find_element_by_css_selector(".score.unvoted").text
                                    except:
                                        print("Couldn't get score")

                                    print(f"Got score {score}")
                                    try:
                                        permalink = comment.find_element_by_class_name(
                                            'bylink').get_attribute(
                                            "href")
                                    except:
                                        print("Couldn't get link.")

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

                                    row = [(False, time_posted,
                                            score,
                                            permalink, "",
                                            text, key_phrase, city_post,
                                            country_post,
                                            thread_id, query)]

                                    print(f"inner row {row}")

                                    error = client.insert_rows(table, row)

                                    if not error:
                                        print(f"Row number {row_num} inserted.")
                                        row_num += 1
                                    else:
                                        print(error)

                                    del time_posted, text, score, permalink, country_post, row, thread_id, \
                                        city_post, r, error, query

                            except:
                                print(f"Operation expired. Reconnecting for {n}/{submission.num_comments}")
                                the_comment = driver.find_elements_by_css_selector(".entry.unvoted")
                                the_iter = i_iter
                                continue
                            else:
                                break
                    except:
                        print('Submission get failed. Retrying.')
                        continue

            except:
                print("Url get failed. Continuing")
                continue
            else:
                break

        del urls, the_result, submission

        print("This done.")

        driver.close()
        driver.quit()

if __name__ == "__main__":
    get_google_reddit_tap_water()
