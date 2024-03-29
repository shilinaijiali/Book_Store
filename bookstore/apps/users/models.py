from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from apps.goods.models import Goods


class UserProfile(AbstractUser):
    """
    用户表，新增字段如下
    """
    GENDER_CHOICES = (
        ("male", u"男"),
        ("female", u"女")
    )
    # 用户注册时我们要新建user_profile 但是我们只有手机号
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    # 保存出生日期，年龄通过出生日期推算
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="female", verbose_name="性别")
    # mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话", help_text="电话号码")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        app_label = 'users'

    def __str__(self):
        return self.username


class UserToken(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    token = models.CharField(max_length=255, verbose_name='用户令牌')

    class Meta:
        db_table = 'user_token'


class SmsModel(models.Model):
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=4, verbose_name='验证码')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_VerifyCode'
        ordering = ['-add_time']


class UserFav(models.Model):
    """
    用户收藏操作
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name
        app_label = 'users'

        # 多个字段作为一个联合唯一索引
        unique_together = ("user", "goods")

    def __str__(self):
        return self.user.username
