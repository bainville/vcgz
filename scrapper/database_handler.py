import pymongo 



class DatabaseInserter:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.database = self.client["mydatabase"]
