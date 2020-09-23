#!/usr/bin/python
# This script is written by the genius and
# the most talented programmer M1cR0xf7 (Youssef Hesham)
#
# you are not supposed to use this script, this script exists
# for educational purposes only.
#
# The author hacked it in his free time for the sake of learning
# web scraping.
#
#
# Author: Youssef Hesham (M1cR0xf7)
#
# Goal: list all available video sessions on the site
# to download and watching it offline (backing it up in case of deletion)
#
# License: Public Domain (I release all my shit public domain)
#
# Tested On: Gnu/Linux; i do not know if windows has enviroment variables
# but you can modify the code and add your email and password as strings
# in their place.
#
# CHANGELOG:
#
# [0.1.1] - 2020-09-11
# ### Changed
# - login function returns a cookie
# - scrape video session urls from another path.
#
# [0.1.2] - 2020-09-22
# - scraping titles and writing them
# - adding the video url under the video so it
#   easies up the process of downloading
#
# [0.2.0] - 2020-09-23
# - add a function to print urls next to titles
# - move _do_work() to main()
# - running a webserver is not necessary =
#
# #################### Script Kiddies Cut Here ####################
import sys
import os
import re
import requests
from lxml import html
from bs4 import BeautifulSoup

from flask import Flask
from flask import render_template

# setting up url the and the path
TARGET_URL = "https://nawaracademy.com"
LOGIN_PATH = "/en/login"
VIDEOS_PATH = "/en/student/session_videos"

RUN_SERVER = False

# get inputs from os enviroment variables (recommended)
# add them as strings if needed (hardcoding creds in source code is dangerous)
try:
    email    = os.environ['EMAIL']  # "youremail@domain.tld"
    password = os.environ['PASS']   # "hunter2"
except Exception as e:
    print("enviroment variables are not set.")
    print(e)
    sys.exit(1)

req_session = requests.session()

app = Flask(__name__)

p = None
urls = None
titles = None

def set_payload(e: str, p: str, t: str) -> dict:
    """
    e: email
    p: password
    t: token
    -> returns a dict
    """
    payload = {
            'email': e,
            'password': p,
            '_token': t,
            'remember': 'off'  # it's off because why not?
    }

    return payload


# Login and return HTML with video sessions urls
def login(e: str, p: str) -> requests.cookies.RequestsCookieJar:
    """
    e: email
    p: password
    -> returns the html of the homepage after login with all the sessions
    """
    # Lets start the login attempt
    login_page_result = req_session.get(TARGET_URL + LOGIN_PATH)
    tree = html.fromstring(login_page_result.text)
    # print(login_page_result.text)
    authenticity_token = list(
            set(tree.xpath("//input[@name='_token']/@value")))[0]

    payload = set_payload(e, p, authenticity_token)

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
    }

    result = req_session.post(TARGET_URL + LOGIN_PATH,
                          data=payload, headers=headers)

    # print(f"Using the payload: {payload}")
    # print(f"Using the headers: {headers}")
    # print(result.text)

    return result.cookies


class Parser:
    def __init__(self, page: str) -> None:
        self.page = page
        self.sessions = list()
        self.urls = list()
        self.titles = list()

    def get_sessions(self) -> list:
        soup = BeautifulSoup(self.page, 'lxml')
        rows = soup.find_all('tr')
        for i in range(len(rows)):
            row = str(rows[i])
            session = BeautifulSoup(row, 'lxml')
            self.sessions.append(
                    session.find_all('a', class_='xplay-promo shadow-lg'))
        self.sessions = [x for x in self.sessions if x != []]

    def get_session_titles(self) -> list:
        soup = BeautifulSoup(self.page, 'lxml')
        rows = soup.find_all('tr')
        for i in range(len(rows)):
            row = str(rows[i])
            titles = BeautifulSoup(row, 'lxml')
            self.titles.append(
                    titles.find_all('span', class_='mx-2'))
        self.titles = [x for x in self.titles if x != []]
        for i in range(len(self.titles)):
            self.titles[i][0] = str(self.titles[i][0])
            self.titles[i][0] = re.findall(r'>(.*?)<', self.titles[i][0])
        for i in range(len(self.titles)):
            self.titles[i] = str(self.titles[i][0][0])

    def get_video_urls(self) -> None:
        for i in self.sessions:
            root = html.fromstring(str(i[0]))
            self.urls.append(root.xpath('//a/@data-video'))

    def show(self) -> None:
        for i, j in enumerate(zip(self.titles, self.urls)):
            print(f"{i} {j}")


def main() -> None:
    global p
    global urls
    global titles

    cookie_jar = login(email, password)
    page = req_session.get(TARGET_URL + VIDEOS_PATH, cookies=cookie_jar)

    p = Parser(page.text)
    p.get_sessions()
    p.get_video_urls()
    p.get_session_titles()

    urls = p.urls
    titles = p.titles

    p.show()

# We Wprk on this later
@app.route('/')
def webserver():
    return render_template('index.html',
            vids=urls, n=len(urls), titles=titles)


if __name__ == '__main__':
    main()

    if RUN_SERVER:
        app.run()
