from crawler.core import application


class DaZhongDianPing(application):
    def __init__(self, config_file, application):
        super().__init__(config_file, application)  # todo 第一入口的设定之后就写在这里
        # self.city = self.config["search_city"]  # 设定目标城市


def main():
    # 爬取评论图片
    print("*****请注意更新Cookie和IP代理！！！*****")
    print("*****请注意更新Cookie和IP代理！！！*****")
    print("*****请注意更新Cookie和IP代理！！！*****")
    dianping = DaZhongDianPing(config_file="config/config.yaml", application="dazhongdianping")
    dianping.crawl_search()  # todo 当前还是 第二入口 开始


if __name__ == "__main__":
    main()


    