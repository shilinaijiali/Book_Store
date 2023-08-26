from django.contrib import admin
from apps.goods.models import GoodsCategory, Goods

# Register your models here.
admin.site.index_title = 'sixstar'
admin.site.site_title = 'sixstar'
admin.site.site_header = 'sixstar'


@admin.register(GoodsCategory)
class GoodsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'desc']


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['name', 'goods_front_image']