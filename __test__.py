from google.cloud import bigquery
from difflib import SequenceMatcher
import datetime
client = bigquery.Client.from_service_account_json('client_secrets.json')

error = client.insert_rows(client.get_table("cydtw-site.reddit_tap_water.tap_water_reddit"),
                   [("22", 22,
                     "2323", "323423",
                     "232", "323")])





print(SequenceMatcher("hello", "hello").ratio())

print(datetime.date.fromordinal("Tue Jul 28 18:36:12 2020 UTC"))