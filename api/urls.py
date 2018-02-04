from django.conf.urls import url
from api import views


urlpatterns = [
    url(r'users/recommendations.json$', views.recommendations, name='recommendations'),
    url(r'users/similar_user.json$', views.similar_user, name='similar_user'),
]
