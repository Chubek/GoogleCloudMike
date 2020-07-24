from google.cloud import bigquery
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread_formatting.dataframe import format_with_dataframe


def run_grab(sheet_name, create_sheet, email):
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

    print("ff", create_sheet)

    if create_sheet:
        try:
            sh = gc.create(sheet_name)
            sh.share(email, perm_type='user', role='writer')
        except NameError as e:
            print(e)
            return "Error creating sheet."
    else:
        try:
            sh = gc.open(sheet_name)
        except NameError as e:
            print(e)
            return "Error opening sheet."

    worksheet = sh.get_worksheet(0)

    records = []

    for row in client.list_rows(table):
        records.append(row)

    df = pd.DataFrame.from_records(records)
    set_with_dataframe(worksheet, df)

    try:
        format_with_dataframe(worksheet, df, include_column_header=True)
    except IOError as e:
        print(e)
        return "Error sending data to Google Sheets."

    return f"Successfully inserted records to worksheet {sheet_name}."


