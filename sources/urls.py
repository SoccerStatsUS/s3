from django.conf.urls import patterns, url

from . import views

urlpatterns = [

                       url(r'^$',
                           views.source_index,
                           name='source_index'),

                       url(r'^(?P<source_id>\d+)/$',
                           views.source_detail,
                           name='source_detail'),

    ]
