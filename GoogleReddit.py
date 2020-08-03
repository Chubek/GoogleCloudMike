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

    SEARCH_ENGINE_ID = "006168594918175601863:t8oecxasips"
    API_KEY = "AIzaSyCjuHRi_hJDXGBsGKSO4nTaz5k4EQ4K1WI"
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

    for city in cities[1:]:
        city = city[0]
        city_country = city[1]
        for country in countries[1:]:
            country = country[0]
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

            try:
                for item in the_result.get("items"):
                    urls.append(item.get("link").replace("www", "old"))
            except:
                print("No items.")
                continue

            for i in range(50):
                try:
                    for url in urls:
                        print(f"Operating on {url}")
                        driver.get(url)
                        driver.find_element_by_name('user').send_keys("OceanLinerXLL")
                        driver.find_element_by_name('passwd').send_keys("lasvegas")
                        element_submit_button = driver.find_element_by_class_name('btn')
                        webdriver.ActionChains(driver).move_to_element(element_submit_button).click(
                            element_submit_button).perform()

                        rows = []

                        pattern = re.compile(rf"(?i)(?:\btap\b.*\bwater\b|\bwater\b.*\btap.\b{city}\b)")
                        pattern_country = re.compile(rf"(?i)(?:\b{country}\b)")
                        pattern_city = re.compile(rf"(?i)(?:\b{city}\b)")
                        submission = reddit.submission(url=url)
                        thread_id = ""

                        try:
                            if submission.is_self:
                                if bool(pattern.search(submission.selfpost)):
                                    thread_id = submission.id
                                    r = Rake()
                                    r.extract_keywords_from_text(submission.selfpost)

                                    country_contains = country if bool(pattern_country.search(submission.selfpost)) else ""

                                    rows.append(
                                        (True, datetime.datetime.fromtimestamp(submission.created_utc), submission.score,
                                        submission.permalink, submission.title,
                                        submission.selfpost, r.get_ranked_phrases()[0], f"{city}, {city_country}",
                                        country_contains,
                                        thread_id))

                                    the_comment = driver.find_elements_by_css_selector(".entry.unvoted")

                                    the_iter = 0

                                    while True:
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
                                                    time_posted = tagline.find_element_by_tag_name('time').get_attribute('title')
                                                except:
                                                    print("Couldn't get time.")

                                                print("Got time")
                                                try:
                                                    text = comment.find_element_by_class_name(
                                                    'md').find_element_by_css_selector(
                                                    'p').text
                                                except:
                                                    print("Couldn't get text")

                                                print("Got text")
                                                try:
                                                    score = tagline.find_element_by_css_selector(".score.unvoted").text
                                                except:
                                                    print("Couldn't get score")

                                                print("Got score!")
                                                try:
                                                    permalink = comment.find_element_by_class_name('bylink').get_attribute(
                                                        "href")
                                                except:
                                                    print("Couldn't get link.")

                                                print("Got link!")

                                                if score and time_posted and text and permalink:
                                                    r = Rake()
                                                    r.extract_keywords_from_text(text)

                                                    country_post = country if bool(pattern_country.search(text)) else ""
                                                    city_post = f"{city}, {city_country}" if bool(pattern_city.search(text)) else ""

                                                    rows.append((False, time_posted,
                                                         score,
                                                         permalink, "",
                                                         text, r.get_ranked_phrases()[0], city_post,
                                                         country_post,
                                                         thread_id))
                                        except:
                                            print("Operation expired. Reconnecting...")
                                            the_comment = driver.find_elements_by_css_selector(".entry.unvoted")
                                            the_iter = i_iter
                                            continue
                                        else:
                                            break


                                    try:
                                        error = client.insert_rows(
                                            client.get_table("cydtw-site.reddit_tap_water.reddit_google_tap_water"),
                                            rows)

                                        if not error:
                                            print("Rows inserted.")
                                    except:
                                        print("Insert unsuccessful")
                                        continue
                        except:
                            continue

                except:
                    print('Failed. Retrying.')
                    continue

                del rows, urls, the_result, submission

                print("This done.")

    driver.close()
    driver.quit()


if __name__ == "__main__":
    get_google_reddit_tap_water()