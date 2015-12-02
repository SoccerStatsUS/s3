from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$',
        views.person_index,
        name='person_index'),

    url(r'^(?P<slug>[a-z0-9-]+)/$',
        views.person_detail,
        name='person_detail'),


]
