from bs4 import BeautifulSoup

html_doc = "<html><head><title><a>Sample Page</a></title></head><body></body></html>"
soup = BeautifulSoup(html_doc, 'html.parser')

title_tag = soup.find('title')  # 获取第一个<title>标签
print(title_tag.text)

