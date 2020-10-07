from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
	'''fast dfs文件存储类'''
	def __init__(self,client_conf=None,base_url=None):
		'''初始化'''
		if client_conf is None:
			#client_conf = './utils/fdfs/client.conf'
			client_conf = settings.FDFS_CLIENT_CONF
		self.clint_conf = client_conf
			
		if base_url is None:
			#base_url = 'http://127.0.0.1:8888/'
			base_url = settings.FDFS_URL
		self.base_url = base_url

	def _open(self,name,mode='rb'):
		'''打开文件时使用'''
		pass

	def _save(self,name,content):
		'''保存文件时使用'''
		#name:你选择上传文件的名字
		#content:包含你上传文件内容的 File对象
		
		#创建一个Fdfs_client对象
		#client = Fdfs_client('./utils/fdfs/client.conf')
		client = Fdfs_client(self.clint_conf)

		#上传文件到fast dfs系统中
		res = client.upload_by_buffer(content.read())	

		#上传后信息状态会存储到字典
		#dict
		# {
		# 	'Group name':group_name,
		# 	'Remote file_id':remote_file_id,
		# 	'Status':'Upload successed.',
		# 	'Local file name':'',
		# 	'Uploaded size':upload_size,
		# 	'Storage IP:storage_ip		
		# }

		if res.get('Status') != 'Upload successed.':
			#上传失败
			raise Exception('上传文件到fast djs失败')

		#获取返回的文件ID
		filename = res.get('Remote file_id')

		return filename

	def exists(self,name):
		'''django判断文件名是否可用'''
		return False

	#网页 图片请求地址url
	def url(self,name):
		'''返回访问文件的url路径'''
		#return 'http://127.0.0.1:8888/'+name
		return self.base_url+name