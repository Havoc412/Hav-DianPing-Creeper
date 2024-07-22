from bs4 import BeautifulSoup

# 假设 html_content 是你从文件或网页中获取的 HTML 内容
html_content = """
<div class="reviews-items">
    <ul>
        <li>
            <a class="dper-photo-aside" target="_blank">Link 1</a>
            <li>
                test-photo
                <a class="dper-photo-aside" target="_blank">Link 4</a>
            </li>
            <l1>test-photo</l1>
            <l1>test-photo</l1>
        </li>
        <li><a class="dper-photo-aside" target="_blank">Link 2</a></li>
        <li><a class="dper-photo-aside" target="_blank">Link 3</a></li>
    </ul>
</div>
"""

soup = BeautifulSoup(html_content, 'html.parser')

# 查找包含评论的 div
reviews_div = soup.find('div', class_='reviews-items')

# 获取该 div 下所有的 li 标签
list_items = reviews_div.find_all('li')

print(len(list_items))
# 遍历每个 li 标签
for li in list_items:
    # 在每个 li 标签中进一步查找需要的信息，例如 <a> 标签
    a_tag = li.find('a', class_='dper-photo-aside')
    if a_tag:
        print("Link text:", a_tag.text)
        print("Link target:", a_tag['target'])