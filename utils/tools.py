"""
File that contains utility functions that don't interact with external files.
"""

import re
import discord
import requests
import sys
if sys.version_info[:2] == (3, 6):
    from random import choices
else:
    from random import choice

word_site = 'http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain'


def aooo_conform(query):
    if not isinstance(query, str):
        query = '+'.join(query)
    clean = query.replace(" ", "+")
    clean = clean.replace("/", "%2F")
    clean = clean.replace("&", "%26")
    return clean


def find_word(message, words):
    """Looks for one of several words in a string.
    Has not been tested for String instead of a List.
    :param message: String, the string you want to look in.
    :param words: List of words you want to look for.
    :return: True if word is in the message, false if not
    """

    def finder(word):
        return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search

    for w in words:
        if finder(w)(message):
            return True
    return False


def find_member(bot, member_id: str):
    return discord.utils.get(bot.get_all_members(), id=member_id)


def get_random_words(n):
    """
    Returns n random words
    """
    response = requests.get(word_site)
    words = response.content.splitlines()
    try:
        res = [x.decode('utf-8') for x in choices(words, k=n)]
    except Exception as e:
        res = [choice(words).decode('utf-8') for x in range(n)]
    return res

# TODO merge tools.py and file_tools.py
