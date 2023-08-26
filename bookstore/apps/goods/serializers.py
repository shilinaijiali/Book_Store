from django.db.models import Q
from rest_framework import serializers

from apps.goods.models import GoodsCategory, Goods, GoodsImage, HotSearchWords, GoodsCategoryBrand, IndexAd, Banner


class GoodsCategorySer(serializers.ModelSerializer):
    """商品的一级类别序列化器"""
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GoodsImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = '__all__'


class GoodsSerializer(serializers.ModelSerializer):
    """返回商品列表的序列化器"""
    category = GoodsCategory()
    images = GoodsImagesSerializer(many=True)

    class Meta:
        model = Goods
        fields = '__all__'


class GoodsDetailSerializer(serializers.ModelSerializer):
    """商品详情页序列化器"""
    class Meta:
        model = Goods
        fields = '__all__'


class HotSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = '__all__'


class GoodsCategorySer3(serializers.ModelSerializer):
    """三级商品类别"""
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GoodsCategorySer2(serializers.ModelSerializer):
    """二级商品类别"""
    sub_cat = GoodsCategorySer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class IndexCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True)
    sub_cat = GoodsCategorySer2(many=True)
    goods = serializers.SerializerMethodField()     # 表示需要获取并显示的字段，需要搭配方法(get_goods)
    ad_goods = serializers.SerializerMethodField()

    def get_goods(self, obj):
        all_goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)
                                                                 |Q(category__parent_category__parent_category_id=obj.id))
        serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        # 由于序列化器之间是可以互相调用的，那么在调用的时候需要告诉下一个序列化器，当前请求的对象是谁，否则容易出现数据紊乱
        return serializer.data

    def get_ad_goods(self, obj):
        """get_xxx方法定义时需要和SerializerMethodField结合使用，二者必须同时出现"""
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            good_ins = ad_goods.first().goods
            serializer = GoodsSerializer(good_ins, context={'request': self.context['request']})
            return serializer.data

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'
