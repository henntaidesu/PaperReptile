from lxml import etree

# 读取HTML文件内容
file_path = r"C:\Users\Makuro\Desktop\Lens - Elastic.html"
with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# 创建Element对象
root = etree.HTML(html_content)

# 使用xpath获取目标文本数据
target_texts = root.xpath('//div[@class="echLegendList"]//text()')

# 输出结果
for text in target_texts:
    print(text.strip())
