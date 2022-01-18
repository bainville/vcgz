#!/usr/bin/env python3
import urllib
import json
import subprocess
import os
from os import listdir
from os.path import isfile, join


url = "https://www.youtube.com/c/JLMelenchon/videos"
url = "https://www.youtube.com/watch?v=D30s3Yzb4Vc"


class Video:
    def __init__(self):
        pass

    def getSubtitle() -> str:
        pass

    def getDate() -> str:
        pass

    def getPersonalityName() -> str:
        pass

    def parse(download_data_id: str):
        pass


class Source:
    def __init__(self, personality_name=str, channel_url=str):
        if not personality_name.strip(""):
            raise Exception("contact_name empty")
        if not channel_url.strip(""):
            raise Exception("channel_url empty")
        self.personality_name = personality_name
        self.channel_url = channel_url

    def proceed(self):
        self.get_all_video_in_channel()
        self.list_newly_download_id()

    def list_newly_download_id(self):
        all_files = [
            filename
            for filename in listdir(os.getcwd())
            if isfile(join(os.getcwd(), filename))
        ]
        only_file_for_this_personality = [
            filename for filename in all_files if (self.personality_name in filename)
        ]
        only_ids = [
            filename.lstrip(f"{self.personality_name}-").split(".")[0]
            for filename in only_file_for_this_personality
            if (".vtt" in filename)
        ]
        return only_ids

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
                "--output",
                f"{self.personality_name}-%(id)s",
                self.channel_url,
            ],
            stdout=subprocess.PIPE,
        )
        spc.communicate()
        spc.wait()

melanchon=Source("Melanchon",url)
melanchon.proceed()
