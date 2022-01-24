import os
import sys
import inspect
import datetime



currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from scrapper import VideoDataExtractor 
from scrapper import isContinuationOfLastLine

def testgetPersonalityName():
    video_id="D30s3Yzb4Vc"
    unit=VideoDataExtractor(video_id)
    assert("Melanchon"==unit.getPersonalityName())


def testVideoDataExtraction():
    video_id="D30s3Yzb4Vc"
    unit=VideoDataExtractor(video_id)
    expected_date=datetime.datetime(2021,12,18)
    assert(unit.getDate()==expected_date)
    
def testSubtitleExtraction():
    video_id="D30s3Yzb4Vc"
    unit=VideoDataExtractor(video_id)
    expected_subtitle="bonjour jean luc mélenchon merci beaucoup d'avoir accepté notre invitation vous êtes à fort-de-france où martin et que vous étiez d'ailleurs en guadeloupe ces derniers jours les départements d'outre-mer où la vaccination a du mal à convaincre est-ce que ce pass vaccinale annoncée pourrait changer les choses je crains que ça ne fasse que tout aggravé car ici on en a été à avoir des charges de police dans l'hôpital c'est"
    assert(unit.getSubtitle()==expected_subtitle)   


def testisContinuationOfLastLine():
    line="vous etes"
    one_line_before="vous"
    assert(True==isContinuationOfLastLine(one_line_before,line))
    assert(False==isContinuationOfLastLine(line,one_line_before))
