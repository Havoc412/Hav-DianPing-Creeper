# from crawler.utils.pinyin import get_pinyin
from Crawler.crawler.utils.pinyin import get_pinyin


class City:
    def __init__(self, city_CN=None, admin_list=[]):
        self.city_CN = city_CN
        self.city_EN = get_pinyin(city_CN)
        self.admin_list = admin_list

        self.TABLE_NAME = "city"
        self.spot_list = []

    def insert(self, mongo):
        mongo.insert(self.TABLE_NAME, self.to_json())

    def add_admin(self, admin):
        """
        先记录 admin_id，用于保存 DB；
        再记录 spot_id，用于后续遍历任务。
        :param admin: Admin 类
        :return:
        """
        self.admin_list.append({
            'admin_id': admin.admin_id,
            'admin_name': admin.name
        })
        self.extend_spot(admin.spot_list)

    def extend_spot(self, spot_list):
        # 用于遍历
        self.spot_list.extend(spot_list)

    def to_json(self):
        return {
            'city_CN': self.city_CN,
            'city_EN': self.city_EN,
            'admin_list': self.admin_list
        }

    def get_spot_list(self):
        """ 去重 """
        unique_list = {d['spot_id']: d for d in self.spot_list}.values()
        self.spot_list = list(unique_list)
        return unique_list

    @classmethod
    def from_db(cls, city):
        return cls(city_CN=city['city_CN'], admin_list=city['admin_list'])
