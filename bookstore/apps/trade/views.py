from datetime import datetime

from alipay import Alipay
# , AliPayConfig)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from bookstore.settings import ALIPAY_APPID, app_private_key_string, alipay_public_key_string
from apps.trade.models import ShoppingCart, OrderInfo, OrderGoods
from apps.trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderGoodsSerializer, OrderCreateSerializer


class ShoppingCartViewSet(ModelViewSet):
    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ShopCartSerializer
    lookup_field = 'goods_id'

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class ShoppingCartDelView(APIView):
    def post(self, request):
        user = request.user
        shoppingcart = ShoppingCart.objects.filter(user=user).delete()
        return Response(status=204)


class OrderViewSet(ModelViewSet):
    """
    订单部分：
        1. list获取
        2. delete删除
        3. create增加
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = None

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    # 除了以判断行为之外的行为
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderGoodsSerializer
        return OrderCreateSerializer

    def perform_create(self, serializer):
        order = serializer.save()  # 保存并获取到保存的订单模型类对象
        shoppingcart = ShoppingCart.objects.filter(user=self.request.user)
        for shopcart in shoppingcart:
            order_goods = OrderGoods()
            order_goods.goods = shopcart.goods
            order_goods.goods_num = shopcart.nums
            order_goods.order = order
            # 库存量 = 库存量 - 购物车中的商品数量
            # shopcart.goods.goods_num -= shopcart.nums
            # 销售量 = 销售量 + 购物车中的商品数量
            shopcart.goods.sold_num += shopcart.nums
            shopcart.goods.save()
            order_goods.save()
            shopcart.delete()
        return order


from django.shortcuts import redirect

class AlipayView(APIView):
    def get(self, request):
        """处理支付宝的返回结果，验证支付是否成功并修改订单的支付状态"""
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value
        sign = processed_dict.pop("sign", None)     # 取出钥匙，在之后进行交易号验证的时候使用
        alipay = Alipay(
            appid=ALIPAY_APPID,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',   # 指定加密方式，一般为RSA2或RSA
            # config=AliPayConfig(timeout=15),  # 选择性进行添加，表示请求等待时间为15秒，超时的话会返回错误信息
        )
        verify_result = alipay.verify(processed_dict, sign)
        # verify中传入验证的订单信息以及钥匙
        # verify中传入两个参数，一个为订单信息，一个为验证的钥匙
        if verify_result:
            # 支付成功，执行以下代码
            order_sn = processed_dict.get('out_trade_no', None)     # 获取订单编号
            trade_no = processed_dict.get('trade_no', None)   # 获取交易号
            existed_order = OrderInfo.objects.filter(order_sn=order_sn).first()     # 取出订单对象
            # 修改订单的对应数据信息
            existed_order.trade_no = trade_no
            existed_order.pay_status = 'TRADE_SUCCESS'
            existed_order.pay_time = datetime.now()
            existed_order.save()
            response = redirect('http://192.168.1.183')
            return response
        else:
            # 支付未成功，执行else中的代码
            order_sn = processed_dict.get('out_trade_no', None)  # 获取订单编号
            trade_no = processed_dict.get('trade_no', None)  # 获取交易号
            existed_order = OrderInfo.objects.filter(order_sn=order_sn).first()  # 取出订单对象
            # 修改订单的对应数据信息
            existed_order.trade_no = trade_no
            existed_order.pay_status = 'TRADE_CLOSED'
            existed_order.pay_time = datetime.now()
            existed_order.save()
            response = redirect('http://192.168.1.183')
            return response

