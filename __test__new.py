import pandas as pd
import re

df = pd.read_csv("reddit.csv")

repl = lambda _r: "https://reddit.com" + _r.group(0)

repl_comma = lambda _r: _r.group(0)[:-1]

pattern_old = r"https://old.reddit.com/[a-z]+"

pattern_no_reddit = r"^\/[a-z]((\/\w+)+|\/?)"

pattern_comma_at_the_end = r"(?:[a-zA-Z]+,|,[a-z]+,?)"

df["Link"] = df["Link"].str.replace(pattern_old, "https://reddit.com", regex=True)

df["Link"] = df["Link"].str.replace(pattern_no_reddit, repl, regex=True)

df["Countries"] = df["Countries"].str.replace(pattern_comma_at_the_end, repl_comma, regex=True)
df["Cities"] = df["Cities"].str.replace(pattern_comma_at_the_end, repl_comma, regex=True)

df.to_csv("new_reddit.csv")
