from django.conf.urls import url

from . import views

urlpatterns = [

                       url(r'^$',
                           views.team_index,
                           name='team_index'),


                       url(r'^az/(?P<fragment>.+)/$',
                           views.team_name_fragment,
                           name='team_name_fragment'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/$',
                           views.team_detail,
                           name='team_detail'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/games/$',
                           views.team_games,
                           name='team_games'),

                       url(r'^(?P<team_slug>[a-z0-9-]+)/stats/$',
                           views.team_stats,
                           name='team_stats'),


]
