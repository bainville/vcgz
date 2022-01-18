#!/usr/bin/env python3 
import urllib
import json
API_KEY="AIzaSyAnyhQ6E_ut2exthm8pHXofFrjb0DUw8dg"
channel_id="UCk-_PEY3iC6DIGJKuoEe9bw"


# class Video:
#     def __init__(self,url,)


class Source:
    def __init__(self, contact_name=str, channel_id=str):
        if not contact_name.strip(""):
            raise Exception ("contact_name empty")
        if not channel_id.strip(""):
            raise Exception ("channel_id empty")
        self.contact_name=contact_name 
        self.channel_id=channel_id

    def get_all_video_in_channel(channel_id):
        base_video_url = 'https://www.youtube.com/watch?v='
        base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

        first_url = base_search_url+f"key={API_KEY}&channelId={self.channel_id}&part=snippet,id&order=date&maxResults=25"

        video_links = []
        url = first_url
        while True:
            inp = urllib.request.urlopen(url,timeout=3)
            resp = json.load(inp)

            for i in resp['items']:
                if i['id']['kind'] == "youtube#video":
                    video_links.append(base_video_url + i['id']['videoId'])

            try:
                next_page_token = resp['nextPageToken']
                url = first_url + '&pageToken={}'.format(next_page_token)
            except:
                break
        return video_links

    def get
