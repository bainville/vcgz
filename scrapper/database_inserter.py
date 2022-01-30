#!/usr/bin/env python3
import pymongo 
import urllib3
import urllib




class DatabaseInserter:
    def __init__(self):
        password="HASI0KjXi@hk1uTUV&9T8u6q0C52VqD2h?c#goH0"
        self.client= pymongo.MongoClient(f"mongodb+srv://vcgz_admin:"+urllib.parse.quote(password)+"@veilleconcurentielle.zfgil.mongodb.net/vcdataout?retryWrites=true&w=majority")
        self.database = self.client['recorded_video']
        self.data_table=self.database['video_subtitle']
    
    def insertVideoRecord(self,video_metadata:dict):
        self.data_table.insert_one(video_metadata)
        

def main():
    db=DatabaseInserter()


if __name__ == "__main__":
    main()
