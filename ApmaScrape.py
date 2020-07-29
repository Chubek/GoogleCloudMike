from bs4 import BeautifulSoup
import requests
import pandas as pd

name_address = []
phone_fax_web = []
education_qualification_certification = []

soups = []

for i in range(20, 11428, 20):
    print(i)
    req = requests.get(
        f"https://www.apma.org/Directory/FindAPodiatrist.cfm?Compact=0&FirstName=&LastName=&City=&State=&Zip=&Country=United+States&startrow=1&endrow={i}")
    soups.append(BeautifulSoup(req.content, 'html.parser'))


print("-------------------------------------------------------------------------------------")


for i, soup in enumerate(soups):
    print(i)
    for tr in soup.find_all('tr')[2:]:
        tds = tr.find_all('td')
        name_address.append(tds[0].get_text())
        phone_fax_web.append(tds[1].get_text())
        education_qualification_certification.append(tds[2].get_text())


print("-------------------------------------------------------------------------------------")



df = pd.DataFrame({'Name/Address': name_address,
                   'Phone/Fax/Web': phone_fax_web,
                   'Education, Qualifications, and Certification': education_qualification_certification})

df.to_csv("apma.csv")