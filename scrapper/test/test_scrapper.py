import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from scrapper import VideoDataExtractor
from scrapper import isContinuationOfLastLine
from scrapper import initializeData


def testInitializeData():
    initialized_data = initializeData()
    for expected_key in [
        "video_id",
        "personality_name",
        "subtitle",
        "title",
        "duration",
        "channel",
        "view_count",
        "average_rating",
        "upload_date",
        "fulltitle",
        "tags",
        "categories",
        "playlist",
        "playlist_title",
    ]:
        assert expected_key in initialized_data.keys()

def testDataExtaction():
    video_id = "D30s3Yzb4Vc"
    unit = VideoDataExtractor(video_id)
    expected_subtitle = "bonjour jean luc mélenchon merci beaucoup d'avoir accepté notre invitation vous êtes à fort-de-france où martin et que vous étiez d'ailleurs en guadeloupe ces derniers jours les départements d'outre-mer où la vaccination a du mal à convaincre est-ce que ce pass vaccinale annoncée pourrait changer les choses je crains que ça ne fasse que tout aggravé car ici on en a été à avoir des charges de police dans l'hôpital c'est"
    expected_data = initializeData()
    expected_data["video_id"]=video_id
    expected_data["subtitle"] = expected_subtitle
    expected_data["personality_name"] = "Melanchon"
    expected_data[
        "title"
    ] = "Le pass vaccinal va aggraver les tensions - M\u00e9lenchon sur TF1"
    expected_data["duration"] = 221
    expected_data["channel"] ="JEAN-LUC M\u00c9LENCHON"
    expected_data["view_count"] = 167322
    expected_data["average_rating"] = None
    expected_data["upload_date"] = "20211218"
    expected_data["fulltitle"] ="Le pass vaccinal va aggraver les tensions - M\u00e9lenchon sur TF1"
    expected_data["tags"] = [
        "pass vaccinal",
        "pass sanitaire",
        "vaccin",
        "vaccination",
        "taubira",
        "hidalgo",
        "primaire",
    ]
    expected_data["categories"] = ["News & Politics"]
    expected_data["playlist"] = None
    expected_data["playlist_title"]

    assert(unit.getData() == expected_data)



def testisContinuationOfLastLine():
    line = "vous etes"
    one_line_before = "vous"
    assert True == isContinuationOfLastLine(one_line_before, line)
    assert False == isContinuationOfLastLine(line, one_line_before)
