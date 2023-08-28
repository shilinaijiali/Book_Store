import time

from alipay import Alipay          # 导入支付包相关的类
from bookstore import settings
from alipay.utils import AliPayConfig
from rest_framework import serializers
from django.db import transaction

from bookstore.settings import ALIPAY_APPID, app_private_key_string, alipay_public_key_string
from apps.goods.models import Goods
from apps.goods.serializers import GoodsSerializer
from apps.trade.models import ShoppingCart, OrderInfo, OrderGoods


class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()

    class Meta:
        model = ShoppingCart
        fields = '__all__'


class ShopCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    nums = serializers.IntegerField(required=True, label='数量', min_value=1,
                                    error_messages={
                                        "min_value": "商品的数量不能小于1",
                                        "required": "请选择需要购买的数量"
                                    })
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    def create(self, validated_data):
        user = self.context.get('request').user   # 获取请求用户
        nums = validated_data.get('nums')
        goods = validated_data.get('goods')
        exist = ShoppingCart.objects.filter(user=user, goods=goods)
        if exist:
            ins = exist.first()
            ins.nums += nums    # 如果商品已存在于购物车，那么商品数量就再已有的基础上再加上前端需要再添加的数量
            ins.save()
        else:
            ins = ShoppingCart.objects.create(**validated_data)
        return ins

    def update(self, instance, validated_data):
        instance.nums = validated_data.get('nums')
        instance.save()
        return instance


class OrderGoodsOneSerializer(serializers.ModelSerializer):
    """用于订单已存在的情况,一个订单只存在一件商品的情况"""
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderCreateSerializer(serializers.ModelSerializer):
    """用于订单创建，即订单不存在的情况"""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    pay_status = serializers.CharField(label='订单状态', read_only=True)
    order_sn = serializers.CharField(label='订单号', read_only=True)
    trade_no = serializers.CharField(label='交易号', read_only=True)
    create_time = serializers.DateTimeField(label='订单创建时间', read_only=True)
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        alipay = Alipay(
            appid=ALIPAY_APPID,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',   # 指定加密方式，一般为RSA2或RSA
            config=AliPayConfig(timeout=15),  # 选择性进行添加，表示请求等待时间为15秒，超时的话会返回错误信息
        )
        order_string = alipay.api_alipay_trade_wap_pay(
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
            subject='二手书商城订单:%s' % obj.order_sn,
            return_url='http://192.168.1.183:8000/alipay/return/',
            notify_url='https://example.com/notify',
        )
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return alipay_url

    # 订单号由时间加上用户id加上一个随机数构成，注意是字符串格式进行拼接
    def generic_order_sn(self):
        # 生成订单编号的方法
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context['request'].user.id,
                                                       ranstr=random_ins.randint(10,99))
        return order_sn

    def validate(self, attrs):
        req_user = self.context['request'].user
        shoppingcart = req_user.shoppingcart_set.all()  # 取出请求用户的购物车商品信息
        with transaction.atomic():
            save_id = transaction.savepoint()
            for obj_good in shoppingcart:
                while True:
                    origin_nums = obj_good.goods.goods_num      # 原来商品的数量，库存
                    new_nums = origin_nums - obj_good.nums      # 减去购物车中要购买的数量
                    if obj_good.nums > origin_nums:
                        # 如果购物车中的商品数量大于了库存，返回库存不足的信息
                        raise serializers.ValidationError('商品库存不足')
                    result = Goods.objects.filter(id=obj_good.goods.id, goods_num=origin_nums).update(goods_num=new_nums)
                    if result == 0:
                        transaction.get_rollback(save_id)
                        continue
                    break
            transaction.savepoint_commit(save_id)
        attrs['order_sn'] = self.generic_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderGoodsSerializer(serializers.ModelSerializer):
    """用于订单已存在的情况，一个订单存在多个商品的情况"""
    goods = OrderGoodsOneSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'