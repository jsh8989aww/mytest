from django.shortcuts import render,redirect#重定向
from django.core.urlresolvers import reverse#反响解析
from django.core.mail import send_mail #发送邮件包
from django.contrib.auth import authenticate,login,logout#登陆校验包 保存session,退出包
from django.views.generic import View#视图类包 要继承的类
from django.http import HttpResponse#打印
from user.models import User,Address#用户表的模型类
from goods.models import GoodsSKU#用户表的模型类
from celery_tasks.tasks import send_regisder_active_email#倒入发送邮件函数
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #重命名加密类 
from django.conf import settings #django.conf下的是dailyfresh 下的  用其中key为加密所用
from itsdangerous import SignatureExpired #解密超时 捕获异常
from utils.mixin import LoginRequiredMixin#给函数包装一个函数外壳
from django.core.exceptions import ObjectDoesNotExist#倒入异常类
from django_redis import get_redis_connection#redis数据库拿链接包
import re #正则匹配
# Create your views here.
#/user/register
def register(request):
	if request.method == 'GET':#GET输入地址访问
		return render(request,'register.html')
	else:#post请求访问
		'''注册处理'''
		#接受提交的数据
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		email = request.POST.get('email')
		allow = request.POST.get('allow')

		#校验数据
		#校验完整性
		if not all([username,password,email]):
			#数据不完整
			return render(request,'register.html',{'errmsg':'数据不完整'})#在页面添加显示
		#校验邮箱
		if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
			return render(request,'register.html',{'errmsg':'邮箱不合法'})
		#校验协议选框
		if allow != 'on':
			return render(request,'register.html',{'errmsg':'请同意协议'})
		#校验用户名是否重复
		try:
			user = User.objects.get(username=username)#表中匹配用户名
		except User.DoesNotExist:
			#用户名不存在
			user = None
		if user:
			#用户名已存在
			return render(request,'register.html',{'errmsg':'用户名已存在'})


		#进行业务处理
		# user = User()
		# user.username = username
		# user.password = password
		# user.save()
		user = User.objects.create_user(username,email,password)
		user.is_active = 0
		user.save()

		#返回应答,跳转到首页,反向解析
		return redirect(reverse('goods:index'))
	
def register_handle(request):
	'''注册处理'''
	#接受提交的数据
	username = request.POST.get('user_name')
	password = request.POST.get('pwd')
	email = request.POST.get('email')
	allow = request.POST.get('allow')

	#校验数据
	#校验完整性
	if not all([username,password,email]):
		#数据不完整
		return render(request,'register.html',{'errmsg':'数据不完整'})#在页面添加显示
	#校验邮箱
	if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
		return render(request,'register.html',{'errmsg':'邮箱不合法'})
	#校验协议选框
	if allow != 'on':
		return render(request,'register.html',{'errmsg':'请同意协议'})
	#校验用户名是否重复
	try:
		user = User.objects.get(username=username)#表中匹配用户名
	except User.DoesNotExist:
		#用户名不存在
		user = None
	if user:
		#用户名已存在
		return render(request,'register.html',{'errmsg':'用户名已存在'})


	#进行业务处理
	# user = User()
	# user.username = username
	# user.password = password
	# user.save()
	user = User.objects.create_user(username,email,password)
	user.is_active = 0
	user.save()

	#返回应答,跳转到首页,反向解析
	return redirect(reverse('goods:index'))

