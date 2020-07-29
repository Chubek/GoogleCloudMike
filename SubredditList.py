from bs4 import BeautifulSoup
import requests
import re
import praw

reddit = praw.Reddit(client_id="o-ZP_mKBAwQJRQ",
                     client_secret="KCfO1wo6DVVfP8zAKVYWOP8KHEQ",
                     password="lasvegas",
                     user_agent="Water Safety Grab by /u/OceanLinerXLL",
                     username="OceanLinerXLL")


page = reddit.subreddit("ListOfSubreddits").wiki["listofsubreddits"]


soup = BeautifulSoup(page.content_html, "html.parser")

all_as = soup.find_all('a')

pattern = re.compile("\/r\/[a-z]+")

sub_list = []

file = open("subreddits_list.txt", "w")

for a in all_as:
    text = a.get_text()
    print(text)
    if pattern.match(text):
        sub_list.append(text.replace("/r/", ""))





