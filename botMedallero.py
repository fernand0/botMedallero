#!/usr/bin/env python

import json
import logging
import os
import pickle
import requests
import sys

from bs4 import BeautifulSoup
from socialModules.configMod import *


# Tokyo
#       https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-by-sport-spain.htm
#       https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-by-sport-italy.htm

#       files = ['/tmp/noc-medalist-by-sport-spain.htm',
#               '/tmp/noc-medalist-by-sport-italy.htm',
#               '/tmp/noc-medalist-by-sport-germany.htm',
#               '/tmp/noc-medalist-by-sport-france.htm',
#               ]

medalsIcons = {'ME_GOLD':'🥇', 'ME_SILVER':'🥈', 'ME_BRONZE':'🥉'}

# Paris 2024

# url = 'https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/noc-medalist-by-sport-spain.htm'
# url = 'https://olympics.com/en/paris-2024/medals'
urlCountry = 'https://olympics.com/en/paris-2024/profile/spain'
# url = 'https://olympics.com/en/paris-2024/medals/china'
url = 'https://olympics.com/en/paris-2024/medals/spain'


def nameFile():
    return os.path.expanduser('~/.mySocial/data/spain.json')

def getData(listing=False):
    try:
        with open(nameFile(), 'rb') as f:
            data = pickle.load(f)
    except:
        data = []

    medalsD = []
    try:
        #print(f"Url: {url}")
        req = urllib.request.Request(url, data=None,
                                     headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36' })
        result = urllib.request.urlopen(req)
        res = result.read()
        #print(res)
        logging.debug(f"Result: {res}")
        soup = BeautifulSoup(res, "lxml")
        logging.debug(f"Soup: {soup}")

        jsonD = soup.find_all(attrs={'type':'application/json'})
        json_object = json.loads(jsonD[0].contents[0])
        medals = json_object["props"]['pageProps']['initialMedals']
        medals = medals['medalStandings']['medalsTable']#[0]['disciplines']
        for med in medals:
            # print(f"Medallaa: {med}")
            if med['organisation'] == 'ESP':
                # print(f"Medalla: {med['disciplines'][0]}")
                for disc in med['disciplines']:
                    medd = disc
                    competition = disc['name']
                    logging.debug(f"Comp: {competition}")
                    for aMed in medd['medalWinners']:
                        aMed = medd['medalWinners'][0]
                        logging.debug(f"Med: {aMed}")
                        medD=(competition,
                              aMed['eventDescription'], 
                              aMed['medalType'], 
                              aMed['competitorDisplayName'])

                        logging.debug(f"Discipline: {medD}")
                        medalsD.append(medD)
                        if listing:
                            print(f"Medal: {medD}")
            
    except:
        print(f"No medals yet")

    logging.debug(f"Medals: {medalsD}")
    return medalsD, data

def printResults(msg, mode):
    if mode == 'test':
        dsts = {
            "twitter": "fernand0Test",
            "telegram": "testFernand0",
            # "facebook": "Fernand0Test",
        }
    else:
        dsts = {"twitter":"medalleroESP",
                "telegram": "testFernand0",
                "mastodon":"@medalleroESP@botsin.space",
                }

    msg = f"{msg} #paris2024"
    for dst in dsts:
        logging.info(f"Destination: {dst}")
        api = getApi(dst, dsts[dst])
        logging.info(f"Account: {api, dsts[dst]}")
        res = api.publishPost(msg, "", "")
        logging.info(f"Res: {res}")

def main():
    logging.basicConfig(
        stream=sys.stdout, 
        level=logging.INFO,
        format="%(asctime)s %(message)s"
    )
    newData = False

    mode = None
    listing = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '-t':
            mode = 'test' 
            logging.basicConfig( 
                                stream=sys.stdout, 
                                level=logging.DEBUG, 
                                format="%(asctime)s %(message)s"
                                )
        if sys.argv[1] == '-n':
            newData = True
        if sys.argv[1] == '-l':
            listing = True

    text, data = getData(listing)
    if listing:
        for med in data: 
            print(f"Med: {med}")
        return
    logging.debug(f"Data: {data}")
    logging.debug(f"Medal: {text}")

    count = [0, 0, 0]

    for i, medalOld in enumerate(data):
        if medalOld[3]:
            if medalOld[2] == 'ME_GOLD':
                count[0] = count[0] + 1
            elif medalOld[2] == 'ME_SILVER':
                count[1] = count[1] + 1
            elif medalOld[2] == 'ME_BRONZE':
                count[2] = count[2] + 1

    logging.debug(f"Count: {count}")

    for i, medal in enumerate(text):
        logging.debug(f"Disc: {medal}")
        if (medal not in data):
            if medal[3]:
                if medal[2] == 'ME_GOLD':
                    count[0] = count[0] + 1
                elif medal[2] == 'ME_SILVER':
                    count[1] = count[1] + 1
                elif medal[2] == 'ME_BRONZE':
                    count[2] = count[2] + 1

                printResults(f"Nueva medalla: {medalsIcons[medal[2]]} "
                             f"{medal[3]} - {medal[0]} ({medal[1]})", mode)
                data.append(medal)
                newData = True
        else:
            logging.debug("No news")

    if newData:
        printResults(f"Total medallas:"
              f" {medalsIcons['ME_GOLD']}: {count[0]}"
              f" {medalsIcons['ME_SILVER']}: {count[1]}"
              f" {medalsIcons['ME_BRONZE']}: {count[2]}", mode)
        with open(nameFile(), 'wb') as f:
            pickle.dump(data, f)

    logging.debug(f"Count: {count}")

if __name__ == "__main__":
    main()

# Code that works, but unused
#
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

