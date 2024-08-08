import re
import gzip
import requests
import random
import urllib
import urllib.request
import time
import json

class Crawl_proxy:
    def __init__(self):
        self.url1 = "https://www.kuaidaili.com/free/inha/"
        self.url2 = "https://www.kuaidaili.com/free/intr/"
        self.urls = [self.url1, self.url2]

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
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }

    def request(self, url, data=None, headers=None, method="GET"):
        print("Request url:", url)
        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)  # 实际上爬取 html 的操作只是一个 GET 的接口。
        response = self.urlopen(request)
        return response

    def urlopen(self, url):
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            raise Exception(e)
        return response

    # def write_txt(self, path, content):
    #     with open(path, "w", encoding="utf-8") as f:
    #         f.write(content)
    #
    # def read_txt(self, path):
    #     with open(path, "r", encoding="utf-8") as f:
    #         content = f.read()
    #     return content

    def get_html_from_url(self, url, save_path=None):
        self.headers["User-Agent"] = random.choice(self.user_agent)
        resp = self.request(url=url, headers=self.headers)
        if resp.code == 200:
            print(f"{url} 成功响应。")
        else:
            print(f"{url} 响应失败！")

        html = resp.read()
        html = gzip.decompress(html).decode("utf-8")
        if save_path is not None:
            self.write_txt(save_path, html)
        return html

    def get_porxy(self):
        ip_port_list = []
        for url in self.urls:
            time.sleep(1)
            html = self.get_html_from_url(url)

            # 正则表达式来提取 fpsList 的内容
            pattern = r'const fpsList = (\[.*?\]);'
            # 搜索匹配的部分
            match = re.search(pattern, html, re.DOTALL)

            if match:
                fps_list = match.group(1)
                # print(fps_list)
            else:
                print("没有找到 fpsList")

            fps_list_json = json.loads(fps_list)
            # print(fps_list_json)

            for fps in fps_list_json:
                ip_port_list.append(["http", f"{fps['ip']}:{fps['port']}"])

        return ip_port_list


if __name__ == "__main__":
    crawler = Crawl_proxy()
    ip_port_list = crawler.get_porxy()
    print(ip_port_list)