#!/usr/bin/env python3
from distutils.command.clean import clean
from hashlib import new
from re import sub
import urllib
import json
import subprocess
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re  


url = "https://www.youtube.com/c/JLMelenchon/videos"
url = "https://www.youtube.com/watch?v=D30s3Yzb4Vc"


# TODO implement me and test me
def getContentFromSubTitleFile(video_id: str) -> str:
    pass

def isContinuationOfLastLine(lastline:str, newline:str)->bool:
    return lastline.rstrip(" ")==newline.split(" ")[0]

class VideoDataExtractor:
    def __init__(self, video_id):
        self.__parse(video_id)

    def getSubtitle(self) -> str:
        return self.subtitle.lstrip(" ")

    def getDate(self) -> datetime:
        return self.upload_date

    def getPersonalityName(self) -> str:
        return self.personalityname

    def __parse_json_file(self,json_filename:str)->None:
        json_file=open(json_filename)
        data=json.load(json_file)
        try: 
            date_string=data['upload_date']
            year=date_string[0:4]
            month=date_string[4:6]
            day=date_string[6:8]
            self.upload_date=datetime(int(year),int(month),int(day))
        except Exception as e:
            print (e)

    def __parse_subtitle(self,subtitle_filename:str)->None:
        self.subtitle=str()
        line=str()
        one_line_before=str()
        content = [content_line.rstrip('\n').rstrip(" ") for content_line in open(subtitle_filename)]
        for content_line in content[3:]:
            one_line_before=line
            if len(content_line)>0 and not "-->" in content_line:
                clean_content=re.sub(r'\<.*\>',r'',content_line)
                if clean_content==one_line_before:
                    continue 
                line=clean_content
                if not isContinuationOfLastLine(one_line_before,line):
                    self.subtitle=self.subtitle+" "+one_line_before
        self.subtitle=self.subtitle+" "+line
            
        

    def __parse(self, video_id: str):
        all_files = [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]
        for filename in all_files:
            if video_id in filename and ".fr.vtt" in filename :
                self.personalityname=filename.rstrip(f'-{video_id}.fr.vtt')
                json_filename=filename.rstrip('.fr.vtt')+'.info.json'
                description_filename=filename.rstrip('.fr.vtt')+'.description'
                self.__parse_json_file(json_filename)
                self.__parse_subtitle(filename)
                break


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
        for video_id in self.list_newly_download_id():
            print(f"Extracting information for video id: {video_id}")
            extractor = VideoDataExtractor(video_id)
            print (f"Video was from {extractor.getPersonalityName()}")
            
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
        command = [
            "youtube-dl",
            "--skip-download",
            "--write-annotations",
            "--write-description",
            "--write-info-json",
            "--no-overwrite",
            "--download-archive",
            "--write-info-json",
            "--write-auto-sub",
            "--sub-lang=fr",
            "--output",
            f"{self.personality_name}-%(id)s",
            self.channel_url,
        ]
        print(" ".join(command))

        spc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
        )
        spc.communicate()
        spc.wait()


def main():
    melanchon = Source("Melanchon", url)
    melanchon.proceed()


if __name__ == "__main__":
    main()
