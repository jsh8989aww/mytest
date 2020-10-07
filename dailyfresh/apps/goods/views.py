from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsType,GoodsSKU,Goods,GoodsImage,IndexGoodsBanner,IndexTypeGoodsBanner,IndexPromotionBanner
# Create your views here.

def index(request):
	'''首页'''
	return render(request,'index.html')

#首页 http://127.0.0.1:8000
class IndexView(View):
	#首页显示
	def get(self,request):
		#获取商品的种类信息
		types = GoodsType.objects.all()
		#获取首页轮播商品信息
		goods_banners = IndexGoodsBanner.objects.all().order_by('index')
		#获取首页促销活动信息
		promotion_banners = IndexTypeGoodsBanner.objects.all().order_by('index')

		#获取首页分类商品展示信息
		#type_goods_banners = IndexTypeGoodsBanner.objects.all()
		for type in types:
			#获取type种类首页分类商品的图片展示信息
			image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')
			#获取type种类首页分类商品的文字展示信息	
			title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by('index')
			#动态给对象type添加属性,分别保存上面两种信息
			type.image_banners = image_banners
			type.title_banners = title_banners
		#获取用户购物车中商品的数目
		cart_count = 0

		#组织横版上下文
		context = {'types':types,
					'goods_banners':goods_banners,
					'promotion_banners':promotion_banners,
					'cart_count':cart_count
					}


		return render(request,'index.html',context)