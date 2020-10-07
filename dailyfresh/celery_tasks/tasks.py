#使用celery
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery

#下面就是解决办法：将Django中的配置信息先导入进来
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

#创建一个Celery类的实例对象 终端启动celery是处理者
app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/8')#名字,redis数据库8号中间人


#定义任务函数
@app.task#固定装饰
def send_regisder_active_email(to_email,username,token):
	'''发送激活邮件'''
	#组织邮件信息
	subject = '天天生鲜欢迎信息'
	message = ''#邮件正文 只能传字符串,不能解析html标签,html_message参数可以解析
	sender = settings.EMAIL_FROM#发件人
	receiver = [to_email]#收件人列表
	html_message = '<h1>%s,恭喜您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username,token,token)#激活链接
	send_mail(subject,message,sender,receiver,html_message=html_message)#发送函数

