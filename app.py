import requests
from bs4 import BeautifulSoup
import os
import random
import datetime
import json
from qbittorrent import Client

#variables
web_folder_path = "/media/piho/rasp2/webcontent" #folder directory
anime_folder_path = "/media/piho/rasp2/anime" #anime directory
A1 = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
) #Agents
nurls = ['https://nyaa.si/?f=2&c=1_0&q=&p=1', 'https://nyaa.si/?f=2&c=1_0&q=&p=2', 'https://nyaa.si/?f=2&c=1_0&q=&p=3'] #nyaa url
surls_ani = ['https://sukebei.nyaa.si/?f=2&c=1_1&q=english'] #sukubei anime
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') #yesterday's date

def clear_dir():
    files = [f for f in os.listdir(web_folder_path)]
    for f in files:
        os.remove(os.path.join(web_folder_path, f))

def get_header():
    Agent1 = A1[random.randrange(len(A1))]
    headers = {'user-agent': Agent1}
    return headers

def fit_criteria(rows):
    #returns a list of torrent links and anime names if matches criterias
    results = []

    #obtain list of animes to download
    with open(anime_folder_path + '/anime.txt', 'r') as f:
        animes_to_download = f.read().splitlines() #splitlines removes /n from read
        
    for tr in rows:
        tds = tr.find_all('td') #obtian tds in the row
        
        #Checks
        if len(tds) == 0:
            continue
        if not tds[1].find('a'):
            continue
        if not tds[2].find('a'):
            continue

        #Vars
        name = tds[1].find_all('a', class_=None)[0].contents[0]
        url = str(tds[2].find_all('a')[1]['href'])
        date = False
        quality = False
        anime = None
        
        #Check date
        if yesterday in str(tds[4].contents[0]):
            date = True
    
        #Check quality
        if '1080p' in name:
            quality = True

        #update for anime and episode
        for atd in animes_to_download:
            if atd.lower() in name.lower() and quality:
                anime = name
                animes_to_download.remove(atd)
                break

        if date and quality and anime:
            results.append({
                'anime': anime,
                'url': url
            })

    return results

def fit_criteria_sukebei(rows):
    #returns a list of torrent links and anime names if matches criterias
    results = []

    for tr in rows:
        tds = tr.find_all('td') #obtain tds in the row

        #Checks
        if len(tds) == 0:
            continue
        if not tds[1].find('a'):
            continue
        if not tds[2].find('a'):
            continue

        #var
        name = tds[1].find('a').contents[0]
        url = str(tds[2].find_all('a')[1]['href'])

        #Check date
        if yesterday in str(tds[4].contents[0]):
            #add to results
            results.append({
                'name': name,
                'url': url
            })
        
    return results

def get_anime():
    #return torrents to download

    #scrape pages and obtain list of tr
    rows = []
    rows2 = []

    for url in nurls: 
        requ = requests.get(url, headers=headers)
        soup = BeautifulSoup(requ.text, 'html.parser')
        rows += soup.find_all('tr')
        
    for url in surls_ani:
        requ2 = requests.get(url, headers=headers)
        soup2 = BeautifulSoup(requ2.text, 'html.parser')
        rows2 += soup2.find_all('tr')

    #filter
    animes = fit_criteria(rows)
    s_animes = fit_criteria_sukebei(rows2)
    
    return [animes, s_animes]

def download(results):
    #download on qbittorent
    qb = Client('http://127.0.0.1:8080/')
    qb.login('admin', 'adminadmin')

    animes = results[0]
    s_animes = results[1]

    for anime in animes:
        qb.download_from_link(anime.get('url'), category='anime')
    for s_anime in s_animes:
        qb.download_from_link(s_anime.get('url'), savepath='/media/piho/rasp2/sukubei/anime', category='sukubei_anime')

    #save results as a log
    with open(web_folder_path + '/anime_' + yesterday + '.txt', 'w') as fout:
        json.dump(animes, fout)
    with open(web_folder_path + '/anime_' + yesterday + '.txt', 'a') as fout:
        fout.write("\nAdded " + str(len(animes)) + " animes")
    with open(web_folder_path + '/s_animes_' + yesterday + '.txt', 'w') as fout:
        json.dump(s_animes, fout)
    with open(web_folder_path + '/s_animes_' + yesterday + '.txt', 'a') as fout:
        fout.write("\nAdded " + str(len(s_animes)) + " sukubei animes")
    print('Success downloaded ' + str(len(animes)) + ' animes')
    print('Success downloaded ' + str(len(s_animes)) + ' sukubei animes')

clear_dir() #clear yesterday's changelog
headers = get_header()
results = get_anime()
download(results)