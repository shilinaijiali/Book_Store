import os
from django.template import loader
from goods.models import Goods


def generate_static_index():
    """生成静态化页面"""
    goods = Goods.objects.all()
    context = {'all_goods': goods}
    template = loader.get_template('index.html')     # 加载模板
    html_text = template.render(context=context)     # 渲染模板
    with open('index.html', 'w', encoding='utf-8')as f:
        f.write(html_text)


# if __name__ == '__main__':
#     generate_static_index()
