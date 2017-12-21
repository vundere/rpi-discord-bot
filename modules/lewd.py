"""Cog that contains lewd commands and the tools/commands necessary to control these.
CONF_FILE is listed as a global var here as well because I can't find a better way
of doing this, since I can't pass any arguments when loading cogs.
"""
import requests
import json
import re

from lxml import html
from discord.ext import commands
from utils import lewd_channel, file_tools, tumblr_search, e621  # TODO this can be cleaned up
from random import randint
from bot import is_mommy

CONF_FILE = 'cfg/bot_config.json'


def lewd_allowed(ctx):
    server = ctx.message.server.id
    if ctx.message.channel.id in ctx.bot.cogs["Lewd"].allowed_channels[server]:
        return True
    if ctx.message.channel.name[0:4] == 'nsfw':
        return True
    else:
        return False


class Lewd:
    def __init__(self, bot):
        self.bot = bot
        with open(CONF_FILE, 'r') as conf:
            file = json.load(conf)
            self.allowed_channels = file["lewd_allowed"]
            # These will need to be reworked if other sites are added
            self.url = file["sites"]["pornhub"]["url"]
            self.xpath = file["sites"]["pornhub"]["xpath"]

    @commands.command(description='Enables lewd commands in channel',
                      pass_context=True, hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def enlewd(self, ctx):
        current_channel = ctx.message.channel.id
        channel_server = ctx.message.channel.server.id
        if channel_server not in self.allowed_channels or current_channel not in self.allowed_channels[channel_server]:
            self.allowed_channels = lewd_channel.push(channel_server, current_channel)
            return await self.bot.say("Lewds enabled, buckle down and lube up!")
        else:
            return await self.bot.say("This channel is already lewd!")

    @commands.command(description='De-lewds a channel',
                      pass_context=True, hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def delewd(self, ctx):
        current_channel = ctx.message.channel.id
        current_server = ctx.message.channel.server.id
        if current_channel in self.allowed_channels[current_server]:
            self.allowed_channels = lewd_channel.pop(current_server, current_channel)
            return await self.bot.say("Go home, folks. Lewd party is over.")
        else:
            return await self.bot.say("This channel is already safe!")

    @commands.command(description='Posts n amount of randomly selected PornHub titles.'
                                  'Call with no argument for single title, and with '
                                  '2 - 10 as an argument for a list of titles.',
                      help='Posts random PornHub titles',
                      pass_context=True)
    @commands.check(lewd_allowed)
    async def phub(self, ctx, num=1):
        # TODO maybe add an option to return links?

        def get_title():
            page = requests.get(self.url)
            url = page.url
            page_tree = html.fromstring(page.content)
            page_title = page_tree.findtext(self.xpath)
            if page_title:
                page_title = page_title[0:-14]  # Removes site url from title
                if num == 1:
                    return "{0} - <{1}>".format(page_title, url)
                else:
                    return "{}".format(page_title)
            else:
                return "There was a problem fetching title."

        if num > 1:
            if num > 10:
                return await self.bot.say("Too much! Limit yourself, jeez!")
            titles = []
            list_marker = "```"
            result = ""
            for i in range(0, num):
                titles.append(get_title())
                result = result+"{}\n"
            result = list_marker+result+list_marker
            return await self.bot.say(result.format(*titles))
        else:
            title = get_title()
            return await self.bot.say(title)

    @commands.command(pass_context=True, hidden=True, help='Go on, try!', description='...')
    @commands.check(lewd_allowed)
    async def pomf(self, ctx):
        selector = randint(0, 9)
        if selector < 2:
            return await self.bot.say("What are we going to do on the bed, {0.author.mention}?".format(ctx.message))
        elif selector < 4:
            return await self.bot.say("https://www.youtube.com/watch?v=5bHimOJb-Xw")
        else:
            return await self.bot.upload(file_tools.pomf_get())

    @commands.command(pass_context=True, hidden=True)
    async def snag(self, ctx, n=1):
        """
        This deletes the command message and saves the last n images posted to a channel.
        In lewds because it was created to archive some tasty lewd spam, but should maybe be moved out of here.
        """

        def is_origin(context, cand):
            return context.message.channel == cand.channel

        await self.bot.delete_message(ctx.message)
        yoinked = 0
        async for message in self.bot.logs_from(ctx.message.channel, limit=200):
            url = re.search("(?P<url>https?://[^\s]+)", message.content)
            if is_origin(ctx, message):
                if yoinked < n and url and not message.attachments:
                    url = url.group("url")
                    filename = url.split('/')[-1]
                    success = file_tools.stash(url, filename)
                    if success:
                        print("Image yoinked")
                    else:
                        print("Unable to yoink")
                elif yoinked < n and message.attachments:
                    url = message.attachments[0]['url']
                    filename = message.attachments[0]['filename']
                    success = file_tools.stash(url, filename)
                    if success:
                        print("Image yoinked")
                    else:
                        print("Unable to yoink")
                yoinked += 1

    @commands.command(help='Tumblr search, NSFW results on', description='Searches Tumblr, NSFW results are on so '
                                                                         'it only works in lewd enabled channels.'
                                                                         'Pretty basic right now, but it works.')
    @commands.check(lewd_allowed)
    async def tumblr(self, *query):
        result = tumblr_search.search('+'.join(query))
        await self.bot.say(result)

    @commands.command(hidden=True)
    async def tumblr_test(self, *query):
        """
        This searches tumblr using selenium
        NOTE TO SELF: selenium not configured on rpi, don't use this there until that's sorted.
        Could safely be deleted, but it's nice having it around just in case.
        """
        return await self.bot.say(tumblr_search.scrape_js_load('+'.join(query)))

    @commands.command(help='e621 search', description='Searches e621, has a filter to prevent returning loli etc.')
    @commands.check(lewd_allowed)
    async def e621(self, *query):
        await self.bot.say(e621.post(query))


def setup(bot):
    bot.add_cog(Lewd(bot))
