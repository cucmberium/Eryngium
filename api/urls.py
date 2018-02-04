from django.conf.urls import url
from api import views


urlpatterns = [
    url(r'users/recommendations.json$', views.recommendations, name='recommendations'),
    url(r'users/similar_users.json$', views.similar_users, name='similar_users'),
]
