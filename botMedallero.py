#!/usr/bin/env python

import logging
import os
import pickle
import requests
import sys

from bs4 import BeautifulSoup
from socialModules.configMod import *


# https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-by-sport-spain.htm
# https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-by-sport-italy.htm

# text = soup.select('a[title*="Athlete Profile"]')
# print(text)
# text = soup.select('a[title*="Results"]')
# print(text)



# files = ['/tmp/noc-medalist-by-sport-spain.htm',
#         '/tmp/noc-medalist-by-sport-italy.htm',
#         '/tmp/noc-medalist-by-sport-germany.htm',
#         '/tmp/noc-medalist-by-sport-france.htm',
#         ]

medals = ['🥇', '🥈', '🥉']

url = 'https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-by-sport-spain.htm'
url = 'https://olympics.com/en/paris-2024/medals'

urlCountry = 'https://olympics.com/en/paris-2024/profile/china'

def nameFile():
    return os.path.expanduser('~/.mySocial/data/spain.json')

def getData():
    try:
        with open(nameFile(), 'rb') as f:
            data = pickle.load(f)
    except:
        data = []

    req = urllib.request.Request(url, data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36' })
    result = urllib.request.urlopen(req)
    res = result.read()
    logging.debug(f"Result: {res}")
    soup = BeautifulSoup(res, "lxml")
    logging.info(f"Soup: {soup}")

    #p2024-main-content > div.emotion-srm-uzcajx > div.emotion-srm-b12ho6 > div:nth-child(2) > div > div:nth-child(2) > div > div > div > div
    selection = soup.find_all(attrs={'data-testid': "noc-row"})
    print(f"Sel: {selection}")
    print(f"Len Sel: {len(selection)}")

    for row in selection:
        name = row.find(attrs={'class':"elhe7kv5 emotion-srm-uu3d5n"})
        print(f"Name: {name.text}")
        medals = row.find_all(attrs={'class':'e1oix8v91 emotion-srm-81g9w1'})
        print(f"Medals: {medals[0].text} {medals[1].text} {medals[2].text}")

    urlMedal='https://olympics.com/en/paris-2024/medals/medallists'
    req = urllib.request.Request(urlMedal, data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36' })
    result = urllib.request.urlopen(req)
    res = result.read()
    logging.debug(f"Result: {res}")
    soup = BeautifulSoup(res, "lxml")
    logging.info(f"Soup: {soup}")

    return selection, data

def printResults(msg, mode):
    if mode == 'test':
        dsts = {
            "twitter": "fernand0Test",
            "telegram": "testFernand0",
            "facebook": "Fernand0Test",
        }
    else:
        dsts = {"twitter":"medalleroESP"}


    for dst in dsts:
        print(dst)
        api = getApi(dst, dsts[dst])
        print(api, dsts[dst])
        res = api.publishPost(msg, "", "")
        print(res)

def main():
    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(message)s"
    )
    newData = False

    mode = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '-t':
            mode = 'test'

    text, data = getData()

    count = [0, 0, 0]

    for i in range(int(len(text)/4)):
        j = i*4
        field1=text[j+0].contents[1]
        if field1.find_all('span'):
            field1 = field1.find_all('span')[1].text
        else:
            field1 = field1.text
        field2=text[j+1].contents[1]['title'].split(' - ')[1]
        field3=text[j+2].text[1:]
        field4=text[j+3].contents[1]['alt']
        pos = int(field4) - 1
        field4 = medals[pos]
        count[pos] = count[pos] + 1
        medal = (field1, field2, field3, field4)
        if (medal not in data):
            printResults(f"Nueva medalla: {medal[3]} {medal[0]} - "
                         f"{medal[1]} ({medal[2]})", mode)
            data.append(medal)
            newData = True
        else:
            print("No news")
    if newData:
        printResults(f"Total medallas:"
              f" {medals[0]}: {count[0]}"
              f" {medals[1]}: {count[1]}"
              f" {medals[2]}: {count[2]}", mode)
        with open(nameFile(), 'wb') as f:
            pickle.dump(data, f)


if __name__ == "__main__":
    main()
