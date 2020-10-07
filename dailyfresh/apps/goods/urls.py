from django.conf.urls import url
from goods.views import IndexView
from goods import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^$',views.index,name='index'),#首页
    url(r'^$',IndexView.as_view(),name='index'),#首页
]
 