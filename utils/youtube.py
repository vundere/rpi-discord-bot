from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json

CONF_FILE = 'cfg/bot_config.json'
with open(CONF_FILE, 'r') as conf:
    file = json.load(conf)
    DEVELOPER_KEY = file["youtube_api_key"]


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def search(query, max_results=10):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY, cache_discovery=False)

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
