"""Discord bot that does some things.
"""
import json
import re
import traceback

import requests
import discord
import logging

from random import randint, randrange, random

import sys

from utils import file_tools, youtube
from discord.ext import commands
from discord.ext.commands import Bot
from lxml import html


DATA_FILE = 'bot_data.json'
CONF_FILE = 'cfg/bot_config.json'
with open(CONF_FILE, 'r') as conf:
    file = json.load(conf)
    # loads token from file for security reasons
    TOKEN = file["token"]

HANJO = False  # Defaulting this to True is not that smart.
startup_extensions = ["cmd.lewd", "cmd.memes", "cmd.community"]
cat_words = ['cat', 'cats', 'kitty', 'kitties', 'kitten', 'kittens']
cat_reacts = ['nyaaa~', ":3", "(ↀДↀ)", "(๑ↀᆺↀ๑)✧", "ლ(=ↀωↀ=)ლ", "～((Φ◇Φ)‡", "(=^-ω-^=)", "(^･ω･^=)~"]

bun_bot = Bot(command_prefix="!bb.")
# TODO move utility functions to separate file, find way to init vars to keep hardcoded vars down, use env vars


def is_mommy(ctx):
    return str(ctx.message.author) == 'vun#1688'


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

async def react_with_hanzo(message, p):
    if message.channel.server.name == "Friend Team":
        hanzo = next((emoji for emoji in bun_bot.get_all_emojis() if emoji.name == 'hanzo'), None)
        if HANJO and hanzo:
            await bun_bot.add_reaction(message, hanzo)
        elif hanzo and random() < p and not message.author == bun_bot.user:
            log.info('{0.timestamp}: Hanzo react triggered in #{0.channel.name} ({0.server.name})'.format(message))
            await bun_bot.add_reaction(message, hanzo)


async def react_cats(message):
    has_cat_word = find_word(message.content, cat_words)
    if has_cat_word and randint(0, 10) < 2 and not message.author == bun_bot.user:
        log.info('{0.timestamp}: Cat react triggered in #{0.channel.name} ({0.server.name})'.format(message))
        await bun_bot.send_message(message.channel, cat_reacts[randrange(len(cat_reacts))])


async def wordcounter(message):
    if str(message.author) == "Father Jenson#4100":
        if message.content == "Rip" or message.content == "rip":
            with open(DATA_FILE, 'r+') as f:
                data = json.load(f)
                if "rip" not in data:
                    data["rip"] = 1
                else:
                    data["rip"] += 1
                f.seek(0)
                json.dump(data, f, indent=4, sort_keys=True)
                f.truncate()


def setup_logging():
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.CRITICAL)
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
    log.addHandler(handler)
    return log


def end_logging(log):
    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)


@bun_bot.event
async def on_command(command, ctx):
    message = ctx.message
    destination = '#{0.channel.name} ({0.server.name})'.format(message)

    log.info('{0.timestamp}: {0.author.name} in {1}: {0.content}'.format(message, destination))


