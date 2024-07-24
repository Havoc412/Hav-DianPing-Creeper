import urllib
import urllib.request
import gzip
import os
import re
import time
import requests
import logging
import random
from bs4 import BeautifulSoup

from crawler.utils.yaml_utils import load_yaml
from crawler.utils.encode import encode_chinese
from crawler.utils.html import (
    read_html_from_file,
    get_rank_text,
    get_shop_info,
)

from crawler.models.comment import Comment
from crawler.models.spot import Spot
from crawler.models.shop import Shop
from crawler.MongoDB.Mongo import Mongo

logger = logging.getLogger(__name__)


class Crawl:
    def request(self, url, proxy_list, data=None, headers=None, method="GET"):
        # IP代理
        if len(proxy_list) > 0:
            # 随机从IP列表中选择一个IP
            proxy = random.choice(proxy_list)
            logger.info("IP代理:{}".format(proxy))
            # 基于选择的IP构建连接
            handle = urllib.request.ProxyHandler({proxy[0]: proxy[1]})
            opener = urllib.request.build_opener(handle)
            urllib.request.install_opener(opener=opener)
        print("Request url:", url)
        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)  # 实际上爬取 html 的操作只是一个 GET 的接口。
        response = self.urlopen(request)
        return response
    
    def urlopen(self, url):
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            logger.error("{}: {}".format(e, url.full_url))
            logger.error("cookie可能已失效，请更新cookie后重试！")
            raise Exception(e)
        return response

    def write_txt(self, path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def read_txt(self, path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content


def check_login(html):  # 因为 logger， 就先留在这个 py 了。
    """检查网页是否登录"""
    if re.search("登录失败", html):
        logger.info("网页未登录账号，请更新Cookie后重试！")
        raise Exception("网页未登录账号，请更新Cookie后重试！")


def proxy_is_availabel(proxy):
    try:
        # 设置重连次数
        requests.adapters.DEFAULT_RETRIES = 3
        proxy_dict = {proxy[0]:proxy[1]}
        res = requests.get(url="http://icanhazip.com/", timeout=2, proxies=proxy_dict)
        if res.text.strip() == proxy[1].split(":")[0]:
            return True
        else:
            logger.info(f"IP代理{proxy[0]}://{proxy[1]}无效！")
            print(f"IP代理{proxy[0]}://{proxy[1]}无效！")
            return False
    except:
        logger.info(f"IP代理{proxy[0]}://{proxy[1]}无效！")
        print(f"IP代理{proxy[0]}://{proxy[1]}无效！")
        return False


def sleep_random(delay):
    """
    在一定范围里，随机延迟
    :param delay:
    :return:
    """
    time.sleep(random.uniform(delay, delay+1))


class application():
    def __init__(self, config_file, application):
        self.crawler = Crawl()
        self.config = load_yaml(config_file)[application]
        # self.shop_id = self.config["shop_id"]  # shop_id !!  # todo list 之后就不该从 config 中获取，而是通过 search 动态获取了。
        # self.shop_name = None

        # url path
        self.base_url_search_food = self.config["search_food"]["base_url"]
        self.base_url_shop = self.config["base_url_shop"]
        self.base_url_comment = self.config["comment"]["base_url"]
        # 爬取的图片保存地址
        self.save_dir = self.config["save_dir"]
        os.makedirs(self.save_dir, exist_ok=True)
        # 爬取相关的参数
        self.crawl_delay = float(self.config["crawl_delay"])
        self.download_delay = float(self.config["download_delay"])
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
            'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
            "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ]
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh,zh-CN;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }
        # 更新headers
        for k, v in self.config["headers"].items():
            if v:
                self.headers[k] = v
        # logging设置
        log_file = os.path.join(self.save_dir, "{}.log".format(time.strftime('%Y%m%d_%H', time.localtime())))
        if self.config["set_logfile"]:
            hander = logging.FileHandler(filename=log_file)
        else:
            hander = logging.StreamHandler()
        logger.setLevel(logging.INFO)  # 设置日志级别
        # log格式
        fmt = '%(asctime)s - %(levelname)s: %(message)s'
        format_str = logging.Formatter(fmt)  # 设置日志格式
        hander.setFormatter(format_str)
        logger.addHandler(hander)
        # proxy
        if self.config["use_proxy"]:
            self.proxy_list = [_.split("|") for _ in self.config["proxy"]]
        else:
            self.proxy_list = []
        # 可用IP代理过滤
        self.filter_proxy()
        # 打印基本参数
        logger.info("header: {}".format(self.headers))
        logger.info("proxy: {}".format(self.proxy_list))
        # database link
        self.mongo = Mongo(config_file="config/config.yaml", application="MongoDB")
        # todo spot

    def filter_proxy(self):
        """检查IP代理池是否可用"""
        self.proxy_list = [_ for _ in self.proxy_list if proxy_is_availabel(_)]

    # def get_title(self, html):
    #     bs = BeautifulSoup(html, "html.parser")
    #     # 读取店铺名
    #     shop_name = bs.find("h1", class_="shop-name").string.strip()
    #     if len(shop_name) == 0:
    #         raise Exception("店铺名称为空！")  # 通过检查 Shop Name 的方式，来确保获取的 html 可用。
    #     self.shop_name = shop_name
    #     return shop_name

    """
    获取 html 数据的两种方式; from local is in html.py
    """
    def get_html_from_respose(self, url, save_path):
        """
        从网络上获取目标路径。
        :param url:
        :param save_path: 由外部确认保存的位置。
        :return:
        """
        sleep_random(self.crawl_delay)  #

        # check ip proxy: ip will be useless any time
        self.headers["User-Agent"] = random.choice(self.user_agent)
        self.filter_proxy()
        # link to url
        resp = self.crawler.request(url=url, proxy_list=self.proxy_list, headers=self.headers)
        if resp.code == 200:
            print(f">>> 链接{url}成功响应!")
            logger.info(f">>> 链接{url}成功响应!")
        else:
            print(f">>> 链接{url}响应失败:{resp.code}")
            logger.info(f">>> 链接{url}响应失败:{resp.code}")
        # get html
        html = resp.read()
        html = gzip.decompress(html).decode("utf-8")
        # save html
        check_login(html)
        self.crawler.write_txt(save_path, html)
        resp.close()
        return html

    """
    各类 crawler 的启动函数;
    """
    def crawl_comments(self, dir_path, shop):  # 启动入口
        """
        默认用于 comments; 整个任务的第三步。
        :param dir_path: 具体到 shop 的路径
        :param shop: 目标 shop 类
        :return:
        """
        page_start = self.config["comment"]["page_start"]
        page_end = self.config["comment"]["page_start"]
        cuisine = set()

        # 获取目标 urls
        def get_urls():
            return [self.base_url_comment.format(shop.shop_id, _) for _ in range(page_start, page_end+1)]

        # 一页页遍历
        for i, url in enumerate(get_urls()):
            # LOCAL TEST
            page_num = range(page_start, page_end+1)[i]
            html_path = os.path.join(dir_path, f"comment-page-{page_num}.html")

            html = self.get_html_from_respose(url, html_path)
            # html = read_html_from_file(html_path)  #

            check_login(html)  # check usable

            # 先获取 shop 信息
            if i == 0:
                get_shop_info(shop, html)

            # 下载 图片
            pic_dir = os.path.join(dir_path, f"comment-pic")
            if not os.path.exists(pic_dir):
                os.makedirs(pic_dir, exist_ok=True)
            # self.download_pic(html, pic_dir, page_num, self.proxy_list)

            recommend_cuisine = self.get_comments(html, pic_dir, shop.shop_id)
            cuisine.update(recommend_cuisine)

        # 从评论中获取各类 cuisine，然后再导入数据库。
        shop.cuisine['all'] = list(cuisine)
        shop.insert(self.mongo)
        print(f">>> 所有 comment && picture 已完成下载，请查看:\n{dir_path}")
        logger.info(f">>> 所有 comment && picture 已完成下载，请查看:\n{dir_path}")

    # def download_pic(self, html, pic_dir, page_num, proxy_list):
    #     bs = BeautifulSoup(html, "html.parser")
    #
    #     def is_img_and_has_data_big(tag):
    #         return tag.has_attr("data-big")  # 通过 tag 来获取指定元素，然后通过 IP 代理来获取图片。
    #
    #     items = bs.find_all(is_img_and_has_data_big)
    #     for i, item in enumerate(items):
    #         img_link = item.attrs["data-big"]
    #         # 获取无水印图片
    #         img_link = img_link.replace("joJrvItByyS4HHaWdXyO_I7F0UeCRQYMHlogzbt7GHgNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg", "")
    #         if not img_link.endswith(".jpg"):
    #             img_link = img_link.split(".jpg")[0]+".jpg"
    #         # 延时下载
    #         time.sleep(self.download_delay)
    #         logger.info("正在下载: {}".format(img_link))
    #         saveimg = os.path.join(pic_dir, f"p{page_num}_{i}{os.path.splitext(img_link)[-1]}")
    #         # IP代理
    #         if len(proxy_list) > 0:  # 还是用 IP代理 来请图床。
    #             # 随机从IP列表中选择一个IP
    #             proxy = random.choice(proxy_list)
    #             # 基于选择的IP构建连接
    #             handle = urllib.request.ProxyHandler({proxy[0]: proxy[1]})
    #             opener = urllib.request.build_opener(handle)
    #             urllib.request.install_opener(opener=opener)
    #         urllib.request.urlretrieve(img_link, saveimg)  # 下载链接内容

    """
        the function for comments
    """
    def get_comments(self, html, pic_dir, shop_id) -> set:
        """
        获取 comment 基本信息，
        同时返回 shop - cuisine 需要的内容
        :param shop_id:
        :param html:
        :param pic_dir:
        :return: shop-cuisine-other
        """
        recommend_cuisine = set()
        bs = BeautifulSoup(html, "html.parser")
        # mongo = Mongo(config_file="config/config.yaml", application="MongoDB")

        reviews_div = bs.find('div', class_="reviews-items")
        # 只获取子节点
        ul = reviews_div.find('ul')
        comments_li = ul.find_all('li', recursive=False)

        for index, comment_li in enumerate(comments_li):
            comment = Comment(shop_id=shop_id, user_id=index)
            # rank * 3
            rank_items = comment_li.find_all('span', class_="item")
            comment.rank['taste'], comment.rank['environment'], comment.rank['service'] = get_rank_text(rank_items)
            # words
            words_div = comment_li.find('div', class_="review-words")
            comment.words = words_div.text.strip()
            # pic
            reviews_pic = comment_li.find('div', class_="review-pictures")
            if reviews_pic is not None:
                comment.pic_num = self.download_pic_each_comment(reviews_pic, pic_dir, index, self.proxy_list)
            # time
            time_span = comment_li.find('span', class_="time")
            comment.time = time_span.text.strip()

            self.mongo.insert("comment", comment.to_json())

            # get the cuisine for shop
            recommend_div = comment_li.find('div', class_="review-recommend")
            if recommend_div is not None:
                for cuisine in recommend_div.find_all('a'):
                    recommend_cuisine.add(cuisine.text)
        return recommend_cuisine

    def download_pic_each_comment(self, pic_div, pic_dir, user_id, proxy_list):
        """"
        这是我后来写的单对评论的图片获取。
        """
        def is_img_and_has_data_big(tag):
            return tag.has_attr("data-big")  # 通过 tag 来获取指定元素，然后通过 IP 代理来获取图片。

        items = pic_div.find_all(is_img_and_has_data_big)
        for i, item in enumerate(items):
            img_link = item.attrs["data-big"]
            # 获取无水印图片
            img_link = img_link.replace("joJrvItByyS4HHaWdXyO_I7F0UeCRQYMHlogzbt7GHgNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg", "")
            if not img_link.endswith(".jpg"):
                img_link = img_link.split(".jpg")[0]+".jpg"
            # 延时下载
            time.sleep(self.download_delay)
            logger.info("正在下载: {}".format(img_link))
            saveimg = os.path.join(pic_dir, f"u{user_id}_{i}{os.path.splitext(img_link)[-1]}")
            # IP代理
            if len(proxy_list) > 0:  # 还是用 IP代理 来请图床。
                # 随机从IP列表中选择一个IP
                proxy = random.choice(proxy_list)
                # 基于选择的IP构建连接
                handle = urllib.request.ProxyHandler({proxy[0]: proxy[1]})
                opener = urllib.request.build_opener(handle)
                urllib.request.install_opener(opener=opener)
            urllib.request.urlretrieve(img_link, saveimg)  # 下载链接内容
        return len(items)

    def download_pic_single(self, img_link, save_path):
        """
        只负责完成 IP代理 到文件保存的任务。
        :param img_link:
        :param save_path:
        :return:
        """
        time.sleep(self.download_delay)
        logger.info("Downloading:{}".format(img_link))
        # 配置代理
        if len(self.proxy_list) > 0:
            # 随机从IP列表中选择一个IP
            proxy = random.choice(self.proxy_list)
            # 基于选择的IP构建连接
            handle = urllib.request.ProxyHandler({proxy[0]: proxy[1]})
            opener = urllib.request.build_opener(handle)
            urllib.request.install_opener(opener=opener)
        urllib.request.urlretrieve(img_link, save_path)  # 下载链接内容

    """
        crawl to shop
    """
    def crawl_shop_info(self, dir_path, shop):
        """
        未登录的 shop 主页，只有【营业时间】比较有价值；几乎都有。不再调用其他模块。
        :param shop: Shop 类。
        :param dir_path: 继承路径到 keyword
        :return:
        """
        url = self.base_url_shop.format(shop.shop_id)
        # get && save html
        html_path = os.path.join(dir_path, "shop-info.html")
        html = self.get_html_from_respose(url, html_path)
        # html = read_html_from_file("result/k37IMiQDsL5EYDfw/shop-info.html")  # TEST
        # get the core info
        bs = BeautifulSoup(html, "html.parser")
        business_hours_p = bs.find('p', class_='info-indent')  # 只获取第一个，也就是目标的营业时间
        item_span = business_hours_p.find('span', class_="item")
        if item_span:
            shop.business_hours = item_span.text.strip()

    # def get_shop_info(self, html):
    #     """
    #     但是 【特色菜】 并不好直接获取，所以更换方式了。而 shop 主页面目标信息过少，此函数弃用。
    #     :param html:
    #     :param pic_dir: 存储店铺 photo && 特色菜的文件夹。
    #     :return:
    #     """
    #     pass

    """
    crawl to search by keyword
    """
    def crawl_search(self, keyword=None):
        """
        作为 第二端口 ，获取店铺基本信息（部分），收集 shop_id 用于访问详情 && 评论。
        :param keyword: 此处 keyword 主要是特定的 景区名，然后通过大众点评的通道10，主要获取附近餐饮信息。
        :return:
        """
        keyword = self.config['search_pt']  # todo 之后从 city 的列表中获取。
        encode_keyword = encode_chinese(keyword)
        # get && save html
        dir_path = os.path.join(self.save_dir, f"{keyword}")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 遍历 search keyword
        page_start = self.config["search_food"]["page_start"]
        page_end = self.config["search_food"]["page_end"]
        spot = Spot(spot_name=keyword, city=self.city)

        def get_urls():
            return [self.base_url_search_food.format(encode_keyword, _) for _ in range(page_start, page_end + 1)]

        # todo 这里设计一个遍历，获取 50 ~ 100，先目标 5 页的数据吧。
        for i, url in enumerate(get_urls()):
            page_num = range(page_start, page_end + 1)[i]
            html_path = os.path.join(dir_path, f"search-pt-{page_num}.html")

            html = self.get_html_from_respose(url, html_path)
            # html = read_html_from_file(html_path)  # test by local html file

            # get specific data
            self.get_spot_with_shop_info(html, spot, dir_path)

        print("Finish the task of [Search Spot]")
        logger.info("Finish the task of [Search Spot].")

        spot.insert(self.mongo)  # spot 的任务完成了。

        # other operations， 目前看来就是直接联动，启动 shop 的查询。
        for shop in spot.shop_list_class:  # 直接遍历 Shop 类
            # check dir: base on the shop info
            sub_dir_path = os.path.join(dir_path, f"{shop.shop_id}-{shop.shop_name}")
            if not os.path.exists(sub_dir_path):
                # continue  # test
                os.makedirs(sub_dir_path)
            # 启动 shop 主页爬取
            self.crawl_shop_info(sub_dir_path, shop)
            # 然后爬取 review_all，先补充 shop，然后获取 review
            self.crawl_comments(sub_dir_path, shop)

        print("FINISH ALL TASK!")

    def get_spot_with_shop_info(self, html, spot, dir_path):
        """
        存储 spot 结构
        从 search 路由获取初步的 shop 信息。
        :param dir_path:
        :param spot:
        :param html:
        :return:
        """

        def get_tags(tag_div_inside):
            tag_list = []
            tags_a = tag_div_inside.find_all('a')
            for tag in tags_a:
                tag_list.append(tag.find('span').text)
            if len(tag_list) < 2:
                tag_list.append(None)
            return tag_list

        def get_recommend(recommend_div_inside):
            recommend_list = []
            recommend_a = recommend_div_inside.find_all('a')
            # todo <a> 中的 href 可以导航到目标菜品的详细介绍，之后可以考虑。
            for recommend in recommend_a:
                recommend_list.append(recommend.text)
            return recommend_list

        # 店铺首图的存储路径
        pic_dir_path = os.path.join(dir_path, ".shop-pic")
        if not os.path.exists(pic_dir_path):
            os.makedirs(pic_dir_path)
        # core
        bs = BeautifulSoup(html, "html.parser")
        # 获取 shop 的 li 节点
        shop_list_div = bs.find('div', class_="shop-all-list")
        ul = shop_list_div.find('ul')
        shops_li = ul.find_all('li', recursive=False)

        for index, shop_li in enumerate(shops_li):
            # from Picture module
            pic_div = shop_li.find('div', class_="pic")
            # 查找包含 data-shopid 的 a 标签
            a_tag = pic_div.find('a', attrs={'data-shopid': True})
            shop_id = a_tag['data-shopid'] if a_tag else None

            # build new shop && add shop_id to spot
            shop = Shop(shop_id)

            # 查找 img 标签并获取 src 属性
            img_tag = a_tag.find('img') if a_tag else None
            img_src = img_tag['src'] if img_tag else None

            # from Txt model
            txt_div = shop_li.find('div', class_='txt')
            tit_div = txt_div.find('div', class_='tit')
            h4_tag = tit_div.find('h4')
            shop.shop_name = h4_tag.text if h4_tag else None

            # 下载单张图片
            save_path = os.path.join(pic_dir_path, f'{shop.shop_id}-{shop.shop_name}.jpg')  # 从机器处理方便上，还是将 id 前置会更好。
            self.download_pic_single(img_src, save_path)

            tag_div = txt_div.find('div', class_='tag-addr')
            shop.type, shop.address['brief'] = get_tags(tag_div)

            recommend_div = txt_div.find('div', class_='recommend')
            shop.cuisine['main'] = get_recommend(recommend_div)

            # 并加入到 spot 中
            spot.add_shop_list(shop)
