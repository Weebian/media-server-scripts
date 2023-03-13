import requests
from selenium import webdriver
import urllib.request
from bs4 import BeautifulSoup
import random
import sys
import time
import urllib
import os

#vars
dir_path = "/media/piho/rasp2/anime"
A1 = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
) #Agents

def get_header():
    Agent1 = A1[random.randrange(len(A1))]
    headers = {'user-agent': Agent1}
    return headers

def loadingbar(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * (int(duration) + 1)))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

def get_eps(url, type):
    requ = requests.get(url, headers=get_header())
    soup = BeautifulSoup(requ.text, 'html.parser')

    if type == "geno":
        #create folder if not there
        name = soup.find(class_="anime__details__title").find("h3").text
        if not os.path.exists(dir_path + '/' + name):
            os.makedirs(dir_path + '/' + name)

        #obtain 
        eps = []
        for ep in soup.find_all('a', class_='episode', href=True):
            eps.append('https://genoanime.com' + ep['href'][2:]) #need to modify url for geno
        return eps
    
    raise ValueError('Error: Invalid type')

def download(type, eps):
    for ep in eps:
        browser.get(ep)
        time.sleep(3)
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')

        if type == 'geno':
            title = soup.find('a', id='anime_details_breadcrumbs').text
            ep_name = soup.find('li', id="current_episode").text
            vid_url = soup.find('video', id="video_player_html5_api")['src']

        urllib.request.urlretrieve(vid_url, dir_path + '/' + title + '/' + ep_name + '.mp4', loadingbar)

    print("Downloaded " + len(eps) + " episode.")

type = input("Type (Options: geno): ")
url = input("Home link: ")
browser = webdriver.Chrome(executable_path=r"/media/piho/rasp2/chromedriver.exe")
eps = get_eps(url, type)
download(type, eps)