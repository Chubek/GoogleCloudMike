from google.cloud import bigquery


client = bigquery.Client.from_service_account_json('client_secrets.json')

table = client.get_table("cydtw-site.reddit_tap_water.polished_table")

link = "/hello/world"

job = client.query(
    f"SELECT Cities, Countries FROM `cydtw-site.reddit_tap_water.polished_table` WHERE Link = '{link}'  LIMIT 1")

job.result()

row_num = 0

print(job)


for row in job:
    row_num += 1
    city_str = row[0]
    country_str = row[1]

print(row_num)