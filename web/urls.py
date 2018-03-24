from django.conf.urls import url
from web import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^users/(?P<target_user_acct>([a-zA-Z0-9_]+)@(.+))/$', views.user, name='user'),
    url(r'^help/api/$', views.api, name='help_api'),
]
