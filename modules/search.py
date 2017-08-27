import requests
import json

from utils import tools
from discord.ext import commands
from lxml import html
from random import choice
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


class Search:
    def __init__(self, bot):
        self.bot = bot

    def youtube_search(self, query, max_results=10):
        """
        :param query: string, search query
        :param max_results: int, max numbers of results
        :return: dict containing one list of links, one list of titles

        Currently the command just returns the #1 result from the list of links, but this
        already returns everything needed for future selector funcionality.
        """
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=self.bot.yt_api_key,
                        cache_discovery=False)

        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results
        ).execute()

        videos = []
        hidden_videos = []
        n = 0
        for result in search_response.get("items", []):
            if result["id"]["kind"] == "youtube#video":
                n += 1
                # videos.append("%s (%s)" % (result["snippet"]["title"],
                #                            result["id"]["videoId"]))
                videos.append("{0}. {1}".format(n, result["snippet"]["title"]))
                hidden_videos.append("https://www.youtube.com/watch?v={0}".format(result["id"]["videoId"]))

        try:
            list_format = "```Select a video \n{}```"
            result = ""
            for video in videos:
                result = result + "{}\n"
            result = list_format.format(result)
            return {"select": result.format(*videos), "hidden": hidden_videos}
            # return videos[0]
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            return "An error occurred."

    @commands.command(help='Fanfiction search', description='Basic AO3 search function, fetches random result '
                                                            'from the first page.', aliases=["ao3", "fanfiction"])
    async def fic(self, *query):
        search_url = "http://archiveofourown.org/works/search?utf8=✓&work_search[query]="
        link_xpath = '//*[@class="work blurb group"]'
        full_query = search_url + tools.aooo_conform('+'.join(query))
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
            selected = choice(results)
            list_marker = "```"
            info = selected["title"]+": "+selected["link"]+"\n"\
                + list_marker+selected["tags"]+"\n\n"+selected["summary"]+list_marker
            return await self.bot.say(info)
        else:
            return await self.bot.say("No result.")

    @commands.command(help='Returns the top result from YouTube', description='Searches youtube for a term '
                                                                              'and returns the top result.',
                      aliases=["youtube", "video"], pass_context=True)
    async def yt(self, ctx, *query):
        video = self.youtube_search(query)["hidden"][0]
        await self.bot.say(video)


def setup(bot):
    bot.add_cog(Search(bot))