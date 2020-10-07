from django.contrib.auth.decorators import login_required#判断是否登陆的装饰器 未登陆加参数next返回

class LoginRequiredMixin(object):
	@classmethod
	def as_view(cls,**initkwargs):
		#调用父类的as_view
		view = super(LoginRequiredMixin,cls).as_view(**initkwargs)
		return login_required(view)