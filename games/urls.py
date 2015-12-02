from django.conf.urls import url

from . import views

urlpatterns = [

                       url(r'^$',
                           views.games_index,
                           name='games_index'),

                       
                       url(r'^(?P<game_id>\d+)/$',
                           views.game_detail,
                           name='game_detail'),

]
