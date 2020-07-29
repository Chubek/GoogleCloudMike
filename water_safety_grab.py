from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import httplib2
from google.cloud import bigquery


def grab_data():
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', [
        'https://www.googleapis.com/auth/analytics.readonly'])

    http = credentials.authorize(httplib2.Http())
    service = build('analytics', 'v4', http=http,
                    discoveryServiceUrl=('https://analyticsreporting.googleapis.com/$discovery/rest'))

    response = service.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': '200898948',
                    'dateRanges': [{'startDate': 'yesterday', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:sessions'}, {'expression': "ga:users"}],
                    'dimensions': [{"name": "ga:pagePath"}, {"name": "ga:userType"}],
                    'orderBys': [{"fieldName": "ga:sessions", "sortOrder": "DESCENDING"}],
                    'pageSize': 10000
                }]
        }
    ).execute()

    client = bigquery.Client.from_service_account_json('client_secrets.json')
    rows_to_insert = []

    for report in response.get('reports', []):

        rows = report.get('data', {}).get('rows', [])

        for row in rows:
            rows_to_insert.append((*row['dimensions'], *row["metrics"][0]["values"]))

    errors = client.insert_rows(client.get_table("cydtw-site.analytics_data_pre.session_user"), rows_to_insert)
    if not errors:
        print("New rows have been added.")


if __name__ == "__main__":
    grab_data()






