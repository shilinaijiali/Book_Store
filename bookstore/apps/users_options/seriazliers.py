from rest_framework import serializers
from .models import UserLeavingMessage, UserAddress
import re


class UserUpdateSerializer(serializers.Serializer):
    # 保存出生日期，年龄通过出生日期推算
    birthday = serializers.DateField(allow_null=True, label="出生年月")
    gender = serializers.CharField(max_length=6, default="female", label="性别")
    # mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    mobile = serializers.CharField(allow_null=True, max_length=11, label="电话", help_text="电话号码")
    email = serializers.EmailField(max_length=100, allow_null=True, label="邮箱")
    username = serializers.CharField(max_length=30, allow_null=True, label="用户姓名")

    def validate(self, attrs):
        print(self.context['request'].data)
        print(attrs)
        name = attrs.get('username')
        print(name)
        if not re.match(r'1[3-9]\d{9}', name):
            raise serializers.ValidationError('用户名错误，应该以手机号作为用户名')
        regex = r'[a-zA-Z].*@qq.com|[1-9]{6,11}@qq.com|[a-zA-Z].*@163.com'
        email_ = attrs.get('email')
        if not re.match(regex, email_):
            raise serializers.ValidationError('邮箱格式有错，请重新输入')
        return attrs

    def update(self, instance, validated_data):     # instance就是要修改的模型类对象
        instance.name = validated_data.get('name')
        instance.birthday = validated_data.get('birthday')
        instance.gender = validated_data.get('gender')
        instance.mobile = validated_data.get('mobile')
        instance.email = validated_data.get('email')
        instance.save()
        return instance


class LeavingSerializer(serializers.Serializer):
    """
    在用Dajngo RestFramework时， 有时候需要这么一个场景，前端不需要传一个或多个字段，这些字是直接根据用户登录信息判断自动赋值的，如果用mixin和viewset进行搭配写接口，要么重写create,
    update等方法，要么就是在serializer_class时就定义默认值，而第二种方法明显简单一些。
    """
    id = serializers.IntegerField(label='留言ID', read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    message_type = serializers.IntegerField(label='留言类型')
    subject = serializers.CharField(label='主题', max_length=32)
    message = serializers.CharField(label='留言内容', max_length=1024)
    file = serializers.FileField(label='上传文件', allow_empty_file=True, allow_null=True)

    def create(self, validated_data):
        print(validated_data)
        res = UserLeavingMessage.objects.create(**validated_data)
        return validated_data


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserAddress
        fields = '__all__'
