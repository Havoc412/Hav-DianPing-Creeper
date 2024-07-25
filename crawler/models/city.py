from crawler.utils.pinyin import get_pinyin


class City:
    def __init__(self, city_CN):
        self.city_CN = city_CN
        self.city_EN = get_pinyin(city_CN)
        self.admin_id_list = []

        self.TABLE_NAME = "city"
        self.spot_id = []

    def add_admin(self, admin):
        """
        先记录 admin_id，用于保存 DB；
        再记录 spot_id，用于后续遍历任务。
        :param admin:
        :return:
        """
        self.admin_id_list.append(admin.admin_id)
        self.admin_id_list.extend(admin.spot_id_list)

    def to_json(self):
        return {
            'city_CN': self.city_CN,
            'city_EN': self.city_EN,
            'admin_id_list': self.admin_id_list
        }

    def insert(self, mongo):
        mongo.insert(self.TABLE_NAME, self.to_json())
