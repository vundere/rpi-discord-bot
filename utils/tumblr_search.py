import requests
import json
import time
from lxml import html
from random import randint
from selenium import webdriver
import seleniumrequests


DATA_FILE = '/home/pi/shared/rpi-discord-bot/cfg/tumblr_data.json'
DATA_WIN = 'H:/Users/Olav/Documents/GitHub/Personal-projects/discord_bot/static/tumblr_data.json'
PHANTOMJS_PATH = 'H:/Users/Olav/Documents/GitHub/ignored/phantomjs-2.5.0.beta-windows/bin/phantomjs.exe'
payload = {}
with open(DATA_FILE, 'r') as tdata:
    unpacked = json.load(tdata)
    payload["user[email]"] = unpacked["username"]
    payload["user[password]"] = unpacked["password"]


def search(query):
    query = query.replace(" ", "+")
    query = query.replace("/", "%2F")
    with requests.Session() as s:
        response = s.get('https://www.tumblr.com/login', headers=s.headers)
        r = html.fromstring(str(response.text))
        form_key = r.xpath("//meta[@name='tumblr-form-key']/@content")[0]
        payload["form_key"] = form_key
        s.post('https://www.tumblr.com/login', headers=s.headers, data=payload)

        xpath = '//*[@id="search_posts"]/article/section/div/img/@src'
        r = s.get('https://www.tumblr.com/search/'+query)
        r_tree = html.fromstring(r.content)
        results = r_tree.xpath(xpath)
        delivery = []
        for result in results:
            delivery.append(result)
        if len(delivery) > 0:
            return delivery[randint(0, (len(delivery)-1))]
        else:
            return "No valid result."


def scrape_js_load(query):
    browser = webdriver.PhantomJS(PHANTOMJS_PATH)
    browser.get('https://www.tumblr.com/login')
    time.sleep(1)
    username = browser.find_element_by_xpath('//*[@id="signup_determine_email"]')
    nextbtn = browser.find_element_by_xpath('//*[@id="signup_forms_submit"]/span[2]')
    username.send_keys(payload['user[email]'])
    time.sleep(1)
    nextbtn.click()
    time.sleep(1)
    password = browser.find_element_by_xpath('//*[@id="signup_password"]')
    password.send_keys(payload['user[password]'])
    login_attempt = browser.find_element_by_xpath('//*[@id="signup_forms_submit"]/span[6]')
    login_attempt.click()

    xpath = '//*[@id="search_posts"]/article/section/div/img/@src'
    browser.get('https://www.tumblr.com/search/' + query)
    time.sleep(1)
    r = browser.page_source
    r_tree = html.fromstring(r)
    results = r_tree.xpath(xpath)
    delivery = []
    for result in results:
        delivery.append(result)
    if len(delivery) > 0:
        return delivery[randint(0, (len(delivery) - 1))]
    else:
        return "No valid result."