@bun_bot.event
async def on_command_error(exception, context):
    # Modified error handler to include logging of location
    if bun_bot.extra_events.get('on_command_error', None):
        return

    if hasattr(context.command, "on_error"):
        return
    destination = '#{0.channel.name} ({0.server.name})'.format(context.message)

    log.info('{0.timestamp}: {0.author.name} in {1}: Attempted to use invalid command {0.content}'
             .format(context.message, destination))
    print('Ignoring exception in command {}'.format(context.command), file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


@bun_bot.event
async def on_message(message):
    await react_with_hanzo(message, 0.03)
    await react_cats(message)
    await wordcounter(message)
    await bun_bot.process_commands(message)


@bun_bot.event
async def on_ready():
    await bun_bot.change_presence(game=discord.Game(name='commands: !bb.help'))
    print('Logged in as')
    print(bun_bot.user.name)
    print(bun_bot.user.id)
    print('------')


@bun_bot.command(pass_context=True, hidden=True)
async def fox(ctx):
    user = ctx.message.author
    if str(user) == 'aboxoffoxes#3582' or is_mommy(ctx):
        command_list = []
        list_marker = "```"
        result = ""
        for command in bun_bot.commands:
            command_list.append(command)
            result = result + "{}\n"
        result = list_marker + result + list_marker
        return await bun_bot.send_message(user, result.format(*command_list))
    else:
        return await bun_bot.say("This is not for you. Go away.")


@bun_bot.command(help='Correctly places blame.', pass_context=True,
                 description='Pretty self-explanatory when you use it.')
async def blame(ctx):
    user = str(ctx.message.author)
    if user == 'Jax Dasher#0377':
        return await bun_bot.say("It's your fault, dingus!")
    if user == 'vun#1688':
        return await bun_bot.say("It's definitely not vun's fault.")
    else:
        return await bun_bot.say("It's all Jax' fault.")


@bun_bot.command(help='Get XKCD comic', description='By itself fetches random xkcd comic. '
                                                    'Enter comic number as argument to fetch specific comic.'
                                                    'Ex: !bb.xkcd 205')
async def xkcd(no: int = None):
    if no:
        url = "https://xkcd.com/"+str(no)
    else:
        url = requests.get("https://c.xkcd.com/random/comic").url
    return await bun_bot.say(url)


@bun_bot.command(hidden=True, pass_context=True)
@commands.check(is_mommy)
async def fullhanjo():
    global HANJO
    if HANJO:
        print("Easing up on the Hanjo...")
        HANJO = False
    else:
        print("Going full Hanjo!")
        HANJO = True


@bun_bot.command(help='Randomly generated korean nickname')
async def korean():
    master = file_tools.init_korean()
    nouns = master["nouns"]
    verbs = master["verbs"]
    randnoun = nouns[randint(0, (len(nouns)-1))].capitalize()
    randverb = verbs[randint(0, (len(verbs)-1))].capitalize()
    return await bun_bot.say(randnoun+randverb)


@bun_bot.command(help='For Jax', hidden=True)
async def koreanwhy():
    def construct_message():
        list_marker = "```"
        result = "This command generates a nickname by putting two words together, in this case it" \
                 "takes one verb and one noun and concatenates them to create something that " \
                 "may or may not resemble the type of nicknames used by Korean StarCraft players."
        return list_marker+result+list_marker
    return await bun_bot.say(construct_message())


@bun_bot.command(help='Fanfiction search', description='Basic AO3 search function, fetches random result'
                                                       'from the first page.', aliases=["ao3", "fanfiction"])
async def fic(*query):
    search_url = "http://archiveofourown.org/works/search?utf8=✓&work_search[query]="
    link_xpath = '//*[@class="work blurb group"]'
    full_query = search_url + aooo_conform('+'.join(query))
    page = requests.get(full_query)
    page_tree = html.fromstring(page.content)
    elements = page_tree.xpath(link_xpath)
    site_url = 'http://archiveofourown.org'
    results = []
    for element in elements:
        link = element.xpath('div/h4/a[1]')[0]
        href = link.get('href')
        title = link.text_content()
        summary = element.xpath('blockquote/p/text()')
        if summary:
            summary = '\n'.join([str(x) for x in summary])
        else:
            summary = "No summary."
        tags = element.xpath('ul/li/a[1][not(class="warnings")]')
        taglist = []
        for tag in tags:
            taglist.append(tag.text_content())
        results.append({
            "title": title,
            "link": site_url + href,
            "summary": summary,
            "tags": ', '.join([str(x) for x in taglist])
        })
    if results:
        selected = results[randrange(0, len(results))]
        list_marker = "```"
        info = selected["title"]+": "+selected["link"]+"\n"\
            + list_marker+selected["tags"]+"\n\n"+selected["summary"]+list_marker
        return await bun_bot.say(info)
    else:
        return await bun_bot.say("No result.")


@bun_bot.command(help='Returns the top result from YouTube', description='Searches youtube for a term'
                                                                         'and returns the top result.',
                 aliases=["youtube", "video"])
async def yt(*query):
    await bun_bot.say(youtube.search(query))


@bun_bot.command(help="Number of Jenson rips", description="The number of times Jenson has said 'rip' since this "
                                                           "command was implemented.",
                 aliases=["ripcounter", "rip"])
async def ripcount():
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        count = data.get("rip", 0)
    return await bun_bot.say("Current 'rip' count: " + str(count))


@bun_bot.command(hidden=True)
@commands.check(is_mommy)
async def change_bot_name(name):
    await bun_bot.change_nickname(bun_bot.user, name)


@bun_bot.command(hidden=True)
@commands.check(is_mommy)
async def load(extension_name):
    try:
        bun_bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bun_bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bun_bot.say("{} loaded.".format(extension_name))


@bun_bot.command(hidden=True)
@commands.check(is_mommy)
async def unload(extension_name):
    bun_bot.unload_extension(extension_name)
    await bun_bot.say("{} unloaded.".format(extension_name))


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bun_bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    log = setup_logging()
    bun_bot.run(TOKEN)
    end_logging(log)

