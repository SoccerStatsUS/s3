from collections import defaultdict, Counter

from django.shortcuts import render, get_object_or_404

from teams.models import Team
from .models import Game, GameSource



def homepage(request):
    """
    Homepage
    """

    team = Team.objects.get(slug='united-states')
    games = Game.objects.team_filter(team).order_by("-date").exclude(date=None)[:10]

    context = {
        'games': games,
        }

    return render(request, 
                  "games/homepage.html",
                  context)


def games_index(request):
    # Add a paginator.
    # This is probably unnecesary.
    # Consider turning into a games analysis page.
    # Home/Away advantage, graphs, etc.
    
    games = Game.objects.order_by("-date").exclude(date=None)
    game_count = games.count()

    by_year = Counter([e.year for e in games.values_list('date', flat=True)])

    #gd = defaultdict(int)
    #ceiling = 8
    #for game in games.exclude(home_team=None).exclude(team1_score=None).exclude(team2_score=None):
    #    gd[(min(game.home_score(), ceiling), min(game.away_score(), ceiling))] += 1

    context = {
        'games': games,
        'game_count': game_count,
        'games_by_year': json.dumps(sorted(by_year.items())),
        'goal_distribution': json.dumps(gd),
        }

    return render(request, 
                  "games/index.html",
                  context)


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    context = {
        'game': game,
        #'goals': game.goal_set.order_by('minute'),
        'game_sources': GameSource.objects.filter(game=game),

        }
    return render(request, 
                              "games/detail.html",
                              context)
                              


