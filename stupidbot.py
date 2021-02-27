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
# License: WTFPL (check COPYING file)
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
# - scrap video session urls from another path.
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
# [0.2.1] - 2020-10-27
# - control RUN_SERVER var using arguments
# - fix typos
#
# [0.2.2] - 2020-12-07
# - output csv format
# **UPDATE**
# This code sucks, it is ugly and unmanitainable. i am thinking
# about rewriting the Parser class from scratch; not right now or
# very soon, maybe 2 months later idk.
#
# [0.2.3] - 2020-02-18
# # added
# - debug output
# **UPDATE**
# they started embedding youtube videos on the website and this script
# does not support that. i dont have the time to do it.
# it will output "https://nawaracademy.com" in the url field.
#
# [0.3.0] - 2021-02-28
# - parsing youtube videos
# **update**
# now parsing youtube videos without titles and i really dont care
# and i will not implement this.
# this project is done. i am out.
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

from fake_useragent import UserAgent

# setting up url the and the path
TARGET_URL = "https://nawaracademy.com"
LOGIN_PATH = "/en/login"
VIDEOS_PATH = "/en/student/session_videos"
YT_SHORT = "https://youtu.be/"


try:
    RUN_SERVER = True if sys.argv[1] == "serve" else False
except Exception:
    RUN_SERVER = False

# get inputs from os enviroment variables (recommended)
# add them as strings if needed (hardcoding creds in source code is dangerous)
try:
    email = os.environ['EMAIL']     # "youremail@domain.tld"
    password = os.environ['PASS']   # "hunter2"
except Exception as e:
    print("enviroment variables are not set.")
    print(e)
    sys.exit(1)

req_session = requests.session()

# in case if you want to use proxy to debug the web requests
#
# req_session.proxies.update({"http": "http://127.0.0.1:8080",
#                             "https": "http://127.0.0.1:8080"})
# req_session.verify = False

app = Flask(__name__)

p = None
urls = None
titles = None


def _dbg_print(x: str):
    # give more output
    print(x)


if '-d' not in sys.argv:
    del _dbg_print
    _dbg_print = lambda x: None


_dbg_print("[!] verbose mode enabled.")


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
    -> returns a session cookie
    """
    # Lets start the login attempt
    login_page_result = req_session.get(TARGET_URL + LOGIN_PATH)
    tree = html.fromstring(login_page_result.text)
    # print(login_page_result.text)
    authenticity_token = list(
            set(tree.xpath("//input[@name='_token']/@value")))[0]

    payload = set_payload(e, p, authenticity_token)

    ua = UserAgent()

    headers = {
        "User-Agent": ua.chrome
    }

    result = req_session.post(TARGET_URL + LOGIN_PATH,
                              data=payload, headers=headers)

    _dbg_print(f"Using the payload: {payload}")
    _dbg_print(f"Using the headers: {headers}")
    # _dbg_print(result.text)

    _dbg_print(f"Using the cookies: {result.cookies}")
    return result.cookies


class Parser:
    def __init__(self,
                 page: str,
                 cookies: requests.cookies.RequestsCookieJar) -> None:
        self.page = page
        self.cookies = cookies
        self.sessions = list()
        self.urls = list()
        self.titles = list()
        self.yt_vids = list()
        self.yt_shorts = list()

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
            x = root.xpath('//a/@data-video')
            y = root.xpath('//a/@href')
            _dbg_print(f"{x[0]} // {type(str(x[0]))}")
            if re.match("^https://nawaracademy.com$", str(x[0])):
                self.yt_vids.append(y[0])
            self.urls.append(x)
        self.maybe_yt(self.cookies)

    def maybe_yt(self, cookies):
        """
        get url of embedded youtube video
        """
        # _dbg_print(f"YOUTUBE => {self.yt_vids} ")
        for i in self.yt_vids:
            # _dbg_print(f"{str(i)} // {type(str(i))}")
            soup = BeautifulSoup(req_session.get(
                str(i),
                cookies=cookies).text,
                'lxml')
            vid_id = str(soup.find("div",
                {"id": "video-player"}
                )['data-plyr-embed-id'])
            self.yt_shorts.append(YT_SHORT + vid_id)

    def show(self) -> None:
        """
        tee it to a file with a .csv ext
        """
        print("#,name,url")
        for i, j in enumerate(zip(self.titles, self.urls)):
            print(f"{i+1},{j[0]},{j[1][0]}")
        print("0,Embedded youtube vids,0")
        for i in self.yt_shorts:
            print(f"0,0,{i}")


def main() -> None:
    global p
    global urls
    global titles

    cookie_jar = login(email, password)
    page = req_session.get(TARGET_URL + VIDEOS_PATH, cookies=cookie_jar)

    p = Parser(page.text, cookie_jar)
    p.get_sessions()
    p.get_video_urls()
    p.get_session_titles()

    urls = p.urls
    titles = p.titles

    p.show()


@app.route('/')
def webserver():
    return render_template('index.html', vids=urls, n=len(urls), titles=titles)


if __name__ == '__main__':
    main()

    if RUN_SERVER:
        app.run()
