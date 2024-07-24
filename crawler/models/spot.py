
class Spot:
    def __init__(self, spot_name):
        self.spot_name = spot_name
        self.shop_list = []

    def add_shop_list(self, shop_id, shop_name):
        self.shop_list.append({
            'shop_id': shop_id,
            'shop_name': shop_name
        })

    def to_json(self):
        return {
            'spot_name': self.spot_name,
            'shop_list': self.shop_list
        }


if __name__ == '__main__':
    spot = Spot("WHU")
    spot.add_shop_list("123", "WHU")
    spot.add_shop_list("456", "WHU")
    spot.add_shop_list("789", "WHU")

    print(spot.to_json())
