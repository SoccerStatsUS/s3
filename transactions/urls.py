from django.conf.urls import url

from . import views

urlpatterns = [

                       url(r'^$',
                           views.transaction_index,
                           name='transaction_index'),

                       
                       url(r'^(?P<transaction_id>\d+)/$',
                           views.transaction_detail,
                           name='transaction_detail'),


]
