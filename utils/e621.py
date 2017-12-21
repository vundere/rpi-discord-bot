from random import choice
from lxml import html

import json
import requests

bad_words = [
        'loli',
        'shota',
        'child',
        'young'
    ]


def clean(query):
    for word in bad_words:
        if word in query:
            query.replace(word, "")
    query = '+'.join(query)
    query = query.replace(" ", "+")
    query = query.replace("_", "+")
    query = query.replace("/", "%2F")
    return query


def post(query):
    query = clean(query)
    terms = "order:score rating:questionableplus "+query
    payload = {
        "qs": {
                "limit": 200,
                "tags": terms
            },
        "headers": {
            "User-Agent": "bun discord bot"
        }
    }
    r = requests.get("https://e621.net/post/index.json", params=payload)
    pruned = ([x['file_url'] for x in json.loads(r.text) if (w not in x['tags'] for w in bad_words)])
    return choice(pruned)


def search(query):
    query = clean(query)
    base_search = "https://e621.net/post?tags="
    full_search = base_search + query
    xpath = '//*[@class="preview"]'

    page = requests.get(full_search)
    tree = html.fromstring(page.content)
    elements = tree.xpath(xpath)
    # results = []
    results = ([element.get('src').replace('/preview', '') for element in elements])
    # for element in elements:
    #     preview = element.get("src")
    #     image = preview.replace('/preview', '')
    #     results.append(image)
    if results:
        return choice(results)
    else:
        return "No result."
