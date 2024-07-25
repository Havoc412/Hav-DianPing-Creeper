import requests

# 指定要请求的 URL
url = 'https://www.dianping.com/shop/H4b4zwVjgCY45iQh'  # 替换为你要请求的页面

# 发送 GET 请求
response = requests.get(url)

print(response)
# 获取 cookies
cookies = response.cookies

# 打印获取的 cookies
for cookie in cookies:
    print(f'Name: {cookie.name}, Value: {cookie.value}')