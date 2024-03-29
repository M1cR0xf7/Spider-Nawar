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
# #################### Script Kiddies Cut Here ####################
import sys
import os
import requests
from lxml import html
from bs4 import BeautifulSoup

from flask import Flask
from flask import render_template

# setting up url the and the path
TARGET_URL = "https://nawaracademy.com"
LOGIN_PATH = "/en/login"

# get inputs from os enviroment variables (recommended)
# add them as strings if needed (hardcoding creds in source code is dangerous)
try:
    email    = os.environ['EMAIL']  # "youremail@domain.tld"
    password = os.environ['PASS']   # "hunter2"
except:
    print("enviroment variables are not set.")
    sys.exit(1)

req_session = requests.session()

app = Flask(__name__)

p = None
urls = None

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
def login(e: str, p: str) -> str:
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

    return result.text


class Parser:
    def __init__(self, page: str) -> None:
        self.page = page
        self.sessions = list()
        self.urls = list()

    def get_sessions(self) -> list:
        soup = BeautifulSoup(self.page, 'lxml')
        rows = soup.find_all('tr')
        for i in range(len(rows)):
            row = str(rows[i])
            session = BeautifulSoup(row, 'lxml')
            self.sessions.append(
                    session.find_all('a', class_='play-promo shadow-lg'))
        self.sessions = [x for x in self.sessions if x != []]

    def get_video_urls(self) -> None:
        for i in self.sessions:
            root = html.fromstring(str(i[0]))
            self.urls.append(root.xpath('//a/@data-video'))


def _do_work() -> Parser:
    page = login(email, password)
    p = Parser(page)
    p.get_sessions()
    p.get_video_urls()
    return p


def main() -> None:
    global p
    global urls
    p = _do_work()
    urls = p.urls
#    print(f"Nimber of videos found: {len(p.urls)}")
#    for i in urls:
#        print(i[0])


# We Wprk on this later
@app.route('/')
def webserver():
    if urls is None:
        print("What the fuck is happening?")
        sys.exit(1)
    return render_template('index.html', vids=urls, n=len(urls))

if __name__ == '__main__':
    main()
    app.run()
