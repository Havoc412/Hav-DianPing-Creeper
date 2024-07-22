from bs4 import BeautifulSoup

from Crawler.crawler.models.comment import Comment

html_doc = """
<div class="review-words">
    好好吃哦，味道都做得很好，对于广东人的我来说，辣度能接受的，菜都不咸，很新鲜的食材，汤更好喝，莲藕粉粉的，价格也实惠，真的值得来尝一尝的，环境很干净。
</div>
"""

soup = BeautifulSoup(html_doc, 'html.parser')

# 查找包含评论的 div
words_div = soup.find('div', class_='review-words')

# 将获取到的文本内容赋值给 Comment 类实例的 words 属性
comment = Comment("123", 123)
comment.words = words_div.text.strip()  # 使用 strip() 去除可能的前后空白

print("Comment words:", comment.words)
