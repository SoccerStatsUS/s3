from django.conf.urls import url

from . import views

urlpatterns = [

                       url(r'^$',
                           views.transaction_index,
                           name='transaction_index'),



]
