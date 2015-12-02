from django.conf.urls import url

from . import views

urlpatterns = [
                       url(r'^$',
                           views.competition_index,
                           name='competition_index'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/$',
                           views.competition_detail,
                           name='competition_detail'),

]
