from google.cloud import bigquery

client = bigquery.Client.from_service_account_json('client_secrets.json')

error = client.insert_rows(client.get_table("cydtw-site.reddit_tap_water.tap_water_reddit"),
                   [("22", 22,
                     "2323", "323423",
                     "232", "323")])





print(error)