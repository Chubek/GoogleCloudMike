import gspread
from google.oauth2.service_account import Credentials
import requests
from bs4 import BeautifulSoup

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    'client_secrets.json',
    scopes=scopes
)

gc = gspread.authorize(credentials)

sh = gc.open("tech companies")

worksheet = sh.get_worksheet(0)

worksheet_companies = worksheet.get_all_values()

companies = [(company, "-".join(company[0]
                                .lower().split(" ").split(".")))
             for company in worksheet_companies]

file = open("urls_breezy.txt", "w")
failures = open("failures.txt", "w")

sh_list = gc.create('BreezyUrls')
sh_list.share('ihatemusic84@gmail.com', perm_type='user', role='writer')
sh_list.share('chubakbidpaa@gmail.com', perm_type='user', role='writer')
worksheet = sh_list.get_worksheet(0)

for i, company in enumerate(companies):
    print(i + 1)
    url = f"https://{company[1]}.breezy.hr"
    req = requests.get(url)
    if req.status_code == 200:
        soup = BeautifulSoup(url, "html.parser")

        if soup.find('h1', {"class": "polyglot"}).get_text() == "Our Openings":
            print(f"{url}")
            file.write(url)
            file.write("\n")
            worksheet.update_cell(i + 1, 2, company[0])
            worksheet.update_cell(i + 1, 1, url)
