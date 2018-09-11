"""
Discord bot that does some things.
"""
import json
import traceback
import requests
import discord
import logging
import sys
import os

from time import sleep
from random import randint, random, choice
from utils import file_tools, tools
from discord.ext import commands
from discord.ext.commands import Bot
from modules.activity_monitor import update_entry

CONF_FILE = 'cfg/bot_config.json'
HANJO = False  # Defaulting this to True is not that smart.
hanzo = None

startup_extensions = [
    "modules.lewd",
    "modules.memes",
    "modules.search",
    "modules.activity_monitor",
    "modules.ranks"
]
cat_words = [
    'cat',
    'cats',
    'kitty',
    'kitties',
    'kitten',
    'kittens',
    'cato',
    'cattos'
]
cat_reacts = [
    'nyaaa~',
    ":3",
    "(ↀДↀ)",
    "(๑ↀᆺↀ๑)✧",
    "ლ(=ↀωↀ=)ლ",
    "～((Φ◇Φ)‡",
    "(=^-ω-^=)",
    "(^･ω･^=)~"
]
dog_words = [
    'dog',
    'dogs',
    'puppy',
    'puppies',
    'doggo',
    'doggos',
    'pupper',
    'puppers'
]
dog_reacts = [
    'woof',
    '(❍ᴥ❍ʋ)',
    '੯ੁૂ‧̀͡u',
    'ฅ^•ﻌ•^ฅ',
    '₍ᐢ•ﻌ•ᐢ₎*･ﾟ｡',
    '(υ◉ω◉υ)',
    '໒( ◉ ᴥ ◉ )७',
    '▐ ☯ ᴥ ☯ ▐'
]

bun_bot = Bot(command_prefix="!bb.")


def init_vars():
    with open(CONF_FILE, 'r') as conf:
        file = json.load(conf)
        bun_bot.token = file["token"]
        bun_bot.yt_api_key = file["youtube_api_key"]
        bun_bot.mommy = file["mommy"]
        bun_bot.data_file = 'bot_data.json'
        bun_bot.tumblr_data = 'cfg/tumblr_data.json'
        bun_bot.cfg_file = CONF_FILE


def is_mommy(ctx):
    return str(ctx.message.author.id) == bun_bot.mommy


def setup_logging():
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.CRITICAL)

    log = logging.getLogger('bun_bot')
    log.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='a')
    fmt = logging.Formatter('[%(asctime)s] :%(levelname)s: %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(fmt)
    log.addHandler(handler)
    return log


def end_logging(log):
    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)


def set_hanzo():
    """
    sets hanzo emote on bot init to limit excessive rate use
    currently hardcoded to only work on one server, but this could be simplified
    """
    global hanzo
    try:
        for server in bun_bot.servers:
            if server.id == "261561747620626443":
                hanzo = next((emoji for emoji in bun_bot.get_all_emojis() if emoji.name == 'hanzo'), None)

    except AttributeError as ae:
        print("Error finding emote \n {}".format(ae))


async def react_with_hanzo(message, p):
    if message.channel.server.id == "261561747620626443":
        if HANJO and hanzo:
            await bun_bot.add_reaction(message, hanzo)
        elif hanzo and random() < p and not message.author == bun_bot.user:
            log.info('Hanzo react triggered in #{0.channel.name} ({0.server.name})'.format(message))
            await bun_bot.add_reaction(message, hanzo)


async def react_word(message):
    has_cat_word = tools.find_word(message.content, cat_words)
    has_dog_word = tools.find_word(message.content, dog_words)
    if has_cat_word and randint(0, 10) < 2 and not message.author == bun_bot.user:
        log.info('Cat react triggered in #{0.channel.name} ({0.server.name})'.format(message))
        await bun_bot.send_message(message.channel, choice(cat_reacts))
    if has_dog_word and randint(0, 10) < 2 and not message.author == bun_bot.user:
        log.info('Dog react triggered in #{0.channel.name} ({0.server.name})'.format(message))
        await bun_bot.send_message(message.channel, choice(dog_reacts))


async def wordcounter(message):
    if str(message.author.id) == "133237258668081152":  # checks for jenson
        if tools.find_word(message.content, ['rip']):
            with open(bun_bot.data_file, 'r+') as f:
                data = json.load(f)
                if "rip" not in data:
                    data["rip"] = 1
                else:
                    data["rip"] += 1
                f.seek(0)
                json.dump(data, f, indent=4, sort_keys=True)
                f.truncate()


async def boop(message):
    if not message.author == bun_bot.user:
        if message.content.lower() == 'beep':
            return await bun_bot.send_message(message.channel, 'boop')
        if message.content.lower() == 'boop':
            return await bun_bot.send_message(message.channel, 'beep')


async def someone(message):
    channel = message.channel
    server = channel.server

    if message.content.lower() == '@someone':
        target = choice(list(server.members))
        msg = await bun_bot.send_message(channel, target.mention)
        await bun_bot.delete_message(msg)


