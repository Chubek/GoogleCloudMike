import praw
import textwrap
import re
import datetime
pattern = re.compile(r"(?i)(?:\btap\b.*\bwater\b|\bwater\b.*\btap\b)")

reddit = praw.Reddit(client_id="o-ZP_mKBAwQJRQ",
                     client_secret="KCfO1wo6DVVfP8zAKVYWOP8KHEQ",
                     password="lasvegas",
                     user_agent="Water Safety Grab by /u/OceanLinerXLL",
                     username="OceanLinerXLL")

submission = reddit.submission(url="https://old.reddit.com/r/paris/comments/cak84x/can_i_drink_tap_water_in_paris/".replace("old", "www"))
print(f"Got submission with ID {submission.id} with title "
                                  f"{textwrap.shorten(submission.title, width=30)} with "
                                  f"keywords {pattern.search(submission.title)} and "
                                  f"selfpost {textwrap.shorten(submission.selftext, width=30)} with "
                                  f"keywords {pattern.search(submission.selftext)}")





print(datetime.datetime.fromtimestamp(submission.created_utc))