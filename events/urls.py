from django.conf.urls import url

from . import views

urlpatterns = [

                       url(r'^$',
                           views.event_index,
                           name='event_index'),

                       
                       url(r'^(?P<event_id>\d+)/$',
                           views.event_detail,
                           name='event_detail'),


]
