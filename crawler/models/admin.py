"""
    行政区 类
"""

from model import MongoModel


class Admin(MongoModel):
    def __init__(self, admin_id, name=None):
        super().__init__(table_name="admin")
        self.admin_id = admin_id
        self.name = name
        self.spot_id_list = []

    def add_spot_id(self, spot_id):
        self.spot_id_list.append(spot_id)

    def to_json(self):
        return {
            'admin_id': self.admin_id,
            'name': self.name,
            'spot_id': self.spot_id_list
        }

    def insert(self, mongo):
        super().insert(mongo, self.to_json())
