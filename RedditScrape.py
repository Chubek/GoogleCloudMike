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
from google.cloud import bigquery

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
    client = bigquery.Client.from_service_account_json('client_secrets.json')

    time = ['all', 'day', 'month', 'week', 'year']
    time_frame = time[random.randint(0, len(time) - 1)]

    page = reddit.subreddit("ListOfSubreddits").wiki["listofsubreddits"]

    soup = BeautifulSoup(page.content_html, "html.parser")

    all_as = soup.find_all('a')

    pattern = re.compile("\/r\/[a-z]+")

    sub_list = []

    for a in all_as:
        text = a.get_text()
        if pattern.match(text):
            sub_list.append(text.replace("/r/", ""))

    print(f"Searching in timeframe {time_frame}")

    submissions_list = []

    for sub in sub_list[400:]:
        print(f"Searching sub {sub} from a list of {len(sub_list)}")
        submissions_list.append(reddit.subreddit(sub).search("tap AND water", time_filter='all'))
        print(f"Search Done!")

    pattern = re.compile(r"(?i)(?:\btap\b.*\bwater\b|\040tap\bwater\.)")
    result_num = 3055

    for i, submissions in enumerate(submissions_list):
        try:
            for j, submission in enumerate(submissions):
                print(f"Checking submission {j} of {i}")
                submission.comments.replace_more(limit=0)
                for comment in submission.comments:
                    if isinstance(comment, MoreComments):
                        continue
                    if bool(pattern.search(comment.body)):
                        result_num += 1
                        results = (
                            {"query_result": comment.body,
                             "levenshtein_distance": nltk.edit_distance("tap water", comment.body),
                             "cities_mentioned": "",
                             "countries_mentioned": ""})

                        try:
                            rake = Rake(ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO)
                            rake.extract_keywords_from_text(results["query_result"])
                            phrases = rake.get_ranked_phrases()
                            results["key_phrases"] = phrases[1:]
                            results["main_key_phrase"] = phrases[0]
                        except:
                            print("Error with Rake")
                            continue

                        try:
                            for city in cities[1:]:

                                pattern_city = re.compile(rf"\b(?=\w)\b{city[0]}\b|\b{city[0].lower()}\b(?!\w)")
                                pattern_nyc = re.compile(rf"\b(?=\w)\bNew\040York\b|\bnew\040york\b(?!\w)")

                                if bool(pattern_city.search(results["query_result"])):
                                    if city[0].strip() == "York":
                                        if bool(pattern_nyc.search(results["query_result"])) and not bool(
                                                pattern_nyc.search(results["cities_mentioned"])):
                                            results["cities_mentioned"] = results[
                                                                              "cities_mentioned"] + f"New York, New " \
                                                                                                    f"York\n "
                                        continue
                                    if not bool(pattern_city.search(results["cities_mentioned"])):
                                        results["cities_mentioned"] = results[
                                                                          "cities_mentioned"] + f"{city[0]}, " \
                                                                                                f"{city[1]}\n "
                        except:
                            print("Error with City")
                            continue

                        try:
                            for country in countries[1:]:

                                pattern_country = re.compile(
                                    rf"\b(?=\w)\b{country[0]}\b|\b{country[0].lower()}\b(?!\w)")

                                if bool(pattern_country.search(results["query_result"])):
                                    if not bool(pattern_country.search(results["countries_mentioned"])):
                                        results["countries_mentioned"] = results[
                                                                             "countries_mentioned"] + f"{country[0]}\n"
                        except:
                            print("Problem with country")
                            continue

                        error = client.insert_rows(client.get_table("cydtw-site.reddit_tap_water.tap_water_reddit"),
                                                   [(results["query_result"], int(results["levenshtein_distance"]),
                                                     results["cities_mentioned"], results["countries_mentioned"],
                                                     ", ".join(results["key_phrases"]), results["main_key_phrase"])])

                        if not error:
                            print(f"Row {result_num} inserted.")
                        else:
                            print(error)
        except:
            print("The whole thing failed.")
            continue

    # letters = string.ascii_lowercase
    # result_str = ''.join(random.choice(letters) for i in range(5))

    # worksheet_name = f"{str(datetime.datetime.now().date())} - {result_str}"

    # sh_final = gc.open_by_url(
    #   "https://docs.google.com/spreadsheets/d/1vBDJzaPKGS7-aEBmn0ZfgG6PiNNoVXjMjZhNZaGQCaw/edit#gid=0")
    # worksheet_today = sh_final.add_worksheet(
    # worksheet_name, rows="60000",
    # cols="8")

    # print(f"Created worksheet {worksheet_name}")

    # df = pd.DataFrame.from_records(results)
    # set_with_dataframe(worksheet_today, df)
    # format_with_dataframe(worksheet_today, df, include_column_header=True)

    print("Done!")


if __name__ == "__main__":
    scrape_reddit()
