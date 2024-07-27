import logging
from pymongo import MongoClient

from crawler.utils.yaml_utils import load_yaml  # 适用于从 crawler 开始运行
# from Crawler.crawler.utils.yaml_utils import load_yaml

# 配置日志记录
logging.basicConfig(filename="MongoDB.log", level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class Mongo:
    def __init__(self, config_file, application):
        self.config = load_yaml(config_file)[application]  # 采用相似的方式来获取基本配置
        self.dbname = self.config['db_name']
        self.client = self.link_MongoClient()
        self.db = self.client[self.dbname]  # link to db

    def link_MongoClient(self):
        host = self.config['host']
        port = self.config['port']
        return MongoClient(host, port)

    def insert(self, collection_name: str, data: dict) -> None:
        """
        插入数据到指定的 MongoDB 集合中。
        :param collection_name: 集合名。
        :param data: 一个字典，包含要插入的数据。
        """
        if isinstance(data, dict):
            collection = self.db[collection_name]
            collection.insert_one(data)
        else:
            logging.error(f"Insert failed: Data provided is not a dictionary - {data}")
            raise ValueError("Data must be a dictionary")

    def find_data(self, collection_name: str, query: dict) -> list:
        """
        根据提供的查询参数在指定集合中查询数据。
        :param collection_name: 集合名。
        :param query: 一个字典，表示查询条件。
        :return: 返回查询结果的列表。
        """
        collection = self.db[collection_name]
        results = collection.find(query)
        return [result for result in results]

    def find_last_data(self, collection_name: str):
        collection = self.db[collection_name]
        last_cursor = collection.find().sort('_id', -1).limit(1)
        last_element = list(last_cursor)
        if last_element:
            last_dict = last_element[0]
        else:
            last_dict = None
        return last_dict

    def find_admin_by_city(self, city_admin_list):
        admin_id_list = [item['admin_id'] for item in city_admin_list]

        collection = self.db['admin']
        matching_admins = list(collection.find({'admin_id': {'$in': admin_id_list}}))
        return matching_admins

    def delete_data(self, collection_name: str, query: dict) -> None:
        """
        根据查询条件在指定集合中删除数据。
        :param collection_name: 集合名。
        :param query: 一个字典，表示删除条件。
        """
        collection = self.db[collection_name]
        result = collection.delete_many(query)
        print(f"delete {result} element from {collection_name} by {query}")

    def update_data(self, collection_name: str, query):
        collection = self.db[collection_name]
        res = collection.update_one(query[0], query[1])

        # 打印返回结果
        if res.upserted_id is not None:
            print(f'Inserted document ID: {res.upserted_id}')  # 新插入文档的 ID
        else:
            print('No document was inserted.')

    def close_connection(self) -> None:
        """
        关闭数据库连接。
        """
        self.client.close()


if __name__ == "__main__":
    mongo = Mongo(config_file="../../config/config.yaml", application="MongoDB")

    mongo.insert("shopInfo", {
        'name': 'test link',
        'age': 723
    })
