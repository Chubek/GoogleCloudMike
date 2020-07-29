import requests
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import httplib2
from google.cloud import bigquery
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from gspread_formatting.dataframe import format_with_dataframe
from gspread_formatting import format_cell_ranges, CellFormat
from google.cloud import bigquery
import re


class AhrefsClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def request_backlinks(self, target, mode, limit, output):
        url = f"https://apiv2.ahrefs.com?token={self.api_key}&target={target}&limit={limit}&output={output}&from" \
              f"=backlinks&mode={mode}"
        print(url)
        req = requests.get(url)

        return req.content, req.status_code

    def request_refdomains(self, target, mode, limit, output):
        url = f"https://apiv2.ahrefs.com?token={self.api_key}&target={target}&limit={limit}&output={output}&from" \
              f"=refdomains&mode={mode}"
        req = requests.get(url)

        return req.content, req.status_code

    def request_urlrating(self, target, mode, limit, output):
        url = f"https://apiv2.ahrefs.com?token={self.api_key}&target={target}&limit={limit}&output={output}&from" \
              f"=domain_rating&mode={mode}"
        req = requests.get(url)

        return req.content, req.status_code


class AnalyticsAPI:

    def __init__(self, client_secret_json):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret_json, [
            'https://www.googleapis.com/auth/analytics.readonly'])

        http = credentials.authorize(httplib2.Http())
        self.service = build('analytics', 'v4', http=http,
                             discoveryServiceUrl='https://analyticsreporting.googleapis.com/$discovery/rest')
        self.res = None

    def request_data_and_get(self, view_id, start_date, end_date, regex, row_limit):
        self.res = self.service.reports().batchGet(
            body={
                'reportRequests': [
                    {
                        'viewId': view_id,
                        'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                        'metrics': [{'expression': 'ga:sessions'}, {'expression': "ga:users"},
                                    {'expression': 'ga:percentNewSessions'}, {'expression': 'ga:newUsers'},
                                    {'expression': 'ga:pageviews'}, {'expression': 'ga:avgSessionDuration'},
                                    {'expression': 'ga:goalConversionRateAll'}, {'expression': 'ga:goalCompletionsAll'},
                                    {'expression': 'ga:goalCompletionsAll'}, {'expression': 'ga:goalValueAll'}
                                    ],
                        'dimensions': [{"name": "ga:pagePath"}, {"name": "ga:userType"}],
                        'orderBys': [{"fieldName": "ga:sessions", "sortOrder": "DESCENDING"}],
                        "filtersExpression": f"ga:pagePath={regex}",
                        'pageSize': row_limit
                    }]
            }
        ).execute()

        return self.res


class ConsoleAPI:

    def __init__(self, client_secret_json):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret_json, [
            'https://www.googleapis.com/auth/webmasters.readonly'])

        http = credentials.authorize(httplib2.Http())
        self.service = build('webmasters', 'v4', http=http)
        self.res = None

    def request_data_and_get(self, start_date, end_date, uri, row_limit):
        self.res = self.service.searchanalytics().query(
            siteUrl=uri, body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': row_limit
            }).execute()

        return self.res


class SheetsExport:

    def __init__(self, client_secret_json, worksheet_name, create_worksheet, share_email, worksheet_index_title):
        gc = gspread.service_account(filename=client_secret_json)

        if not create_worksheet:
            sh = gc.open(worksheet_name)
        else:
            sh = gc.create(worksheet_name)
            sh.share(share_email, perm_type='user', role='writer')

        digit = re.compile("""\d+""")

        if digit.match(worksheet_index_title):
            self.worksheet = sh.get_worksheet(worksheet_index_title)
        else:
            self.worksheet = sh.worksheet(worksheet_index_title)

    def insert_data_into_worksheet(self, dataframe):
        set_with_dataframe(self.worksheet, dataframe)
        format_with_dataframe(self.worksheet, dataframe, include_column_header=True)

    def format_cell(self, cell_addresses, color):

        fmt = CellFormat(
            backgroundColor=color(color[0], color[1], color[2]),
        )

        ranges = []

        for cell_address in cell_addresses:
            ranges.append((cell_address, fmt))

        format_cell_ranges(self.worksheet, [*ranges])


class BigQueryExport:

    def __init__(self, client_secrets_json):
        self.client = bigquery.Client.from_service_account_json(client_secrets_json)

        self.res = None

    def insert_data_into_bigquery(self, rows_to_insert, table_route):

        self.res = self.client.insert_rows(self.client.get_table(table_route), rows_to_insert)

        return self.res


class MainAPI:

    def __init__(self, client_secret, ahrefs_api_key):

        self.ahrefsClient = AhrefsClient(ahrefs_api_key)
        self.analyticsClient = AnalyticsAPI(client_secret)
        self.searchConsoleClient = ConsoleAPI(client_secret)
        self.sheetsExport = SheetsExport(client_secret)
        self.bigQueryExport = BigQueryExport(client_secret)

        self.ahrefsData = None
        self.analyticsData = None
        self.searchConsoleData = None

