import json
import os
import time

import requests
from dotenv import load_dotenv
from lxml import etree
from requests_oauthlib import OAuth1

load_dotenv()

oauth = OAuth1(
    os.environ['CONSUMER_KEY'],
    os.environ['CONSUMER_SECRET'],
    os.environ['ACCESS_TOKEN'],
    os.environ['ACCESS_SECRET'],
)

def tweet(section, title, link):
    message = f'{title}: {link} #{section} #SGLiveNews'
    requests.post(
        'https://api.twitter.com/1.1/statuses/update.json',
        params={
            'status': message
        },
        headers={
            'User-Agent': 'SGLiveNews'
        },
        auth=oauth
    )

def telegram(section, title, link):
    message = f'{title}: {link} #{section} #SGLiveNews'
    requests.post(
        f'https://api.telegram.org/bot{os.environ["TELEGRAM_BOT_TOKEN"]}/sendMessage',
        json={
            'chat_id': '@sglivenews',
            'text': message,
        }
    )

BASE = 'https://www.straitstimes.com/news/{feed}/rss.xml'
QUERY = {
    'singapore': None,
    'asia': None,
    'tech': None,
    'world': None,
    'opinion': None
}

try:
    with open('save.json') as f:
        QUERY.update(json.load(f))
except FileNotFoundError:
    pass

print('Started')

while True:
    for k, v in QUERY.items():
        req = requests.get(
            BASE.format(feed=k),
            headers={'User-Agent': 'SGLiveNews'}
        )
        root = etree.fromstring(req.text.encode())
        articles = root.find('channel').findall('item')

        if articles:
            title = articles[0].findtext('title')
            description = articles[0].findtext('description')
            link = articles[0].findtext('link')
            if title != v:
                tweet(k, title, link)
                telegram(k, title, link)
                QUERY[k] = title
                print(f'Posted {title}')
                with open('save.json', 'w+') as f:
                    json.dump(QUERY, f)

    time.sleep(3)
