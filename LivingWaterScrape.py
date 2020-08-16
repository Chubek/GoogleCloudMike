from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
from googleapiclient.discovery import build
from lxml.html.soupparser import fromstring
import re

index_start_file = open("index_start.txt", "r+")
done_urls_file = open("done_urls.txt", "r+")

index_start = [line.strip().split(";") for line in index_start_file.readlines()]
done_urls = [url.strip() for url in done_urls_file.readlines()]

ns = {"re": "http://exslt.org/regular-expressions"}

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    'client_secrets.json',
    scopes=scopes
)

gc = gspread.authorize(credentials)

sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Eg5cF8BCjwZe7rUu5U8m6qckkbCaZHF-jsbk7whTWfI/")

cities_sheet = sh.worksheet("Cities")
countries_sheet = sh.worksheet("Countries")

cities = cities_sheet.get_all_values()
countries = countries_sheet.get_all_values()
client = bigquery.Client.from_service_account_json('client_secrets.json')
table = client.get_table("cydtw-site.living_water.tap_water_living_water")
SEARCH_ENGINE_ID = "8038b946b9a62a518"
API_KEY = "AIzaSyA7BzGkhk5iJdWpkfFDJQcywUsFv0s1SqE"

service = build("customsearch", "v1", developerKey=API_KEY)

options = Options()
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument('headless')
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--remote-debugging-port=9222')
driver = webdriver.Chrome(executable_path="./chromedriver", options=options)

wrap_num = lambda num: 0 if num == 90 else num

city_marker = int(index_start[-1][0])

for city, country in cities[int(index_start[-1][0]):]:
    urls = []
    city_marker += 1
    for i in range(int(index_start[-1][1]), 100, 10):
        index_start_file.write(f"\n{city_marker};{wrap_num(i)}")
        print(f"Checking {city_marker};{i}")
        query = f"(tap AND water) AND ({city} OR {country})"
        the_result = service.cse().list(q=query,
                                        start=i,
                                        cx=SEARCH_ENGINE_ID).execute()

        pattern = re.compile(rf"(tap.water).(.*{city})|(.quality|.safety)")

        try:
            for item in the_result.get("items"):
                if bool(pattern.search(item.get('link'))) and item.get('link') not in done_urls:
                    urls.append(item.get('link'))
        except:
            continue

    print(f"Got {len(urls)} urls")

    for url in urls:
        print(f"Getting {url}")

        done_urls.append(url)
        done_urls_file.write(f"\n{url}")

        driver.get(url)

        root = fromstring(driver.page_source)

        tag_contains_pre = ""
        tag_contains_p = ""
        tag_contains_li = ""
        tag_contains_post = ""

        try:
            element_main_p = root.xpath(
                r'//p[re:match(.,"\btap\b.*\bwater\b|\bwater\b.*\btap\b", "i")]', namespaces=ns)
            element_pre_p = root.xpath(
                r'//p[re:match(.,"\btap\b.*\bwater\b|\bwater\b.*\btap\b", "i")]/preceding-sibling::p', namespaces=ns)
            element_fll_p = root.xpath(
                r'//p[re:match(.,"\btap\b.*\bwater\b|\bwater\b.*\btap\b", "i")]/following-sibling::p', namespaces=ns)

            for el in element_main_p:
                tag_contains_p += f"{el.text}\n\n\n"
            for el in element_pre_p:
                tag_contains_pre += f"{el.text}\n\n\n"
            for el in element_fll_p:
                tag_contains_post += f"{el.text}\n\n\n"

            if tag_contains_p:
                client.insert_rows(table, [(url, tag_contains_pre, tag_contains_p, tag_contains_post, "p", query)])

        except:
            print("No p")

        try:
            element_main_li = root.xpath(
                r'//li[re:match(.,"\btap\b.*\bwater\b|\bwater\b.*\btap\b", "i")]', namespaces=ns)
            element_pre_li = root.xpath(
                r'//li[re:match(.,"\btap\b.*\bwater\b|\bwater\b.*\btap\b", "i")]/preceding-sibling::li', namespaces=ns)
            element_fll_li = root.xpath(
                r'//li[re:match(.,"\btap\b.*\bwater\b|\bwater\b.*\btap\b", "i")]/following-sibling::li', namespaces=ns)

            for el in element_main_li:
                tag_contains_li += f"{el.text}\n\n\n"
            for el in element_pre_li:
                tag_contains_pre += f"{el.text}\n\n\n"
            for el in element_fll_li:
                tag_contains_post += f"{el.text}\n\n\n"

            if tag_contains_li:
                client.insert_rows(table, [(url, tag_contains_pre, tag_contains_li, tag_contains_post, "li", query)])
        except:
            print("No li")

        del element_fll_li, element_fll_p, element_main_p, element_main_li, \
            element_pre_p, element_pre_li, tag_contains_p, tag_contains_li, tag_contains_post, tag_contains_pre, root

driver.close()
driver.quit()