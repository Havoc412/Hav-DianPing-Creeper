import urllib
import urllib.request
import gzip
import os
import re
import time
import requests
import logging
import random
import webbrowser
from bs4 import BeautifulSoup

from crawler.utils.yaml_utils import load_yaml
from crawler.utils.encode import encode_chinese
from crawler.utils.html import (
    read_html_from_file,
    get_rank_text,
    get_shop_info,
)
from crawler.utils.timer_watching import TimerWatch

# 存储用数据库基本配置
from crawler.MongoDB.Mongo import Mongo
from crawler.models.comment import Comment
from crawler.models.spot import Spot
from crawler.models.shop import Shop
from crawler.models.city import City
from crawler.models.admin import Admin


logger = logging.getLogger(__name__)


class Crawl:
    # def __init__(self):
        # # 隧道域名:端口号
        # tunnel = "q547.kdltpspro.com:15818"
        #
        # # 用户名密码方式
        # username = "t12192669709642"
        # password = "u2t9srwx"
        # self.proxies = {
        #     "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        #     "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
        # }
        # # 使用隧道域名发送请求
        # proxy_support = urllib.request.ProxyHandler(self.proxies)
        # opener = urllib.request.build_opener(proxy_support)
        # urllib.request.install_opener(opener)   # 注意此处是全局设置代理，如用这种写法进程内之后的所有urllib请求都会使用代理

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
    time.sleep(random.uniform(delay, delay+3))


