import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import datetime
import certifi
# pip install lxml

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.bep7j.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

URL = 'https://www.tagsfinder.com/ko-kr/stats/'
headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.232 Whale/2.10.124.26 Safari/537.36"}

today = datetime.datetime.today()       # prevent mongodb error (date.today())
dt = datetime.datetime(today.year, today.month, today.day) 

def extract_tags():
    tags = {}
    print(f'Scrapping tags...')
    result = requests.get(URL, headers=headers)
    soup = BeautifulSoup(result.text,'html.parser')
    results = soup.find_all("table")[0]
    result = results.find_all("tr")

    for i in result:
        tag = i.select_one('td>a').string.strip('#')
        tag_per = i.select_one('td.text-right').get_text(strip=True)
        tags[tag] = tag_per

    # print(tags)
    
    doc = {"today":dt, "tags": tags}
    print(doc)
    # db.tags.insert_one(doc)

    return doc

# extract_tags()
# print(db.tags.find_one({'today':dt})['tags'])
