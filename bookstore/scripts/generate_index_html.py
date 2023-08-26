import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../apps')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'bookstore.settings'

# 初始化django配置,相当于此处是一个小的django的依赖环境了
import django
django.setup()
from apps.goods.cron import generate_static_index
if __name__ == '__main__':
    generate_static_index()
