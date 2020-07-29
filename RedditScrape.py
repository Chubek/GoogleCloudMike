import praw
from rake_nltk import Metric, Rake
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread_formatting.dataframe import format_with_dataframe
import re
import datetime
import random
from praw.models import MoreComments
import string
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from bs4 import BeautifulSoup


def scrape_reddit():
    reddit = praw.Reddit(client_id="o-ZP_mKBAwQJRQ",
                         client_secret="KCfO1wo6DVVfP8zAKVYWOP8KHEQ",
                         password="lasvegas",
                         user_agent="Water Safety Grab by /u/OceanLinerXLL",
                         username="OceanLinerXLL")

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

    results = []

    time = ['all', 'day', 'month', 'week', 'year']
    time_frame = time[random.randint(0, len(time) - 1)]

    page = reddit.subreddit("ListOfSubreddits").wiki["listofsubreddits"]

    soup = BeautifulSoup(page.content_html, "html.parser")

    all_as = soup.find_all('a')

    pattern = re.compile("\/r\/[a-z]+")

    sub_list = []

    for a in all_as:
        text = a.get_text()
        print(text)
        if pattern.match(text):
            sub_list.append(text.replace("/r/", ""))

    print(f"Searching in timeframe {time_frame}")

    submissions = reddit.subreddit("all").search("tap AND water", time_filter=time_frame)
    print(f"Search Done!")

    pattern = re.compile(r"(?i)(?:\040tap\040.*\040water\040|\040tap\040water\.)")

    for submission in submissions:
        submission.comments.replace_more(limit=0)
        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue
            if bool(pattern.search(comment.body)):
                results.append(
                    {"query_result": comment.body,
                     "levenshtein_distance": nltk.edit_distance("tap water", comment.body)})

    print(f"Found {len(results)} queries containing the phrase.")

    for res in results:
        rake = Rake(ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO)
        rake.extract_keywords_from_text(res["query_result"])
        phrases = rake.get_ranked_phrases()
        res["key_phrases"] = phrases[1:]
        res["main_key_phrase"] = phrases[0]

    for city in cities[1:]:

        pattern_text_city = rf"\b(?=\w){city[0]}|{city[0].lower()}\b(?!\w)"
        print(f"Searching for city {city[0]}, {city[1]} with pattern {pattern_text_city}")

        pattern_city = re.compile(rf"\b(?=\w){city[0]}|{city[0].lower()}\b(?!\w)")

        for res in results:
            res["cities_mentioned"] = ""

            if bool(pattern_city.search(res["query_result"])):
                print(f"City found! {city[0]}")
                res["cities_mentioned"] = res["cities_mentioned"] + f"{city[0]}, {city[1]}\n"

    for country in countries[1:]:

        pattern_text_country = rf"\b(?=\w){country[0]}|{country[0].lower()}\b(?!\w)"
        print(f"Searching for country {country[0]} with pattern {pattern_text_country}")

        pattern_country = re.compile(rf"\b(?=\w){country[0]}|{country[0].lower()}\b(?!\w)")

        for res in results:
            res["countries_mentioned"] = ""

            if bool(pattern_country.search(res["query_result"])):
                print(f"Country found! {country[0]}")
                res["countries_mentioned"] = res["countries_mentioned"] + f"{country[0]}\n"

    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(5))

    worksheet_name = f"{str(datetime.datetime.now().date())} - {result_str}"

    sh_final = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1vBDJzaPKGS7-aEBmn0ZfgG6PiNNoVXjMjZhNZaGQCaw/edit#gid=0")
    worksheet_today = sh_final.add_worksheet(
        worksheet_name, rows="1500",
        cols="20")

    print(f"Created worksheet {worksheet_name}")

    df = pd.DataFrame.from_records(results)
    set_with_dataframe(worksheet_today, df)
    format_with_dataframe(worksheet_today, df, include_column_header=True)

    print("Done!")


if __name__ == "__main__":
    scrape_reddit()