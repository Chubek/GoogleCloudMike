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

    print(f"Searching in timeframe {time_frame}")

    submissions = reddit.subreddit("all").search("tap AND water", time_filter=time_frame)
    print(f"Search Done!")
    pattern = re.compile("(?i)(?:\040tap\040.*\040water\040|\040tap\040water\\.)")

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

        print(f"Searching for city {city[0]}")

        for res in results:
            res["cities_mentioned"] = []
            for key_phrase in res["key_phrases"]:
                if city[0].strip() in key_phrase:
                    res["cities_mentioned"].append(city[0])

    for country in countries[1:]:

        print(f"Searching for country {country[0]}")

        for res in results:
            res["countries_mentioned"] = []
            for key_phrase in res["key_phrases"]:
                if country[0].strip() in key_phrase:
                    res["countries_mentioned"].append(country[0])

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