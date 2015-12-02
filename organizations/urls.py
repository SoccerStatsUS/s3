from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
                       url(r'^confederations/$',
                           views.confederations_index,
                           name='confederations_index'),

                       url(r'^(?P<confederation_slug>[a-z0-9-]+)/$',
                           views.confederation_detail,
                           name='confederation_detail'),
]
