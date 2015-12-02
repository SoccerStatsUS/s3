from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.country_index, name='country_index'),

    url(r'^countries/(?P<slug>.+)/$',
        views.country_detail,
        name='country_detail'),

]