class application:
    def __init__(self, config_file, application):
        self.crawler = Crawl()
        self.config = load_yaml(config_file)[application]
        # url path
        self.base_url_search_city = self.config["search_city"]["base_url"]
        self.base_url_search_spot = self.config["search_spot"]["base_url"]  # new
        self.base_url_shop = self.config["base_url_shop"]
        self.base_url_comment = self.config["comment"]["base_url"]
        # 爬取的图片保存地址
        self.save_dir = self.config["save_dir"]
        os.makedirs(self.save_dir, exist_ok=True)
        # 爬取相关的参数
        self.crawl_delay = float(self.config["crawl_delay"])
        self.crawl_lax_delay = float(self.config["crawl_lax_delay"])
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
        self.mongo = Mongo(config_file=config_file, application="MongoDB")  # None
        # func
        self.comment_num = 0
        # timer
        self.timer = TimerWatch()

    def filter_proxy(self):
        """检查IP代理池是否可用"""
        self.proxy_list = [_ for _ in self.proxy_list if proxy_is_availabel(_)]

    def check_login(self, html, url):  # 因为 logger， 就先留在这个 py 了。
        """检查网页是否登录"""
        if re.search("登录失败", html):
            logger.info("网页未登录账号，请更新Cookie后重试！")
            raise Exception("网页未登录账号，请更新Cookie后重试！")
        elif re.search("身份核实", html):
            logger.info("需要进行身份核实，请打开指定网页。")
            # 打开指定网页
            webbrowser.open(url)  # 替换为实际的验证网址
            logger.info("请在网页上进行身份核实。")
            cookie = input("请输入新的 Cookies:\n")  # 等待用户输入以挂起程序
            logger.info("身份核实完成，程序继续运行。")
            if len(cookie) > 20:  # 大致判断是否有效
                self.headers['Cookie'] = cookie
            return False
        return True

    """
    获取 html 数据的两种方式; from local is in html.py
    """
    def get_html_from_response(self, url, save_path, retry_count=3, delay_type=True):
        """
        从网络上获取目标路径。
        :param retry_count: 最大重试次数，通过递归实现。
        :param url:
        :param save_path: 由外部确认保存的位置。
        :return:
        """
        def remove_suffix(input_string):
            # 检查是否以 'p1' 或 '/p1' 结尾
            if input_string.endswith('p1'):
                return input_string[:-2]  # 删除 'p1'
            elif input_string.endswith('/p1'):
                return input_string[:-3]  # 删除 '/p1'
            return input_string  # 如果没有以这两者结尾，则返回原字符串

        if delay_type is True:  # 比较严格
            sleep_random(self.crawl_delay)
        else:  # 非严格
            sleep_random(self.crawl_lax_delay)

        # url 预处理
        url = remove_suffix(url)

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
        if not self.check_login(html, url):
            if retry_count > 0:
                print(f">>> 登录检查失败，正在重试... 剩余重试次数: {retry_count}")
                logger.info(f">>> 登录检查失败，正在重试... 剩余重试次数: {retry_count}")
                return self.get_html_from_response(url, save_path, retry_count - 1, False)  # 递归重试
            else:
                print(f">>> 登录检查失败，已达到最大重试次数，停止尝试。")
                logger.info(f">>> 登录检查失败，已达到最大重试次数，停止尝试。")
                resp.close()
                return None  # 如果重试次数用尽，返回 None
        if save_path is not None:
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
        page_end = self.config["comment"]["page_end"]
        cuisine = set()

        # 获取目标 urls
        def get_urls():
            # return [self.base_url_comment.format(shop.shop_id, _) for _ in range(page_start, page_end+1)]
            return [self.base_url_comment.format(shop.shop_id)]

        # 一页页遍历
        self.comment_num = 0
        for i, url in enumerate(get_urls()):
            page_num = range(page_start, page_end+1)[i]
            html_path = os.path.join(dir_path, f"comment-page-{page_num}.html")

            if os.path.exists(html_path):
                html = read_html_from_file(html_path)
            else:
                html = self.get_html_from_response(url, html_path)

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
        print(f">>> 所有 comment && picture 已完成下载，请查看:    {dir_path}")
        logger.info(f">>> 所有 comment && picture 已完成下载，请查看:    {dir_path}")

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

        reviews_div = bs.find('div', class_="reviews-items")
        # 只获取子节点
        if reviews_div is None:
            return recommend_cuisine
        ul = reviews_div.find('ul')
        comments_li = ul.find_all('li', recursive=False)

        for index, comment_li in enumerate(comments_li):
            self.comment_num += 1  # 完整的计数
            # logger
            if index % 7 == 0:
                self.timer.start_timer()  # 不断重启计时器
                print("Getting comments, now {", self.comment_num, "} in this page.")

            comment = Comment(shop_id=shop_id, user_id=self.comment_num)
            # rank * 3
            rank_items = comment_li.find_all('span', class_="item")
            comment.rank['taste'], comment.rank['environment'], comment.rank['service'] = get_rank_text(rank_items)
            # words
            words_div = comment_li.find('div', class_="review-words")
            comment.words = words_div.text.strip()
            # pic  取消评论图片下载。
            # reviews_pic = comment_li.find('div', class_="review-pictures")
            # if reviews_pic is not None:
            #     comment.pic_num = self.download_pic_each_comment(reviews_pic, pic_dir, self.comment_num, self.proxy_list)
            # time
            time_span = comment_li.find('span', class_="time")
            comment.time = time_span.text.strip()

            self.mongo.insert("comment", comment.to_json())

            # get the cuisine for shop
            recommend_div = comment_li.find('div', class_="review-recommend")
            if recommend_div is not None:
                for cuisine in recommend_div.find_all('a'):
                    recommend_cuisine.add(cuisine.text)
        self.timer.stop_timer()
        return recommend_cuisine

    def download_pic_each_comment(self, pic_div, pic_dir, user_id, proxy_list):
        """"
        这是我后来写的单对评论的图片获取。
        """
        def is_img_and_has_data_big(tag):
            return tag.has_attr("data-big")  # 通过 tag 来获取指定元素，然后通过 IP 代理来获取图片。

        items = pic_div.find_all(is_img_and_has_data_big)
        for i, item in enumerate(items):
            # 增加设定，获取单用户前三张
            if i > 3:
                break

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
            try:
                urllib.request.urlretrieve(img_link, saveimg)  # 下载链接内容
            except urllib.error.ContentTooShortError:
                print(f"# 下载不完整，跳过: {img_link}")
                # return None  # 或者返回一个标识符，表示下载失败
            except Exception as e:
                print(f"# 下载时发生错误: {e}")

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
        try:
            urllib.request.urlretrieve(img_link, save_path)  # 下载链接内容
        except:
            print("#下载错误:", img_link, save_path)
            logger.info("# Downloading failed:{} - {}".format(img_link, save_path))

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
        if os.path.exists(html_path):
            html = read_html_from_file(html_path)
        else:
            html = self.get_html_from_response(url, html_path)
        # get the core info
        bs = BeautifulSoup(html, "html.parser")
        business_hours_p = bs.find('p', class_='info-indent')  # 只获取第一个，也就是目标的营业时间
        item_span = business_hours_p.find('span', class_="item")
        if item_span:
            shop.business_hours = item_span.text.strip()

        # INFO 如果评论数 小于 15， 那就直接过滤此店。
        comment_num_span = bs.find('span', id='reviewCount')

        match = re.search(r'\d+', comment_num_span.text.strip())
        if match:
            number = match.group()  # 获取匹配的数字
        else:
            number = 0
            # print("未找到数字")
        if int(number) < 15:
            print("评论过少，此店放弃。")
            logger.info("! 评论过少，此店放弃。")
            return False
        else:
            return True


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
    def crawl_search_food(self, city_EN=None, dir_path=None, spot_id=None, spot_name=None,
                          need_pass=False, pass_shop_target=None, last_spot_id=None):
        """
        作为 第二端口 ，获取店铺基本信息（部分），收集 shop_id 用于访问详情 && 评论。
        :param need_pass:
        :param last_spot_id: 用于判断 spot 状态
        :param pass_shop_target: 任务回复中，用于判断 shop 跳过数量的 id。

        :param city_EN:
        :param dir_path:
        :param spot_id:
        :param spot_name:
        :return:
        """
        if need_pass is True:
            print("执行跳过逻辑")
        else:
            print("无需跳过状态")

        if need_pass and pass_shop_target is None:
            raise Exception("无法执行 shop 跳过逻辑，缺失参数")

        # get && save html
        dir_path = os.path.join(dir_path, f"{spot_id}-{spot_name}")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 遍历 search keyword
        page_start = self.config["search_spot"]["page_start"]
        page_end = self.config["search_spot"]["page_end"]
        spot = Spot(spot_id=spot_id, spot_name=spot_name, city=city_EN)
        spot.shop_list = []  # BUG： 强制清空。

        def get_urls():
            return [self.base_url_search_spot.format(city_EN, spot_id, _) for _ in range(page_start, page_end + 1)]

        for i, url in enumerate(get_urls()):
            page_num = range(page_start, page_end + 1)[i]
            html_path = os.path.join(dir_path, f"search-pt-{page_num}.html")

            if os.path.exists(html_path):
                html = read_html_from_file(html_path)  # test by local html file
            else:
                html = self.get_html_from_response(url, html_path, delay_type=False)

            # get specific data
            self.get_spot_with_shop_info(html, spot, dir_path)

        # logger
        print("Finish the task of [Search Spot]")
        logger.info("!!! Finish the task of [Search Spot] !!!")

        # if need_pass is False:
        spot.insert(self.mongo)  # spot 的任务完成了。  # 还是需要再次上传更新。

        # other operations， 目前看来就是直接联动，启动 shop 的查询。
        if need_pass is True:
            if pass_shop_target in spot.shop_list:
                index = spot.shop_list.index(pass_shop_target)
                # delete next
                delete_shop_id = spot.shop_list[index+1]['shop_id']
                query = {'shop_id': delete_shop_id}
                self.mongo.delete_data('comment', query)
                index += 1
            else:
                raise Exception("Not found pass_shop_target, recover failed!!")
        else:
            index = 0

        shop_len = len(spot.shop_list_class)
        for idx, shop in enumerate(spot.shop_list_class[index:]):  # 直接遍历 Shop 类
            # check dir: base on the shop info
            sub_dir_path = os.path.join(dir_path, f"{shop.shop_id}-{shop.shop_name.replace('/', '-')}")
            if not os.path.exists(sub_dir_path):
                os.makedirs(sub_dir_path)
            # 一定数量之后访问一次父页面  # todo 难道还需要再向上一层？  # 暂时弃用
            if idx % 7 == 0:
                print(f"-- shop status: {idx+index}/{shop_len} --")
                # self.get_html_from_response(get_urls()[int((idx+index)/15)], None, delay_type=False)
            # 启动 shop 主页爬取
            comment_check = self.crawl_shop_info(sub_dir_path, shop)
            # 然后爬取 review_all，先补充 shop，然后获取 review
            if comment_check:
                self.crawl_comments(sub_dir_path, shop)

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
        if shop_list_div is None:
            return
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
            h4_tag = tit_div.find('a')
            shop.shop_name = h4_tag.get('title').replace("/", "-") if h4_tag else None

            # 下载单张图片
            save_path = os.path.join(pic_dir_path, f'{shop.shop_id}-{shop.shop_name}.jpg')  # 从机器处理方便上，还是将 id 前置会更好。
            if not os.path.exists(save_path):
                self.download_pic_single(img_src, save_path)

            tag_div = txt_div.find('div', class_='tag-addr')
            shop.type, shop.address['brief'] = get_tags(tag_div)

            recommend_div = txt_div.find('div', class_='recommend')
            if recommend_div:
                shop.cuisine['main'] = get_recommend(recommend_div)

            # 并加入到 spot 中
            spot.add_shop_list(shop)

    def crawl_search_city(self):
        """
        第一入口
        :return:
        """
        # set city Model
        city = City(self.city_name)  # set by __main__.py
        dir_path = os.path.join(self.save_dir, self.city_name)
        os.makedirs(dir_path, exist_ok=True)
        # request the search page
        url = self.base_url_search_city.format(city.city_EN)
        html_path = os.path.join(dir_path, "search-city.html")

        if os.path.exists(html_path):
            html = read_html_from_file(html_path)
        else:
            html = self.get_html_from_response(url, html_path, delay_type=False)

        admin_dir_path = os.path.join(dir_path, ".admin-html")
        os.makedirs(admin_dir_path, exist_ok=True)
        self.get_admin_ids(html, admin_dir_path, city)
        # load Model city
        city.insert(self.mongo)

        for spot in city.get_spot_list():  # core task
            print("---", spot['spot_id'], spot['spot_name'], "---")
            logger.info(f"---{spot['spot_id'], spot['spot_name']}---")
            # 执行后续操作
            self.crawl_search_food(city.city_EN, dir_path, spot['spot_id'], spot['spot_name'])

        print("todo next!")

    def get_admin_ids(self, html, dir_path, city):
        """
        获取 city 对应行政区 的 id
        :param html:
        :param dir_path:
        :param city:
        :return:
        """
        def get_spot_ids(html_inside, admin_inside):
            bs_inside = BeautifulSoup(html_inside, "html.parser")
            spot_id_div = bs_inside.find('div', id="region-nav-sub")

            items_inside = spot_id_div.find_all('a')
            items_inside = items_inside[1:]  # 使用切片从第二个元素开始

            for item_inside in items_inside:
                spot_id = item_inside.get('data-cat-id')
                spot_name = item_inside.find('span').text.strip().replace("/", "-")  # todo 没有替换成功？

                admin_inside.add_spot(spot_id, spot_name)

        bs = BeautifulSoup(html, "html.parser")

        admin_id_div = bs.find('div', id="region-nav")
        items = admin_id_div.find_all('a')

        for item in items:
            # 提取 data-cat-id 和 data-click-title 属性
            data_cat_id = item.get('data-cat-id')
            data_click_title = item.get('data-click-title')
            # create Model - admin
            admin = Admin(data_cat_id, data_click_title)
            # 随后就获取 spot_list
            url = item.get('href')  # admin 级别的 search
            html_path = os.path.join(dir_path, f"admin-{data_cat_id}-{data_click_title}.html")
            if os.path.exists(html_path):
                sub_html = read_html_from_file(html_path)
            else:
                sub_html = self.get_html_from_response(url, html_path, delay_type=False)
            # 获取 admin 层次下的 spot_id
            get_spot_ids(sub_html, admin)
            # load
            admin.insert(self.mongo)
            city.add_admin(admin)

    def back_task_from_db(self):
        dir_path = os.path.join(self.save_dir, self.city_name)

        # 恢复 city 信息
        city_data = self.mongo.find_last_data('city')
        city = City.from_db(city_data)
        # print(city.to_json())
        # 恢复 admin，需要获取匹配的全部
        admin_list = self.mongo.find_admin_by_city(city.admin_list)
        for admin in admin_list:
            city.extend_spot(admin["spot_list"])
        # 获取 最后一个 spot
        spot_data = self.mongo.find_last_data('spot')
        spot_target = {
            'spot_id': spot_data['spot_id'],
            'spot_name': spot_data['spot_name'].replace('-', '/')  # todo remove 下一个城市的时候
        }
        # 获取最后一个 shop
        shop_data = self.mongo.find_last_data('shop')
        shop_target = {
            'shop_id': shop_data['shop_id'],
            'shop_name': shop_data['shop_name'],
        }
        # 是当前 spot 的最后一个，所以直接从下一个 spot 开始
        print("pass info", spot_target, shop_target, city.city_EN)
        if spot_target in city.get_spot_list():
            index = city.spot_list.index(spot_target)
            # 依靠 last_check 来决定 跳过参数是否有效。
            last_check = (spot_data['shop_list'][-1]['shop_id'] != shop_target['shop_id'])
            # 从后续开始遍历 # 之后需要判断 shop 的后续，不断嵌套
            for spot in city.spot_list[index+int(not last_check):]:
                print("---", spot['spot_id'], spot['spot_name'], "---")
                logger.info(f"---{spot['spot_id'], spot['spot_name']}---")
                # todo 临时方案：解决恢复逻辑中 spot 名中的路径符号。 同上。
                spot['spot_name'] = spot['spot_name'].replace('/', '-')
                # 执行后续操作
                self.crawl_search_food(city.city_EN, dir_path, spot['spot_id'], spot['spot_name'],
                                       need_pass=last_check, pass_shop_target=shop_target,
                                       last_spot_id=spot_target['spot_id'])
                last_check = False  # 之后就不需要跳过了
        else:
            print("back find fail ?!")
            raise Exception("back find fail?!")

    def crawl(self):
        """
        是否直接启动，或从数据库中读取最后状态，然后恢复任务。
        :return:
        """
        if self.BACK_TASK is False:
            self.crawl_search_city()  # 一般的其中入口
        else:
            """
            最核心的部分，都是在对 spot - shop 的遍历中。
            """
            self.back_task_from_db()


if __name__ == '__main__':
    from Crawler.crawler.utils.yaml_utils import load_yaml
    from Crawler.crawler.utils.encode import encode_chinese
    from Crawler.crawler.utils.html import (
        read_html_from_file,
        get_rank_text,
        get_shop_info,
    )
    from Crawler.crawler.MongoDB.Mongo import Mongo
    from Crawler.crawler.models.comment import Comment
    from Crawler.crawler.models.spot import Spot
    from Crawler.crawler.models.shop import Shop
    from Crawler.crawler.models.city import City
    from Crawler.crawler.models.admin import Admin

    application = application(config_file="../config/config.yaml", application="dazhongdianping")

    application.back_task_from_db()
