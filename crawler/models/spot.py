
class Spot:
    def __init__(self, spot_name, city):
        self.spot_name = spot_name
        self.city = city    # todo 设定城市
        self.shop_list = []

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
            'spot_name': self.spot_name,
            'city': self.city,
            'shop_list': self.shop_list
        }

    def insert(self, mongodb):
        mongodb.insert(self.TABLE_NAME, self.to_json())

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
