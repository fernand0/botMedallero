#!/usr/bin/env python

import json
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

medalsIcons = {'ME_GOLD':'🥇', 'ME_SILVER':'🥈', 'ME_BRONZE':'🥉'}

url = 'https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-by-sport-spain.htm'
url = 'https://olympics.com/en/paris-2024/medals'
url = 'https://olympics.com/en/paris-2024/medals/china'

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

    jsonD = soup.find_all(attrs={'type':'application/json'})
    # print(f'Json: {jsonD[0].contents[0]}')
    json_object = json.loads(jsonD[0].contents[0])
    # import pprint
    # pprint.pprint(f'Json: {json_object})')
    # pprint.pprint(f'Json: {json_object.keys()})')
    medals = json_object["props"]['pageProps']['initialMedals']
    medals = medals['medalStandings']['medalsTable'][0]['disciplines']
    medalsD = []
    for med in medals:
        aMed = med['medalWinners'][0]
        logging.debug(f"Med: {aMed}")
        medD=(aMed['eventDescription'],
              aMed['eventCategory'], 
              aMed['medalType'], 
              aMed['competitorDisplayName'])

        logging.info(f"Discipline: {medD}")
        medalsD.append(medD)
        
    # for row in selection:
    #     name = row.find(attrs={'class':"elhe7kv5 emotion-srm-uu3d5n"})
    #     print(f"Name: {name.text}")
    #     medals = row.find_all(attrs={'class':'e1oix8v91 emotion-srm-81g9w1'})
    #     print(f"Medals: {medals[0].text} {medals[1].text} {medals[2].text}")

    # urlMedal='https://olympics.com/en/paris-2024/medals/medallists'
    # req = urllib.request.Request(urlMedal, data=None,
    #                              headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36' })
    # result = urllib.request.urlopen(req)
    # res = result.read()
    # logging.debug(f"Result: {res}")
    # soup = BeautifulSoup(res, "lxml")
    # logging.info(f"Soup: {soup}")

    logging.info(f"Medals: {medalsD}")
    return medalsD, data

def printResults(msg, mode):
    if mode == 'test':
        dsts = {
            "twitter": "fernand0Test",
            "telegram": "testFernand0",
            # "facebook": "Fernand0Test",
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

    for i, medal in enumerate(text):
        if medal[2] == 'ME_GOLD':
            count[0] = count[0] + 1
        elif medal[2] == 'ME_SILVER':
            count[1] = count[1] + 1
        elif medal[2] == 'ME_BRONZE':
            count[2] = count[2] + 1

        print(f"Disc: {medal}")
        if (medal not in data):
            printResults(f"Nueva medalla: {medalsIcons[medal[2]]} "
                         f"{medal[3]} - {medal[0]} ({medal[1]})", mode)
            data.append(medal)
            newData = True
        else:
            print("No news")
    if newData:
        printResults(f"Total medallas:"
              f" {medalsIcons['ME_GOLD']}: {count[0]}"
              f" {medalsIcons['ME_SILVER']}: {count[1]}"
              f" {medalsIcons['ME_BRONZE']}: {count[2]}", mode)
        with open(nameFile(), 'wb') as f:
            pickle.dump(data, f)


if __name__ == "__main__":
    main()
