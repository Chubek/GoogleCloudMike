from google.cloud import bigquery
import gspread
from google.oauth2.service_account import Credentials
import string
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread_formatting.dataframe import format_with_dataframe

def run_grab():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file(
        'client_secrets.json',
        scopes=scopes
    )

    client = bigquery.Client.from_service_account_json("client_secrets.json")

    table = client.get_table("cydtw-site.analytics_data_pre.session_user")

    gc = gspread.authorize(credentials)

    sh = gc.open("BigQuery Project")

    worksheet = sh.get_worksheet(0)

    letters = list(string.ascii_uppercase)

    records = []

    for row in client.list_rows(table):
        records.append(row)

    df = pd.DataFrame.from_records(records)
    set_with_dataframe(worksheet, df)
    format_with_dataframe(worksheet, df, include_column_header=True)


