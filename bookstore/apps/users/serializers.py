import re

from rest_framework import serializers

from apps.goods.serializers import GoodsSerializer
from apps.users.models import UserProfile, SmsModel, UserFav

from datetime import datetime, timedelta

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.contrib.auth import get_user_model


class Sms_CodeSerializer(serializers.Serializer):
    mobile = serializers.CharField(label='手机号')

    def validate_mobile(self, value):
        if UserProfile.objects.filter(mobile=value).count():
            raise serializers.ValidationError('该手机号已注册')
        if not re.match(r'^1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机号不合法')
        return value


User = get_user_model()     # 获取用户模型，django的认证用户模型


class UserRegSerializer(serializers.ModelSerializer):
    """模型类序列化器"""
    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    def validate(self, attrs):
        mobile = attrs.get('username')    # 获取手机号
        print(mobile)
        redis_conn = get_redis_connection('verify_code')
        result = redis_conn.get('sms_%s' % mobile).decode()
        if len(attrs.get('code')) != 4:
            raise serializers.ValidationError('验证码错误')
        if not result:
            raise serializers.ValidationError('验证码已过期')
        if attrs.get('code') != result:
            raise serializers.ValidationError('验证码错误，或验证码已过期')
        if len(attrs.get('password')) < 6 or len(attrs.get('password')) > 20:
            raise serializers.ValidationError('密码长度不正确，应为6-20位')
        # if not attrs.get('password').isalnum():
        #     raise serializers.ValidationError('密码应由字母与数字组成')
        regex = '[a-zA-Z]{1,19}\d+'
        if not re.match(regex, attrs.get('password')):
            raise serializers.ValidationError('密码不正确')
        return attrs

    def create(self, validated_data):
        del validated_data['code']
        user = User(**validated_data)
        user.set_password(user.password)  # 密码加密
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    """模型类序列化器"""
    class Meta:
        model = User
        fields = ("username", "mobile", "password")
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False)

    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    def validate(self, attrs):
        mobile = attrs.get('username')    # 获取手机号
        if not re.match(r'^1[3-9]\d{9}', attrs.get('username')):
            raise serializers.ValidationError('用户名不合法，请重新输入')

        if len(attrs.get('password')) < 6 or len(attrs.get('password')) > 20:
            raise serializers.ValidationError('密码长度不正确，应为6-20位')
        # if not attrs.get('password').isalnum():
        #     raise serializers.ValidationError('密码应由字母与数字组成')
        regex = '[a-zA-Z]{1,19}\d+'
        if not re.match(regex, attrs.get('password')):
            raise serializers.ValidationError('密码不正确')
        return attrs


class UserFavDetailSerializer(serializers.ModelSerializer):
    """通过商品id获取到商品信息"""
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = '__all__'


class UserFavSerializer(serializers.ModelSerializer):
    """已登录用户的收藏序列化器"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())       # 指定默认的用户字段

    class Meta:
        model = UserFav
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),      # 指定验证依赖的查询集
                fields=('user', 'goods'),
                message='该商品已经收藏'
            )
        ]
        fields = '__all__'
