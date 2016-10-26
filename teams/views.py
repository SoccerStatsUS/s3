from collections import OrderedDict
import datetime
import json

from django.shortcuts import render, get_object_or_404

from games.models import Game
from stats.models import TeamStat, Stat
from teams.models import Team


#@cache_page(60 * 60 * 12)
def team_index(request):
    """
    Teams shown by letter.
    """
    # This is not good but not sure how to fix.
    # Need to broaden team standing generation so we use that
    # to pull all teams.
    
    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()

    name_dict = OrderedDict()

    #standings = Standing.objects.filter(competition=None)

    for letter in letters:
        teams = Team.objects.filter(name__istartswith=letter)
        #team_standings = standings.filter(team__name__istartswith=letter)[:10]
        #name_dict[letter] = team_standings
        name_dict[letter] = teams
        
    context = {
        'name_dict': name_dict,
        }

    return render(request, 
                  "teams/index.html",
                  context)


#@cache_page(60 * 60 * 12)
def team_name_fragment(request, fragment):
    return team_list_generic(request,
                             Team.objects.filter(name__istartswith=fragment),
                             'alltime')


def team_detail(request, team_slug):
    """
    Just about the most important view of all.
    """
    team = get_object_or_404(Team, slug=team_slug)

    today = datetime.date.today()


    stats = TeamStat.objects.filter(team=team)

    goal_leaders = game_leaders = None
    if stats.exclude(games_played=None).exists():
        stats = game_leaders = stats.exclude(games_played=None).order_by('-games_played')
        goal_leaders = stats.exclude(goals=None).order_by('-goals')
    elif stats.exclude(goals=None).exists():
        stats = goal_leaders = stats.exclude(goals=None).order_by('-goals')
    else:
        pass


    #competition_standings = Standing.objects.filter(team=team, season=None).order_by('-wins')
    #league_standings = Standing.objects.filter(team=team, season__competition__ctype='League').filter(final=True).reverse()
    #recent_picks = team.pick_set.exclude(player=None).order_by('-draft__season', 'number')[:10]
    #draftees = team.former_team_set.exclude(player=None).order_by('-draft__season', 'number')[:10]


    recent_games = team.game_set().filter(date__lt=today).order_by('-date').select_related()[:10]
    if recent_games.count() == 0:
        recent_games = team.game_set().select_related()[:10]

    """

    current_staff = team.position_set.filter(end=None)

    # Get notable positions.
    positions = team.position_set.filter(name='Head Coach')
    if positions.count() == 0:
        positions = team.position_set.exclude(id__in=current_staff)

    #awards = team.awards.order_by('-season')

    """

    """
    if game_leaders:
        game_leaders = game_leaders[:15]

    if goal_leaders:
        goal_leaders = goal_leaders[:15]
    """


    context = {
        'team': team,
        #'awards': awards,
        'stats': stats[:15],
        'recent_games': recent_games,
        'transactions': team.transactions_to.all()[:10],
        }
    """

        'competition_standings': competition_standings,
        'league_standings': league_standings,
        'positions': positions,
        'current_staff': current_staff,
        'recent_picks': recent_picks,
        'draftees': draftees,
        'game_leaders': game_leaders,
        'goal_leaders': goal_leaders,
        'gx': True,
        }
    """

    return render(request, 
                  "teams/detail.html",
                  context)




#@cache_page(60 * 24)
def team_games(request, team_slug):
    """
    A filterable table of all games played by a team.
    """
    team = get_object_or_404(Team, slug=team_slug)

    games = Game.objects.team_filter(team)

    """
    if request.method == 'GET':
        form = TeamGameForm(team, request.GET)

        if form.is_valid():

            if form.cleaned_data['opponent']:
                games = Game.objects.team_filter(team, form.cleaned_data['opponent'])
            else:
                games = Game.objects.team_filter(team)

            if form.cleaned_data['competition']:
                games = games.filter(competition=form.cleaned_data['competition'])

            if form.cleaned_data['stadium']:
                games = games.filter(stadium=form.cleaned_data['stadium'])

            r = form.cleaned_data['result']
            if r:
                if r == 't':
                    games = games.filter(team1_result='t')
                else:
                    games = games.filter(Q(team1=team, team1_result=r) | Q(team2=team, team2_result=r))



            if form.cleaned_data['year']:
                year = int(form.cleaned_data['year'])
                games = games.exclude(date=None)
                year_filter = form.cleaned_data['year_filter']
                if year_filter == '>':
                    d = datetime.date(year, 1, 1)
                    games = games.filter(date__gte=d)
                elif year_filter == '<':
                    d = datetime.date(year, 12, 31)
                    games = games.filter(date__lte=d)
                else:
                    games = games.filter(date__year=year)
    else:
        form = TeamGameForm(bio)
    """

    games = games.select_related().order_by('-has_date', '-date', '-season')
    #games = games.select_related().order_by('-date', '-season')

    #standings = [TempGameStanding(games, team)]
    standings = []


    calendar_data = [(e.date.isoformat(), e.result(team), e.score(), e.opponent(team).name) for e in games if e.date]

    context = {
        'team': team,
        #'form': form,
        'games': games,
        'standings': standings,
        'calendar_data': json.dumps(calendar_data),
        }

    return render(request, "teams/games.html", context)



def team_stats(request, team_slug):

    team = get_object_or_404(Team, slug=team_slug)

    context = {
        'team': team,
        'stats': team.teamstat_set.all(),
    }

    return render(request, "teams/stats.html", context)
