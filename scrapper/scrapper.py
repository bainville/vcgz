#!/usr/bin/env python3
import inspect 
import json
import subprocess
import os
from os import listdir
from os.path import isfile, join
import argparse
import yaml

from database_inserter import DatabaseInserter


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


KEYS_FROM_JSON=['title','duration','channel','view_count','average_rating','upload_date','fulltitle','tags','categories','playlist','playlist_title']

def isContinuationOfLastLine(lastline:str, newline:str)->bool:
    return lastline.rstrip(" ")==newline.split(" ")[0]

def initializeData()->dict:
    data=dict()
    for key in ['video_id','personality_name','subtitle','query_url']+KEYS_FROM_JSON:
        data[key]=""
    return data

def getCleanedContent(content:str)->str: 
    clean=str()
    if not '<' in content: 
        return content
    for part in content.split('<'):
        if not '>' in part:
            clean=part
            continue
        subparts=part.split('>')
        if len(subparts)>0:
            clean=clean+subparts[1]
    return clean



class InputReader:
    def __init__(self,yaml_input_file):
        if (not os.path.isfile(yaml_input_file)):
            raise Exception(f"Input file not found {yaml_input_file}")
        with open(yaml_input_file, 'r') as stream:
            self.data=yaml.safe_load(stream)
            
class VideoDataExtractor:
    def __init__(self, video_id,query_url):
        self.data=initializeData()
        self.data['video_id']=video_id
        self.data['query_url']=query_url
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
        two_line_before=str()
        content = [content_line.rstrip('\n').rstrip(" ") for content_line in open(subtitle_filename)]
        for content_line in content[3:]:
            two_line_before=one_line_before
            one_line_before=line
            if len(content_line)>0 and not "-->" in content_line:
                clean_content=getCleanedContent(content_line)
                if clean_content==one_line_before:
                    continue 
                line=clean_content
                if not isContinuationOfLastLine(one_line_before,line) and not isContinuationOfLastLine(two_line_before,line):
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
                for f in [description_filename,json_filename,filename]:
                    full_file_path=os.path.join(os.getcwd(),f)
                    if (os.path.isfile(full_file_path)):
                        os.remove(full_file_path)
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
            extractor = VideoDataExtractor(video_id,self.channel_url)
            extracted_metadata.append(extractor.getData())
            print (f"Video was from {extracted_metadata[-1]['personality_name']}")

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
    parser = argparse.ArgumentParser(description="Get metadata from youtube video and insert them into the database")
    parser.add_argument("-i", "--input", help="Just a flag argument" ,nargs='+',default=[os.path.join(currentdir,"input.yaml")])
    args = parser.parse_args()
    input = InputReader(args.input[0])
    for key in input.data:
        for url in input.data[key]:
            source = Source(key, url)
            extracted_metadata=source.proceed()
            for metadata in extracted_metadata:
                database_inserter.insertVideoRecord(metadata)

if __name__ == "__main__":
    main()
