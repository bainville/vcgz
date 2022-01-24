import os
import sys
import inspect
import datetime


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from scrapper import VideoDataExtractor 

def testgetPersonalityName():
    video_id="D30s3Yzb4Vc"
    unit=VideoDataExtractor(video_id)
    assert("Melanchon"==unit.getPersonalityName())


def testVideoDataExtraction():
    video_id="D30s3Yzb4Vc"
    unit=VideoDataExtractor(video_id)
    expected_date=datetime.datetime(2021,12,18)
    assert(unit.getDate()==expected_date)
    
