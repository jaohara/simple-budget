from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.transaction_log, name='transaction_log'),
	url(r'^transaction/(?P<all_boolean>all)$', views.transaction_log, name='transaction_log'),

	url(r'^transaction/add$', views.transaction_add, name='transaction_add'),
	url(r'^transaction/delete$', views.transaction_delete, name='transaction_delete'),

	url(r'^transaction_form_debug/$', views.transaction_form_debug, name='transaction_form_debug'),

	url(r'^user/create/$', views.user_create, name='user_create'),
]