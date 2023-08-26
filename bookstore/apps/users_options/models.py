from django.db import models
from apps.users.models import UserProfile


class UserLeavingMessage(models.Model):
    """用户留言"""
    MESSAGE_CHOICES = (
        (1, '留言'),
        (2, '投诉'),
        (3, '询问'),
        (4, '售后'),
        (5, '求购')
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    message_type = models.IntegerField(verbose_name='留言类型', choices=MESSAGE_CHOICES, default=1, help_text=u'留言类型: 1('
                                                                                                          u'留言),'
                                                                                                          u'2(投诉),'
                                                                                                          u'3(询问),'
                                                                                                          u'4(售后),'
                                                                                                          u'5(求购)')
    subject = models.CharField(verbose_name='主题', max_length=32, default='')
    message = models.CharField(verbose_name='留言内容', max_length=1024, default='')
    file = models.FileField(verbose_name='上传文件', help_text='上传的文件', upload_to='message/images/', null=True)
    add_time = models.DateTimeField(auto_now=True, auto_created=True, verbose_name='添加时间')

    class Meta:
        db_table = 'db_user_message'
        verbose_name = '用户留言'
        verbose_name_plural = verbose_name
        app_label = 'users_options'

    def __str__(self):
        return self.subject


class UserAddress(models.Model):
    """用户收货地址"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    province = models.CharField(max_length=16, verbose_name='省份')
    city = models.CharField(max_length=16, verbose_name='城市')
    district = models.CharField(max_length=16, verbose_name='区域')
    address = models.CharField(max_length=64, verbose_name='详细地址')
    signer_name = models.CharField(max_length=100, default="", verbose_name="签收人")
    signer_mobile = models.CharField(max_length=11, default="", verbose_name="电话")
    add_time = models.DateTimeField(auto_now_add=True, auto_created=True, verbose_name="添加时间")

    class Meta:
        db_table = 'db_user_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        app_label = 'users_options'

    def __str__(self):
        return self.address
