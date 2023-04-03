import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import urllib.request
from bs4 import BeautifulSoup
import random
import sys
import time
import urllib
import os

#vars
dir_path = "/down"
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

def get_eps(url):

    #create folder if not there
    name = url.rpartition('/')[1]
    if not os.path.exists(dir_path + '/' + name):
        os.makedirs(dir_path + '/' + name)

    browser.get(url)
    html = browser.execute_script("return document.documentElement.innerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    print(soup)

    eps = []
    for ep in soup.find('div', id='eps').find_all('a', href=True):
        eps.append(url + ep['href']) #need to modify url
        print(ep)

    return [name, eps]

def download(name, eps):
    #download eps
    for ep in eps:
        browser.get(ep)
        html = browser.execute_script("return document.documentElement.outerHTML")
        soup = BeautifulSoup(html, 'html.parser')

        if type == '4anime':
            ep_name = soup.find('li', class_="item ep-item active").find('a').text
            vid_url = soup.find('video')['src']

        urllib.request.urlretrieve(vid_url, dir_path + '/' + name + '/' + ep_name + '.mp4', loadingbar)
    browser.quit()
    print("Downloaded " + str(len(eps)) + " episode.")

url = input("Home link: ")
#Open firefox
options = FirefoxOptions()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)

home_page = get_eps(url)
download(name=home_page, eps=home_page[1])