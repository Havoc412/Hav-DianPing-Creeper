
class Spot:
    def __init__(self, spot_name):
        self.spot_name = spot_name
        self.shop_ids = []

    def add_shop_id(self, shop_id):
        self.shop_ids.append(shop_id)

    def to_json(self):
        return {
            'spot_name': self.spot_name,
            'shop_ids': self.shop_ids
        }


if __name__ == '__main__':
    spot = Spot("WHU")
    spot.add_shop_id("123")
    spot.add_shop_id("456")
    spot.add_shop_id("789")

    print(spot.to_json())
