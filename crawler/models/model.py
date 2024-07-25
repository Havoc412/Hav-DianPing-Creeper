"""
model 的基类
"""


class MongoModel:
    def __init__(self, table_name):
        self.table_name = table_name

    def insert(self, mongo, data):
        mongo.insert(self.table_name, data)
