from django_filters import rest_framework as filters
from django.db.models import Q

from apps.goods.models import Goods


class GoodsFilter(filters.FilterSet):
    pricemin = filters.NumberFilter(field_name='shop_price', lookup_expr='gte')
    pricemax = filters.NumberFilter(field_name='shop_price', lookup_expr='lte')
    top_category = filters.NumberFilter(field_name='category', method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        """在过滤类中定义过滤方法时，一定要在方法名最后连接上_filter"""
        # 不管点击的是哪一级目录，都返回父级(一级)分类的内容
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|
                               Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['pricemin', 'pricemax', 'name', 'is_new', 'is_hot']
