
class Shop:
    def __init__(self, shop_id):
        self.shop_id = shop_id
        self.shop_name = None
        self.type = None
        self.rank = {
            'overall': None,
            'taste': None,
            'environment': None,
            'service': None
        }
        self.per_cost = None
        self.comment_num = None
        self.address = {
            'brief': None,
            'detail': None,
        }
        self.phone_number = []
        self.cuisine = {
            "main": [],
            "other": []
        }
        self.business_hours = None

    def to_json(self):  # tip 这种工作交给 GPT 就是方便。
        return {
            'shop_id': self.shop_id,
            'shop_name': self.shop_name,
            'type': self.type,
            'rank': self.rank,
            'per_cost': self.per_cost,
            'comment_num': self.comment_num,
            'address': self.address,
            'phone_number': self.phone_number,
            'cuisine': self.cuisine,
            'business_hours': self.business_hours
        }


if __name__ == "__main__":
    # 示例用法
    shop = Shop(shop_id=1)
    shop.shop_name = "美食店"
    shop.type = "餐厅"
    shop.rank['overall'] = 4.5
    shop.per_cost = 100
    shop.comment_num = 50
    shop.address['brief'] = "某街道"
    shop.address['detail'] = "某街道某号"
    shop.phone_number = ["123456789", "987654321"]
    shop.cuisine['main'] = ["中餐"]
    shop.cuisine['other'] = ["快餐", "小吃"]
    shop.business_hours = "10:00-22:00"

    # 转换为 JSON 格式
    shop_json = shop.to_json()
    print(shop_json)

