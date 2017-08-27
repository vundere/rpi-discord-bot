from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from random import randrange

import json

CONF_FILE = 'cfg/bot_config.json'
with open(CONF_FILE, 'r') as conf:
    file = json.load(conf)
    DEVELOPER_KEY = file["youtube_api_key"]


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def search(query, max_results=1):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY, cache_discovery=False)

    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results
    ).execute()

    videos = []
    for result in search_response.get("items", []):
        if result["id"]["kind"] == "youtube#video":
            # videos.append("%s (%s)" % (result["snippet"]["title"],
            #                            result["id"]["videoId"]))
            videos.append(result["id"]["videoId"])

    try:
        video = videos[randrange(0, len(videos))]
        return "https://www.youtube.com/watch?v=" + video
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        return "An error occurred."
