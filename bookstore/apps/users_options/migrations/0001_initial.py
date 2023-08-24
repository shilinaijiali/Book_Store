# Generated by Django 3.1.7 on 2021-09-24 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLeavingMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(auto_created=True, auto_now=True, verbose_name='添加时间')),
                ('message_type', models.IntegerField(choices=[(1, '留言'), (2, '投诉'), (3, '询问'), (4, '售后'), (5, '求购')], default=1, help_text='留言类型: 1(留言),2(投诉),3(询问),4(售后),5(求购)', verbose_name='留言类型')),
                ('subject', models.CharField(default='', max_length=32, verbose_name='主题')),
                ('message', models.CharField(default='', max_length=1024, verbose_name='留言内容')),
                ('file', models.FileField(help_text='上传的文件', null=True, upload_to='message/images/', verbose_name='上传文件')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户留言',
                'verbose_name_plural': '用户留言',
                'db_table': 'db_user_message',
            },
        ),
    ]