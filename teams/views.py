from collections import OrderedDict
import datetime

from django.shortcuts import render, get_object_or_404

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

    """


    standings = Standing.objects.filter(competition=None)
    """

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
    # Add aliases.

    today = datetime.date.today()

    """
    stats = TeamStat.objects.filter(team=team)

    goal_leaders = game_leaders = None
    if stats.exclude(games_played=None).exists():
        stats = game_leaders = stats.exclude(games_played=None).order_by('-games_played')
        goal_leaders = stats.exclude(goals=None).order_by('-goals')
    elif stats.exclude(goals=None).exists():
        stats = goal_leaders = stats.exclude(goals=None).order_by('-goals')
    else:
        pass


    competition_standings = Standing.objects.filter(team=team, season=None).order_by('-wins')
    league_standings = Standing.objects.filter(team=team, season__competition__ctype='League').filter(final=True).reverse()
    recent_picks = team.pick_set.exclude(player=None).order_by('-draft__season', 'number')[:10]


    draftees = team.former_team_set.exclude(player=None).order_by('-draft__season', 'number')[:10]

    recent_games = team.game_set().filter(date__lt=today).order_by('-date').select_related()[:10]
    if recent_games.count() == 0:
        recent_games = team.game_set().select_related()[:10]

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
        #'stats': stats[:15],
        #'stats': stats,
        }
    """
        'recent_games': recent_games,
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
