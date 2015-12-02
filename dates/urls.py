from django.conf.urls import url

from . import views

urlpatterns = [

                       url(r'^(?P<year>\d+)/$',
                           views.year_detail,
                           name='year_detail'),

                       url(r'^(?P<year>\d+)/(?P<month>\d*)/$',
                           views.month_detail,
                           name='month_detail'),

                       url(r'^(?P<year>\d+)/(?P<month>\d*)/(?P<day>\d*)/$',
                           views.date_detail,
                           name='date_detail'),

                       url(r'^day/(?P<month>\d+)/(?P<day>\d+)/$',
                           views.day_detail,
                           name='day_detail'),

]
