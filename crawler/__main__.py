from crawler.core import application


class DaZhongDianPing(application):
    def __init__(self, config_file, application):
        super().__init__(config_file, application)
        # 获取urls
        self.page_start = self.config["page_start"]
        self.page_end = self.config["page_end"]
        self.urls_comment = self.get_urls_comment()

    def get_urls_comment(self):
        urls_comment = [self.base_url_comment.format(self.shop_id, _) for _ in range(self.page_start, self.page_end+1)]
        return urls_comment


def main():
    # 爬取评论图片
    print("*****请注意更新Cookie和IP代理！！！*****")
    print("*****请注意更新Cookie和IP代理！！！*****")
    print("*****请注意更新Cookie和IP代理！！！*****")
    dianping = DaZhongDianPing(config_file="config/config.yaml", application="dazhongdianping")
    # dianping.crawl_comments()
    # dianping.crawl_shop_info()
    dianping.crawl_search()


if __name__ == "__main__":
    main()


    