from urllib.parse import quote


def encode_chinese(txt):
    return quote(txt)


if __name__ == '__main__':
    print(encode_chinese("武汉大学"))
    print(encode_chinese("WHU"))
