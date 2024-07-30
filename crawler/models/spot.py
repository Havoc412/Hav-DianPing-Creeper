
class Spot:
    def __init__(self, spot_id, spot_name, city, shop_list=[]):
        self.spot_id = spot_id
        self.spot_name = spot_name
        self.city = city    # 设定城市
        self.shop_list = shop_list

        # 存储 Shop 类，方便遍历。
        self.shop_list_class = []
        self.TABLE_NAME = 'spot'

    def add_shop_list(self, shop):
        self.shop_list.append({
            'shop_id': shop.shop_id,
            'shop_name': shop.shop_name
        })
        self.shop_list_class.append(shop)

    def to_json(self):
        return {
            'spot_id': self.spot_id,
            'spot_name': self.spot_name,
            'city': self.city,
            'shop_list': self.shop_list
        }

    def insert(self, mongodb):
        # mongodb.insert(self.TABLE_NAME, self.to_json())
        existing_spot = mongodb.db[self.TABLE_NAME].find_one({'spot_id': self.spot_id})

        if existing_spot:
            # 如果存在，合并 shop_list
            existing_shop_list = existing_spot['shop_list']

            # 将现有的 shop_list 转换为字典，使用 shop_id 作为键
            existing_shop_dict = {shop['shop_id']: shop['shop_name'] for shop in existing_shop_list}

            # 将当前的 shop_list 也转换为字典
            current_shop_dict = {shop['shop_id']: shop['shop_name'] for shop in self.shop_list}

            # 合并字典（去重）
            merged_shop_list = {**existing_shop_dict, **current_shop_dict}

            # 将合并后的字典转换回列表形式
            merged_shop_list_as_list = [{'shop_id': shop_id, 'shop_name': shop_name} for shop_id, shop_name in
                                        merged_shop_list.items()]
            # 更新文档
            mongodb.update_data(
                self.TABLE_NAME,
               [
                   {'spot_id': self.spot_id},
                   {'$set': {'shop_list': merged_shop_list_as_list}}
               ]
            )
        else:
            # 如果不存在，直接插入新文档
            mongodb.insert(self.TABLE_NAME, self.to_json())

    @classmethod
    def from_db(cls, spot):
        return cls(spot_id=spot['spot_id'], spot_name=spot['spot_name'],
                   city=spot['city'], shop_list=spot['shop_list'])

    # def get_shop_id_list(self):
    #     """
    #     获取 shop_id 来用于后续遍历。
    #     :return:
    #     """
    #     return [shop['shop_id'] for shop in self.shop_list]


if __name__ == '__main__':
    spot = Spot("WHU")
    spot.add_shop_list("123", "WHU")
    spot.add_shop_list("456", "WHU")
    spot.add_shop_list("789", "WHU")

    print(spot.to_json())

    # print(spot.get_shop_id_list())
