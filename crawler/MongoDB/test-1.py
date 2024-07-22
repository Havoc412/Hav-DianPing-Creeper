from pymongo import MongoClient


if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    # 选择一个数据库
    db = client['CFT-DATA-DianPing']

    # 选择一个集合
    collection = db['shopInfo']

    #
    collection.insert_one({'name': 'Alice', 'age': 25})
    # collection.insert_many([
    #     {'name': 'Bob', 'age': 30},
    #     {'name': 'Charlie', 'age': 35}
    # ])

    # 查询单个文档
    user = collection.find_one({'name': 'Alice'})
    print(user)
    print("\n")

    # 查询所有文档
    for user in collection.find({}):
        print(user)

    # 删除单个文档
    # collection.delete_one({'name': 'Alice'})

    # 删除多个文档
    collection.delete_many({'age': 31})