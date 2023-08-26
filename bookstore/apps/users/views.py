import random
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django_redis import get_redis_connection
from rest_framework.authentication import BaseAuthentication
from rest_framework.viewsets import ModelViewSet
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework_jwt.settings import api_settings


from apps.users.models import SmsModel, UserToken, UserProfile, UserFav
from utils.yuntongxun.ccp_sms import CCP
from apps.users.serializers import Sms_CodeSerializer, UserRegSerializer, LoginSerializer, UserFavDetailSerializer, \
    UserFavSerializer
from celery_tasks.sms_tasks import tasks

logger = logging.getLogger('django')

class SmscodeView(APIView):
    """
    云通讯：https://www.yuntongxun.com/
    """
    def get_varify_code(self):
        resource_ = '0123456789'
        res_str = ''
        for i in range(4):
            res_str += random.choice(resource_) # 生成4位数的随机验证码
        return res_str

    def post(self, request):
        data = request.data
        mobile = data.get('mobile')
        code = self.get_varify_code()
        serializer = Sms_CodeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # result = CCP().send_template_sms(mobile, [code, 5], 1)
        result = tasks.send_sms_code.delay(mobile, code)
        # 发送成功时，返回0，否则非0
        # - celery -A xxxx.main worker -l info 启动
        # - celery multi start -A xxxx.main worker -l info --logfile=./log/celery.log # 守护进程
        SmsModel.objects.create(mobile=mobile, code=code)
        redis_conn = get_redis_connection('verify_code')    # 实例化一个redis连接对象
        redis_pipeline = redis_conn.pipeline()  # 实例化一个redis的管道对象
        redis_pipeline.setex('sms_%s' % mobile, 300, code)  # 通过管道设置redis中的键值对数据
        redis_pipeline.execute()      # 通过管道提交到redis中去
        logger.info('%s验证码%s发送成功' % (mobile, code))
        return Response({'message': '%s验证码%s发送成功' % (mobile, code)}, status=201)


class My_Authtication(BaseAuthentication):
    def authenticate(self, request):
        # 验证方法的返回结果为两个对象，一个是token对象，一个是这个token他所相关的用户对象
        # print(request.META)        # 请求头信息
        try:
            token = request.META.get('HTTP_AUTHORIZATION')[7:]
            token_obj = UserToken.objects.filter(token=token).first()
            if token == token_obj.token:
                print(token_obj)
                user = token_obj.user
                print(user)
                return user, token
        except:
            username = request.data.get('username')
            user = UserProfile.objects.filter(username=username).first()
            if user:
                token = user.usertoken
                return user, token


def create_token(username, password):
    import hashlib
    md5_ = hashlib.md5()
    md5_.update((username+password).encode())
    token = md5_.hexdigest()
    return token


class RegisView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRegSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()        # 用户对象
        # drf-jwt生成
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        dic = serializer.validated_data
        dic['token'] = token    # 往dic字典中添加token键值对
        headers = {'Authorization': 'Bearer %s' % token}
        UserToken.objects.create(user=user, token=token)
        print(serializer.validated_data)
        return Response(dic, status=201, headers=headers)
    # 作业：将该APIVIEW换成CreateApiView来实现注册视图，下周三讲解
    # authentication_classes = [My_Authtication]
    # def post(self, request):
    #     username = request.data.get('username')
    #     password = request.data.get('password')
    #     serializer = UserRegSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()        # 用户对象
    #     # drf-jwt生成
    #     jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    #     jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    #     payload = jwt_payload_handler(user)
    #     token = jwt_encode_handler(payload)
    #     dic = serializer.validated_data
    #     dic['token'] = token    # 往dic字典中添加token键值对
    #     headers = {'Authorization': 'Bearer %s' % token}
    #     UserToken.objects.create(user=user, token=token)
    #     print(serializer.validated_data)
    #     return Response(dic, status=201, headers=headers)

    def get(self, request):
        user = request.user     # 用户对象，来自请求，通过验证方法之后所返回的用户对象，没有通过认证的用户为匿名用户
        serializer = LoginSerializer(user)
        data = serializer.data
        data['mobile'] = user.username
        return Response(data)


class LoginView(APIView):
    authentication_classes = [My_Authtication]

    def post(self, request):
        data = request.data     # 接收前端传递过来的数据，username，password
        print(data)
        serializer = LoginSerializer(data=data)
        verify_result = serializer.is_valid(raise_exception=True)
        user = request.user
        token = user.usertoken.token
        if verify_result:
            # 用户登录成功，返回用户信息
            res = serializer.validated_data
            res['token'] = token
            return Response(res)
        else:
            return Response({'message': '用户信息验证失败！'})


class UserFavViewset(ModelViewSet):
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer
    authentication_classes = [JWTAuthentication]
    lookup_field = 'goods_id'

    def get_queryset(self):
        # 根据请求用户获取收藏表中的数据
        return UserFav.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserFavDetailSerializer
        elif self.action == 'create':
            return UserFavSerializer
        else:
            return UserFavSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
