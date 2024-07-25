"""
    行政区 类
"""

# from model import MongoModel
from crawler.models.model import MongoModel


class Admin(MongoModel):
    def __init__(self, admin_id, name=None):
        super().__init__(table_name="admin")
        self.admin_id = admin_id
        self.name = name
        self.spot_list = []

    def add_spot(self, spot_id, spot_name):
        self.spot_list.append({
            'spot_id': spot_id,
            'spot_name': spot_name
        })

    def to_json(self):
        return {
            'admin_id': self.admin_id,
            'name': self.name,
            'spot_list': self.spot_list
        }

    def insert(self, mongo):
        super().insert(mongo, self.to_json())
