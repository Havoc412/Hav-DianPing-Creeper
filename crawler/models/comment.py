
class Comment:
    def __init__(self, shop_id, user_id):
        self.shop_id = shop_id
        self.user_id = user_id
        self.rank = {
            'taste': None,
            'environment': None,
            'service': None
        }
        self.words = None
        self.time = None
        self.pic_num = None

    def to_json(self):
        """
        将评论数据转换为 JSON 格式的字典。
        """
        return {
            'shop_id': self.shop_id,
            'user_id': self.user_id,
            'rank': self.rank,
            'words': self.words,
            'time': self.time,
            'pic_num': self.pic_num
        }


if __name__ == '__main__':
    # 使用示例
    # 创建 Comment 对象
    comment = Comment()

    # 赋值
    comment.shop_id = '001'
    comment.user_id = 'u123'
    comment.rank['taste'] = 5.0
    comment.rank['environment'] = 4.5
    comment.rank['service'] = 4.8
    comment.words = '非常满意'
    comment.time = '2021-07-23 10:00'
    comment.pic_num = 3
    print(comment.to_json())
