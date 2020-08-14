from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from google.cloud import bigquery

GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google-chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

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
options.binary_location = GOOGLE_CHROME_PATH
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

driver.get("https://www.google.com/search?q=tap+water&num=100&as_sitesearch=worldtravelguide.net")

urls = []

r_urls_first = driver.find_elements_by_xpath("//div[@class = 'r']/a")

for r_url in r_urls_first:
    urls.append(r_url.get_attribute("href"))

driver.find_element_by_xpath("//a[@id = 'pnnext']").click()

r_urls_second = driver.find_elements_by_xpath("//div[@class = 'r']/a")

for r_url in r_urls_second:
    urls.append(r_url.get_attribute("href"))


client = bigquery.Client.from_service_account_json('client_secrets.json')
table = client.get_table("cydtw-site.analytics_data_pre.wtg_tap_water")

for url in urls:
    try:
        driver.get(url)

        try:
            post = driver.find_element_by_xpath("//h2[text() = 'Food and Drink']/following::p")
            client.insert_rows(table, [(url, post.text)])
        except:
            continue
    except:
        continue


driver.close()
driver.quit()