#注册:/user/register   调用RegisterView.as_view() 时自动识别是get还是post请求 然后分配给get()和post()
class RegisterView(View):
	def get(self,request):
		return render(request,'register.html')

	def post(self,request):
		'''注册处理'''
		#接受提交的数据
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		email = request.POST.get('email')
		allow = request.POST.get('allow')#复选框

		#校验数据
		#校验完整性
		if not all([username,password,email]):
			#数据不完整
			return render(request,'register.html',{'errmsg':'数据不完整'})#在页面添加显示
		#校验邮箱
		if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
			return render(request,'register.html',{'errmsg':'邮箱不合法'})
		#校验协议选框
		if allow != 'on':
			return render(request,'register.html',{'errmsg':'请同意协议'})
		#校验用户名是否重复
		try:
			user = User.objects.get(username=username)#表中匹配用户名
		except User.DoesNotExist:
			#用户名不存在
			user = None
		if user:
			#用户名已存在
			return render(request,'register.html',{'errmsg':'用户名已存在'})


		#进行业务处理
		# user = User()
		# user.username = username
		# user.password = password
		# user.save()
		user = User.objects.create_user(username,email,password)#替代上面插入数据 变量名固定
		user.is_active = 0
		user.save()
		#发送激活邮件,包含激活链接:/user/active/1
		#激活链接中需要包含用户的身份信息,并且要把身份信息加密
		#加密用户身份信息
		serializer = Serializer(settings.SECRET_KEY,3600)#加密方式key,有效时间1个小时
		info = {'confirm':user.id}#被加密数据  地址中的1
		token = serializer.dumps(info)#加密数据 字节的
		token = token.decode()#字节转默认utf8
		#发邮件
		"""subject = '天天生鲜欢迎信息'
		message = ''#邮件正文 只能传字符串,不能解析html标签,html_message参数可以解析
		sender = settings.EMAIL_FROM#发件人
		receiver = [email]#收件人列表
		html_message = '<h1>%s,恭喜您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username,token,token)#激活链接
		send_mail(subject,message,sender,receiver,html_message=html_message)#发送函数"""
		#发邮件 celery发出者
		send_regisder_active_email.delay(email,username,token)#此函数装饰器后有的函数,插入队列
		#返回应答,跳转到首页,反向解析
		return redirect(reverse('goods:index'))

#点击邮箱链接后解密处理
class ActiveView(View):
	'''用户激活'''
	def get(self,request,token):
		'''进行用户激活'''
		#进行解密,获取要激活的用户信息
		serializer = Serializer(settings.SECRET_KEY,3600)
		try:
			info = serializer.loads(token)
			#获取带激活用户id
			user_id = info['confirm']
			#根据id获得操作数据库表的对象,去增删改查表
			user = User.objects.get(id=user_id)
			user.is_active = 1#设置激活
			user.save()
			#跳转到登陆页面 反向解析
			return redirect(reverse('user:login'))
		except SignatureExpored as e:
			return HttpResponse('激活链接过期')

#/user/login
class LoginView(View):
	'''登陆'''
	def get(self,request):
		'''显示登陆页面'''
		#判断是否记住了用户名
		if 'username' in request.COOKIES:#cooki中有没有用户
			username = request.COOKIES.get('username')
			checked = 'checked'#设置复选框选中
		else:#cooki没有填空
			username = ''
			checked = ''
		return render(request,'login.html',{'username':username,'checked':checked})

	def post(self,request):
		'''登陆校验'''
		#接受数据
		username = request.POST.get('username')
		password = request.POST.get('pwd')
		#校验数据
		if not all([username,password]):
			#数据不完整
			return render(request,'login.html',{'errmsg':'数据不完整'})#
		#业务处理:登陆校验
		user = authenticate(username=username,password=password)
		if user is not None:
			#用户名密码正确
			if user.is_active:
				#用户已激活
				#记录用户的登陆状态 session,访问以后的网页都会验证是否为已登陆状态
				login(request,user)#
				#获取登陆后要跳转的地址,如果没有就访问第二参数 返回next就是记录你要访问的地址
				next_url = request.GET.get('next',reverse('goods:index'))

				#response = redirect(reverse('goods:index'))#反向解析重定向
				response = redirect(next_url)#重定向
				#判断是否需要记住用户名
				remember = request.POST.get('remember')
				if remember == 'on':
					#记住用户名
					response.set_cookie('username',username,max_age=7*24*3600)#存cook
				else:
					response.delete_cookie('username')

				#返回首页
				return response

			else:
				#用户未激活
				return render(request,'login.html',{'errmsg':'账户为激活'})
		else:
			#用户名或密码错误
			return render(request,'login.html',{'errmsg':'用户名或密码错误'})

