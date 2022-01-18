#!/usr/bin/env python3
import urllib
import json
import subprocess



url = "https://www.youtube.com/c/JLMelenchon/videos"
url = "https://www.youtube.com/watch?v=D30s3Yzb4Vc"


class Source:
    def __init__(self, contact_name=str, channel_url=str):
        if not contact_name.strip(""):
            raise Exception("contact_name empty")
        if not channel_url.strip(""):
            raise Exception("channel_url empty")
        self.contact_name = contact_name
        self.channel_url = channel_url

    def get_all_video_in_channel(self):
        spc = subprocess.Popen(
            [
                "youtube-dl",
                "--skip-download",
                "--write-annotations",
                "--write-description",
                "--write-info-json",
                "--no-overwrite",
                "--download-archive",
                "--write-info-json",
                "--write-sub",
                "--write-auto-sub",
                self.channel_url,
            ],
            stdout=subprocess.PIPE,
        )
        spc.communicate()
        spc.wait()

    
