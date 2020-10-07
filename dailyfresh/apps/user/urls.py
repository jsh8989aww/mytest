from django.conf.urls import url
#from user import views
#配置url前倒入视图类
from user.views import RegisterView,ActiveView,LoginView,UserInfoView,UserOrderView,AddressView,LogoutView#类视图
from django.contrib.auth.decorators import login_required#判断是否登陆的装饰器 未登陆加参数next返回

urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^register$',views.register,name='register' ),#注册路由
    #url(r'^register_handle$',views.register_handle,name='register_handle' ),#注册视图
    url(r'^register$',RegisterView.as_view(),name='register'),#类视图调用
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),#用户激活 捕获()中的加密字符并设置为token ,对应视图函数中要有参数接受
    url(r'^login$',LoginView.as_view(),name='login'),#登陆
    url(r'^logout$',LogoutView.as_view(),name='logout'),#注销登陆
    # url(r'^$',login_required(UserInfoView.as_view()),name='user'),#用户中心-信息页
    # url(r'^order$',login_required(UserOrderView.as_view()),name='order'),#用户中心-订单页
    # url(r'^address$',login_required(AddressView.as_view()),name='address'),#用户中心-地址页
    url(r'^$',UserInfoView.as_view(),name='user'),#用户中心-信息页
    url(r'^order$',UserOrderView.as_view(),name='order'),#用户中心-订单页
    url(r'^address$',AddressView.as_view(),name='address'),#用户中心-地址页
]
  