
import os 
import sys 
import inspect 

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from database_inserter import DatabaseInserter
from scrapper import initializeData


def testDatabaseConnection():
    database_inserter=DatabaseInserter()


def testInsertionIntoDatabase():
    data_to_be_inserted=initializeData()
    data_to_be_inserted["video_id"]="123"
    data_to_be_inserted["personality_name"]="foobar"
    database_inserter=DatabaseInserter()
    database_inserter.insertVideoRecord(data_to_be_inserted)
