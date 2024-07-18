import requests
from bs4 import BeautifulSoup
import os
import random
import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.request import urlretrieve

#variables
web_folder_path = "/media/hoang/rasp2/webcontent" #folder directory
anime_folder_path = "/media/hoang/rasp2/anime" #anime directory
A1 = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
) #Agents
nurls = ['https://nyaa.si/?f=2&c=1_0&q=&p=1', 'https://nyaa.si/?f=2&c=1_0&q=&p=2', 'https://nyaa.si/?f=2&c=1_0&q=&p=3'] #nyaa url
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') #yesterday's date

#Credentials
user = "###"
pwd = "###"

#Log and mail
message = MIMEMultipart("alternative")
message["From"] = user
message["To"] = user
message["Subject"] = f"Torrent NAS Log: {yesterday}"
error_message = "Unable to connect to qBittorent"

def format_message(processed):
    if not processed:
        text = error_message
        html = f"""\
        <html>
        <body>
            <h1>Error</h1>
            <p>{error_message}</p>
        </body>
        </html>
        """
        return [text, html]
    
    animes = processed
    num_animes = str(len(animes))

    text = f"""\
    Anime downloaded ({num_animes})"""
    html = f"""\
    <html>
    <body>
        <h1>Anime</h1>
        <p>Downloaded: <b>{num_animes}</b></p>
        <ul>
    """

    for anime in animes:
        name = anime['anime']
        text += f"\n{name}"
        html += f"<li>{name}</li>"
    html += f"""\
        </body>
        </html>
        """

    return [text, html]

def mail(text, html):

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, user, message.as_string())
        server.quit()

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
        url = str(tds[2].find_all('a')[0]['href'])
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

def get_anime():
    #return torrents to download

    #scrape pages and obtain list of tr
    rows = []

    for url in nurls: 
        requ = requests.get(url, headers=headers)
        soup = BeautifulSoup(requ.text, 'html.parser')
        rows += soup.find_all('tr')

    #filter
    animes = fit_criteria(rows)
    
    return animes

def download(animes):
    try:
        #download files
        for anime in animes:
            urlretrieve("https://nyaa.si/" + anime.get('url'), "/home/hoang/deluge/downloads/" + anime.get('anime')+".torrent")

        #save results as a log
        with open(web_folder_path + '/anime_' + yesterday + '.txt', 'w') as fout:
            json.dump(animes, fout)
        with open(web_folder_path + '/anime_' + yesterday + '.txt', 'a') as fout:
            fout.write("\nAdded " + str(len(animes)) + " animes")
        print('Success downloaded ' + str(len(animes)) + ' animes')
        processed = results
    except:
        processed = None
        print(error_message)

    text, html = format_message(processed)
    mail(text, html)

clear_dir() #clear yesterday's changelog
headers = get_header()
results = get_anime()
download(results)