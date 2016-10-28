from django.conf.urls import url

from . import views

urlpatterns = [
                       url(r'^$',
                           views.competition_index,
                           name='competition_index'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/$',
                           views.competition_detail,
                           name='competition_detail'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/games/$',
                           views.competition_games,
                           name='competition_games'),


                       url(r'^superseason/(?P<superseason_slug>[a-z0-9-]+)/$',
                           views.superseason_detail,
                           name='superseason_detail'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/$',
                           views.season_detail,
                           name='season_detail'),


                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/stats/$',
                           views.season_stats,
                           name='season_stats'),

                       url(r'^(?P<competition_slug>[a-z0-9-]+)/(?P<season_slug>[a-z0-9-]+)/games/$',
                           views.season_games,
                           name='season_games'),


]
