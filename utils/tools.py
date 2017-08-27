import re
import discord


def aooo_conform(query):
    clean = query.replace(" ", "+")
    clean = clean.replace("/", "%2F")
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