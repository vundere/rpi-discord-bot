import requests
from lxml import html
import pprint as pp
import json
from time import sleep

# XPATH vars
all_fdm = '//*[@class="actions"]/a'
base_url = 'http://archiveofourown.org/'


def scrape_categories():
    response = requests.get('http://archiveofourown.org/media')
    response_tree = html.fromstring(response.content)
    elements = response_tree.xpath(all_fdm)
    res = {}
    for element in elements:
        url = base_url + element.get('href')
        fdm = requests.get(url)
        page = html.fromstring(fdm.content)

        title = page.findtext('.//title').split('|')[0].replace('\n', '').strip(' ')

        cats = page.xpath('//*[@class="tag"]')
        cats_res = []
        for cat in cats:
            text = cat.text_content()
            if '|' in text:
                text = text.split('|')[1].strip(' ')
            cats_res.append(text)
        res[title] = cats_res

    with open('result.json', 'w') as f:
        f.seek(0)
        json.dump(res, f, indent=4, sort_keys=True)
        f.truncate()


def gather_tags():
    for i in range(1, 100):
        with open('tags.txt', 'a+') as f:
            url = 'https://archiveofourown.org/tags?show=random'
            response = requests.get(url)
            page_tree = html.fromstring(response.content)
            tags = page_tree.xpath('//*[@id="main"]/ul/li/a')
            for tag in tags:
                text = tag.text_content()
                if text not in f and not (text == 'Most Popular' or text == 'Random'):
                    try:
                        f.write('{}\n'.format(text))
                    except Exception as e:
                        print('{0}\nFailed to write tag {1} to file.'.format(e, text))
    sleep(0.5)


def find_dupes():
    with open('tags.txt', 'r+') as f:
        for i in f:
            for j in f:
                if i == j:
                    print('Dupe found; {}'.format(i))


if __name__ == '__main__':
    # scrape_categories()
    # gather_tags()
    find_dupes()
