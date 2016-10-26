from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.country_index, name='country_index'),

    url(r'^countries/(?P<slug>.+)/$',
        views.country_detail,
        name='country_detail'),

    
    url(r'^states/(?P<slug>.+)/$',
        views.state_detail,
        name='state_detail'),



    url(r'^cities/(?P<slug>.+)/$',
        views.city_detail,
        name='city_detail'),

    url(r'^stadiums/(?P<slug>[a-z0-9-]+)/$',                       
        views.stadium_detail,
        name='stadium_detail'),

    url(r'^stadiums/(?P<slug>[a-z0-9-]+)/games/$',                       
        views.stadium_games,
        name='stadium_games'),

]
