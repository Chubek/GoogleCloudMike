from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import bigquery
from googleapiclient.discovery import build
from lxml.html.soupparser import fromstring
import re
import time
import threading
from google.cloud import logging
import pandas as pd


class ArticleForge:

    def __init__(self, main_kw, sub_kw):
        self.main_kw = main_kw
        self.sub_kw = sub_kw

        df_cookies = pd.read_csv("cookies-af-articleforge-com.txt", sep="\t", header=None)

        cookies_list = []

        for i in range(df_cookies.shape[0]):
            cookies_list.append({"name": df_cookies.loc[i, 5], "value": df_cookies.loc[i, 6]})

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
        options.add_argument('--window-size=1420,1080')
        self.driver = webdriver.Chrome(executable_path="./chromedriver", options=options)

    def run_auto(self, number):

        self.driver.get("https://af.articleforge.com/")

        for cookie in cookies_list:
            self.driver.add_cookie(cookie)

        time.sleep(10)

        self.driver.refresh()

        time.sleep(10)

        self.driver.find_element_by_xpath("//html/body/nav/div[1]/ul/li[1]/a").click()

        time.sleep(20)

        self.driver.find_element_by_xpath('//*[@id="keyword"]').send_keys("Jew's Harp")

        self.driver.find_element_by_xpath('//*[@id="sub_keywords"]').send_keys("Instrument\nMusic\nOcarina")

        self.driver.find_element_by_xpath('//*[@id="create_article_button"]').click()
        self.driver.find_element_by_xpath('//*[@id="create_article_button"]').click()

        time.sleep(30)

        while True:
            try:
                self.driver.find_element_by_xpath("//a[contains(@id, 'hyperlink_')]").click()
            except:
                continue
            else:
                time.sleep(20)

                artfile = open(f"article_{number}_{self.main_kw}.txt", "w")

                elem_article = self.driver.find_element_by_xpath('//*[@id="spintax-area-div-summernote"]')

                artfile.write(elem_article.text)

                artfile.close()

                break

    def close(self):
        self.driver.close()
        self.driver.quit()
