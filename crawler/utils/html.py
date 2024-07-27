# 专门用于处理 HTML
import re
from bs4 import BeautifulSoup


def read_html_from_file(file_path):
    """读取本地 HTML 文件内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


def get_rank_text(rank_items):
    """
    获取 rank-items 中的具体评分
    :param rank_items:
    :return: len = 3 的浮点数组
    """
    rank = []
    for index in range(min(3, len(rank_items))):  # 最多记录三点。
        # 正则表达式匹配数字，可能包括小数点
        numbers = re.findall(r'\d+\.\d+', rank_items[index].text)
        if numbers:  # 确保找到了数字
            # print(f"Extracted number: {numbers[0]}")
            rank.append(numbers[0])
        else:
            print("No number found:", rank_items[index].text)

    while len(rank) < 3:  # maybe bug
        rank.append(0.0)
    return rank


def get_shop_info(shop, html):
    """
    将 review_all 上方的基本信写入 shop 类。
    :param shop: Shop 类
    :param html:
    :return:
    """

    def get_num(text):
        match = re.search(r'\d+', text)
        if match:
            number = match.group()
            return number
        else:
            print(f"没有找到数字部分， origin:{text}")
            return 0

    def get_address(text):
        # 使用正则表达式提取地址
        match = re.search(r'地址:\xa0(.*)', text)

        # 获取匹配的内容
        if match:
            address = match.group(1).strip()
        else:
            address = ''
        return address

    def get_phone_number_list(text):
        # 使用正则表达式提取电话号码
        phone_numbers = text.split('\xa0')  # check ‘ ’ or '&nbsp'; END: it's \xa0 ...
        return phone_numbers[1:]

    bs = BeautifulSoup(html, "html.parser")
    shop_info_div = bs.find('div', class_="review-shop-wrap")
    # load info
    shop.comment_num = get_num(shop_info_div.find('span', class_="reviews").text)
    shop.per_cost = get_num(shop_info_div.find('span', class_="price").text)

    shop.rank['overall'] = shop_info_div.find('div', class_="star_score").text
    rank_items = shop_info_div.find_all('span', class_="item")
    shop.rank['taste'], shop.rank['environment'], shop.rank['service'] = get_rank_text(rank_items)

    shop.address['detail'] = get_address(shop_info_div.find('div', class_="address-info").text.strip())

    phone_info_div = shop_info_div.find('div', class_="phone-info")
    if phone_info_div:
        shop.phone_number = get_phone_number_list(phone_info_div.text.strip())
    # 至此 shop 基本就获取完毕了，只差 cuisine-all
