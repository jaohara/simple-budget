from django.conf.urls import url
from . import views

# testing generic class-based views
from django.views.generic import TemplateView

urlpatterns = [
	url(r'^$', views.transaction_log, name='transaction_log'),
	url(r'^transaction/(?P<all_boolean>all)$', views.transaction_log, name='transaction_log'),

	url(r'^transaction/add$', views.transaction_add, name='transaction_add'),
	url(r'^transaction/delete$', views.transaction_delete, name='transaction_delete'),

	url(r'^transaction_form_debug/$', views.transaction_form_debug, name='transaction_form_debug'),

	#url(r'^categories/$', views.category_display, name='category_display'),
	# above is real, below is test
	url(r'^categories/$', 
		TemplateView.as_view(template_name="budget_app/categories.html"), 
		name="category_display"),

	url(r'^user/create/$', views.user_create, name='user_create'),
]