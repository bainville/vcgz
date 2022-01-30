#!/usr/bin/env python3
from distutils.command.clean import clean
from hashlib import new
from re import sub
import json
import subprocess
import os
from os import listdir
from os.path import isfile, join
from os import listdir
from os.path import isfile, join
import re  


from database_inserter import DatabaseInserter


url = "https://www.youtube.com/c/JLMelenchon/videos"
url = "https://www.youtube.com/watch?v=D30s3Yzb4Vc"


KEYS_FROM_JSON=['title','duration','channel','view_count','average_rating','upload_date','fulltitle','tags','categories','playlist','playlist_title']

def isContinuationOfLastLine(lastline:str, newline:str)->bool:
    return lastline.rstrip(" ")==newline.split(" ")[0]

def initializeData()->dict:
    data=dict()
    for key in ['video_id','personality_name','subtitle']+KEYS_FROM_JSON:
        data[key]=""
    return data

class VideoDataExtractor:
    def __init__(self, video_id):
        self.data=initializeData()
        self.data['video_id']=video_id
        self.__parse(video_id)

    def getData(self)->dict: 
        return self.data

    def __parse_json_file(self,json_filename:str)->None:
        json_file=open(json_filename)
        data=json.load(json_file)
        for key in KEYS_FROM_JSON:
            try: 
                self.data[key]=data[key]
            except Exception as e: 
                print(e)

    def __parse_subtitle(self,subtitle_filename:str)->None:
        subtitle=str()
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
                    subtitle=subtitle+" "+one_line_before
        subtitle=subtitle+" "+line
        subtitle=subtitle.lstrip(" ")
        self.data['subtitle']=subtitle

    def __parse(self, video_id: str):
        all_files = [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]
        for filename in all_files:
            if video_id in filename and ".fr.vtt" in filename :
                self.data['personality_name']=filename.rstrip(f'-{video_id}.fr.vtt')
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
        extracted_metadata=list()
        for video_id in self.list_newly_download_id():
            print(f"Extracting information for video id: {video_id}")
            extractor = VideoDataExtractor(video_id)
            print (f"Video was from {extractor.getPersonalityName()}")
            extracted_metadata.append(extractor.getData())

        return extracted_metadata
            
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
    database_inserter=DatabaseInserter()
    melanchon = Source("Melanchon", url)
    extracted_metadata=melanchon.proceed()
    for metadata in extracted_metadata:
        database_inserter.insertVideoRecord(metadata)



if __name__ == "__main__":
    main()
