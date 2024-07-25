from pypinyin import lazy_pinyin


def get_pinyin(text):
    py = lazy_pinyin(text)
    return "".join(map(str, py))


if __name__ == '__main__':
    # 示例中文字符串
    chinese_text = "武汉"

    # 使用 lazy_pinyin 获取拼音
    pinyin_list = lazy_pinyin(chinese_text)
    print("拼音（不带声调）：", pinyin_list)
    print(get_pinyin(chinese_text))
    #
    # # 使用 pinyin 获取拼音（带声调）
    # pinyin_with_tone = pinyin(chinese_text, style=Style.TONE3)  # 使用数字表示声调
    # print("拼音（带声调）：", pinyin_with_tone)
    #
    # # 如果需要将拼音转换为字符串
    # pinyin_string = ' '.join(lazy_pinyin(chinese_text))
    # print("拼音字符串（不带声调）：", pinyin_string)
