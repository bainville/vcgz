#!/usr/bin/env python3
import pymongo 
import urllib
from add_summary import update_field_on_filter

class DatabaseInserter:
    def __init__(self):
        password="HASI0KjXi@hk1uTUV&9T8u6q0C52VqD2h?c#goH0"
        self.client= pymongo.MongoClient(f"mongodb+srv://vcgz_admin:"+urllib.parse.quote(password)+"@veilleconcurentielle.zfgil.mongodb.net/vcdataout?retryWrites=true&w=majority")
        self.database = self.client['recorded_video']
        self.data_table=self.database['video_subtitles']
    
    def insertVideoRecord(self,video_metadata:dict):
        if len(list(self.data_table.find({'video_id':video_metadata['video_id']})))==0:
            self.data_table.insert_one(video_metadata)
            return 1
        else:
            update_field_on_filter(self.client,'recorded_video','video_subtitles',{'video_id':video_metadata['video_id']},'view_count',video_metadata['view_count'], print_df=False)
            print('We have already '+video_metadata['video_id'])
            return 0
        