#/user/logout
class LogoutView(View):
	'''退出登陆'''
	def get(self,request):
		#清除用户的session信息
		logout(request)

		#跳转到首页
		return redirect(reverse('goods:index'))
		
#/user
class UserInfoView(LoginRequiredMixin,View):
	'''用户中心-信息页'''
	#page 选中函数
	#request.user
	#如果用户未登陆->AnonymoysUser类的一个实例
	#如果用户登陆->User类的一个实例
	#request.user.is_authenticated() 页面中判断是否登陆
	#除了你给模板文件传递的模板变量之外,djang框架会把request.user对象也传给模板,也就是说在模板页面中直接可以用user.is_authenticated()
	

	def get(self,request):
		#获取用户基本信息
		user = request.user
		address = Address.objects.get_default_address(user)

		#获取用户最近浏览记录
		#from redis import StrictRedis
		#sr = StrictRedis(host='127.0.0.1',port='6379',db=9)
		con = get_redis_connection('default')#代替上句拿redis链接
		history_key = 'history_%d'%user.id #拿到history_用户id 的数据
		#获取用户最新浏览的5个商品的id
		sku_ids = con.lrange(history_key,0,4)
		#从数据库中查询用户浏览商品的具体信息 
		#goods_li = GoodsSKU.objects.filter(id__in=sku_ids)?????
		# goods_res = []
		# for a_id in sku_ids:
		# 	for goods in goods_li:
		# 		if a_id == goods.id:
		# 			goods_res.append(goods)

		#遍历获取用户浏览的商品信息
		goods_li = []
		for id in sku_ids:
			goods = GoodsSKU.objects.get(id=id)
			goods_li.append(goods)

		#组织上下文
		context = {'page':'user','address':address,'goods_li':goods_li}

		return render(request,'user_center_info.html',context)
#/user/order
class UserOrderView(LoginRequiredMixin,View):
	'''用户中心-订单页'''
	def get(self,request):
		#获取用户的订单信息

		return render(request,'user_center_order.html',{'page':'order'})
#user/address
class AddressView(LoginRequiredMixin,View):
	'''用户中心-地址页'''
	def get(self,request):
		#获取用户的默认收获地址
		#获取登陆用户对象
		user = request.user
		#获取用户的默认收货地址
		# try:
		# 	address = Address.objects.get(user=user,is_default=True)#user 是user.username
		# #except Address.DoecNotExist:#模型类为什么缺少该属性?
		# except ObjectDoesNotExist:
		# 	#不存在收货地址
		# 	address = None
		address = Address.objects.get_default_address(user)
		return render(request,'user_center_site.html',{'page':'address','address':address})

	def post(self,request):
		'''地址添加'''
		#接受数据
		receiver = request.POST.get('receiver')
		addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		phone = request.POST.get('phone')

		#校验数据
		#校验完整性
		if not all([receiver,addr,phone]):
			return render(request,'user_center_site.html',{'errmsg':'数据不完整'})#在页面添加显示
		#校验手机
		if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
			return render(request,'user_center_site.html',{'errmsg':'电话格式不正确'})
		#业务处理:地址添加
		#如果用户已存在默认收货地址,添加的地址不作为默认收货地址,否则作为默认收货地址
		#获取登陆用户对象
		user = request.user
		# try:
		# 	address = Address.objects.get(user=user,is_default=True)#user 是user.username
		# #except Address.DoecNotExist:
		# except ObjectDoesNotExist:
		# 	#不存在收货地址
		# 	address = None
		address = Address.objects.get_default_address(user)
		#默认变量
		if address:
			is_default = False
		else:
			is_default =True

		#添加地址
		Address.objects.create(user=user,receiver=receiver,addr=addr,zip_code=zip_code,phone=phone,is_default=is_default)# 简单添加写法
		#返回应答
		return redirect(reverse('user:address'))