@bun_bot.event
async def on_command(command, ctx):
    message = ctx.message

    destination = '#{0.channel.name} ({0.server.name})'.format(message)
    log.info('{0.author.name} in {1}: {0.content}'.format(message, destination))


@bun_bot.event
async def on_command_completion(command, ctx):
    # message = ctx.message
    # log.info('Bot responded with {0.content}'.format(message))
    pass  # find way to easily log bot response


@bun_bot.event
async def on_command_error(exception, context):
    """
    Slightly modified error handler, to allow for logging of when and where
    people try to use commands that don't exist.
    """
    if bun_bot.extra_events.get('on_command_error', None):
        return

    if hasattr(context.command, "on_error"):
        return

    destination = '#{0.channel.name} ({0.server.name})'.format(context.message)
    log.info('{0.author.name} in {1}: Attempted to use invalid command {0.content}'
             .format(context.message, destination))

    print('Ignoring exception in command {}'.format(context.command), file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


@bun_bot.event
async def on_message(message):
    # await react_with_hanzo(message, 0.03)
    await react_word(message)
    await wordcounter(message)
    await boop(message)
    update_entry(message)
    await someone(message)
    await bun_bot.process_commands(message)


@bun_bot.event
async def on_ready():
    await bun_bot.change_presence(game=discord.Game(name='commands: !bb.help'))
    set_hanzo()
    print('Logged in as')
    print(bun_bot.user.name)
    print(bun_bot.user.id)
    print('------')


@bun_bot.command(pass_context=True, hidden=True)
async def fox(ctx):
    """
    This just PMs an unsorted list of every command the bot has, since many of them are hidden.
    """
    user = ctx.message.author
    if user.id == '133373976008327168' or is_mommy(ctx):  # checks for fox
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


@bun_bot.command(help='Get XKCD comic', description='By itself fetches random xkcd comic. '
                                                    'Enter comic number as argument to fetch specific comic.'
                                                    'Ex: !bb.xkcd 205')
async def xkcd(no: int = None):
    if no:
        url = "https://xkcd.com/{}".format(no)
    else:
        url = requests.get("https://c.xkcd.com/random/comic").url
    return await bun_bot.say(url)


@bun_bot.command(hidden=True, pass_context=True)
@commands.check(is_mommy)
async def fullhanjo():
    """
    This just makes the bot react with hanzo to every message.
    """
    global HANJO
    if HANJO:
        print("Easing up on the Hanjo...")
        HANJO = False
    else:
        print("Going full Hanjo!")
        HANJO = True


@bun_bot.command(help='Randomly generated korean nickname', description='Combines a noun and a verb in the hopes '
                                                                        'of creating something that resembles a '
                                                                        'Korean StarCraft nickname.')
async def korean():
    master = file_tools.init_korean()
    nouns = master["nouns"]
    verbs = master["verbs"]
    randnoun = choice(nouns).capitalize()
    randverb = choice(verbs).capitalize()
    return await bun_bot.say(randnoun+randverb)


@bun_bot.command(help='Rolls a dice of X sides.')
async def d(x):
    roll = randint(1, int(x))
    await bun_bot.say('Rolled {}'.format(roll))
    if roll == x:
        await bun_bot.say('Critical hit!')
    elif roll == 1:
        await bun_bot.say('Critical fail...')


@bun_bot.command(hidden=True)
@commands.check(is_mommy)
async def load(extension_name):
    try:
        bun_bot.load_extension('modules.{}'.format(extension_name))
    except (AttributeError, ImportError) as e:
        await bun_bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bun_bot.say("{} loaded.".format(extension_name))


@bun_bot.command(hidden=True)
@commands.check(is_mommy)
async def unload(extension_name):
    bun_bot.unload_extension('modules.{}'.format(extension_name))
    await bun_bot.say("{} unloaded.".format(extension_name))


@bun_bot.command(hidden=True)
@commands.check(is_mommy)
async def reload(extension_name):
    try:
        bun_bot.unload_extension('modules.{}'.format(extension_name))
        sleep(0.4)
        bun_bot.load_extension('modules.{}'.format(extension_name))
        await bun_bot.say('{} reloaded.'.format(extension_name))
    except (AttributeError, ImportError) as e:
        await bun_bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return


if __name__ == "__main__":
    log = setup_logging()
    try:
        init_vars()
        for extension in startup_extensions:
            try:
                bun_bot.load_extension(extension)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))

        with open('bunbot.pid', 'w') as f:
            f.write(str(os.getpid()))
        log.info('PID file written.')

        bun_bot.run(bun_bot.token)

        log.info('Bot stopping.')
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        log.info('Bot crashed with exception: \n{}'.format(exc))
    finally:
        log.info('Removing PID file.')
        os.remove('bunbot.pid')
        end_logging(log)

