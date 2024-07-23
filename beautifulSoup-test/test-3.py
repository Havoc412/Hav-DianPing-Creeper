from bs4 import BeautifulSoup
import re

# 示例 HTML
html_doc = """
<span class="item">
    口味：5.0
</span>
<span class="item">
    环境：5.0
</span>
<span class="item">
    服务：5.0
</span>
"""

soup = BeautifulSoup(html_doc, 'html.parser')
items = soup.find_all('span', class_='item')

# 使用正则表达式提取数字
for item in items:
    # 正则表达式匹配数字，可能包括小数点
    numbers = re.findall(r'\d+\.\d+', item.text)
    if numbers:  # 确保找到了数字
        print(f"Extracted number: {numbers[0]}")
    else:
        print("No number found")