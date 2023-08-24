# tasks.py文件名，任务文件名，是固定的就是tasks.py
import uuid
import logging
from utils.yuntongxun.ccp_sms import CCP
from celery_tasks.main import celery_app

logger = logging.getLogger('django')        # 日志器获取，用户日志信息输入

@celery_app.task(name='send_sms_code')      # 将被装饰的函数，做为异步任务提交给celery
def send_sms_code(mobile, sms_code):
    """发送短信验证码"""
    try:
        __business_id = uuid.uuid1()

        resu = CCP().send_template_sms(mobile, [sms_code, 5], 1)
        print(resu)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if resu == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
            return resu
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            return resu

