
from collections import defaultdict, Counter
import datetime

from django.db.models import Sum, Avg
from django.shortcuts import render, get_object_or_404

from .forms import CompetitionForm
from .models import Competition, SuperSeason, Season



#@cache_page(60 * 60 * 12)
def competition_index(request):

    ctype = None

    if request.method == 'GET':
        form = CompetitionForm(request.GET)

        if form.is_valid():
            competitions = Competition.objects.all()

            level = form.cleaned_data['level']
            if level:
                competitions = competitions.filter(level=level)

            ctype = form.cleaned_data['ctype']
            if ctype:
                competitions = competitions.filter(ctype=ctype)

            area = form.cleaned_data['area']
            if area:
                competitions = competitions.filter(area=area)

            code = form.cleaned_data['code']
            if code:
                competitions = competitions.filter(code=code)

            # No changes have been made; use standard competition filter.
            # is_valid() method isn't working because all fields are optional.
            if competitions.count() == Competition.objects.count():
                #competitions = Competition.objects.filter(level=1)
                slugs = ['american-league-of-professional-football',
                         'american-soccer-league-1921-1933',
                         'concacaf-champions-league',
                         'fifa-club-world-cup',
                         'fifa-world-cup',
                         'major-league-soccer',
                         'north-american-soccer-league',
                         'liga-mx',
                         'copa-america',
                         'mls-cup-playoffs',
                         'copa-libertadores',
                         'us-open-cup',
                         'concacaf-championship',
                         'gold-cup',
                         'national-womens-soccer-league',
                         'olympic-games',
                         'womens-united-soccer-association',
                         'womens-professional-soccer',
                         'premier-league',
                         ]
                competitions = Competition.objects.filter(slug__in=slugs)

            #international = form.cleaned_data['international']
            #if international is not None:
            #    competitions = competitions.filter(international=international)

        else:
            raise
            form = CompetitionForm()
    
    else:
        raise
        form = CompetitionForm()
            
    # Add a paginator.

    context = {
        'competitions': competitions.select_related(),
        'form': form,
        'ctype': ctype,
        #'itype': itype,
        #'valid': form.is_valid(),
        #'errors': form.errors,

        }
    return render(request, 
                  "competitions/index.html",
                  context)




#@cache_page(60 * 60 * 12)
def competition_detail(request, competition_slug):

    from stats.models import CompetitionStat

    competition = get_object_or_404(Competition, slug=competition_slug)


    stats = CompetitionStat.objects.filter(competition=competition)

    if stats.exclude(games_played=None).exists():
        stats = stats.exclude(games_played=None).order_by('-games_played', '-goals')[:25]
    else:
        stats = stats.exclude(games_played=None, goals=None).filter(competition=competition).order_by('-games_played', '-goals')[:25]

    games = competition.game_set

    recent_games = games.order_by('-date').exclude(date__gte=datetime.date.today()).exclude(date=None)
    if not recent_games.exists():
        recent_games = games.order_by('-date')

    context = {
        'competition': competition,
        'stats': stats,
        'games': recent_games.select_related()[:25],
        #'big_winners': competition.alltime_standings().order_by('-wins')[:50],
        #'goal_data': json.dumps([(season.goals_per_game(), season.name) for season in competition.season_set.all()]),
        }
    return render(request, 
                  "competitions/detail.html",
                  context)



#@cache_page(60 * 60 * 12)
def competition_games(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)

    return render(request, 
                  "competitions/games.html",
                  context)




#@cache_page(60 * 60 * 12)
def superseason_detail(request, superseason_slug):

    ss = get_object_or_404(SuperSeason, slug=superseason_slug)

    context = {
        'superseason': ss,
        }
    

    return render(request, 
                  "superseason/detail.html",
                  context)


#@cache_page(60 * 60 * 12)
def season_detail(request, competition_slug, season_slug):
    """
    Detail for a given season, e.g. Major League Soccer, 1996.
    """

    from stats.models import Stat
    from bios.models import Bio

    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    stats = Stat.objects.filter(season=season, competition=season.competition)
    if stats.exclude(minutes=None).exists():
        stats = stats.exclude(minutes=None).order_by('-minutes')
    elif stats.exclude(games_played=None).exists():
        stats = stats.exclude(games_played=None).order_by('-games_played')
    elif stats.exclude(goals=None).exists():
        stats = stats.exclude(goals=None).order_by('-goals')
    else:
        pass


    bios = Bio.objects.filter(id__in=stats.values_list('player'))
    nationality_count_dict = Counter(bios.exclude(birthplace__country=None).values_list('birthplace__country'))

    # Compute average attendance.
    games = season.game_set.exclude(attendance=None)
    attendance_game_count = games.count()
    average_attendance = games.aggregate(Avg('attendance'))['attendance__avg']

    goal_leaders = stats.exclude(goals=None).order_by('-goals')
    game_leaders = stats.exclude(games_played=None).order_by('-games_played')

    context = {
        'season': season,
        #'standings': season.standing_set.filter(final=True),
        'games': games[:10],
        'stats': stats[:25],
        'goal_leaders': goal_leaders[:10],
        'game_leaders': game_leaders[:10],
        'average_attendance': average_attendance,
        'attendance_game_count': attendance_game_count,
        }

    return render(request, "season/detail.html", context)
                  


#@cache_page(60 * 60 * 12)
def season_stats(request, competition_slug, season_slug):
    """
    Detail for a given season, e.g. Major League Soccer, 1996.
    """

    from stats.models import Stat
    from bios.models import Bio

    competition = get_object_or_404(Competition, slug=competition_slug)
    season = get_object_or_404(Season, competition=competition, slug=season_slug)

    stats = Stat.objects.filter(season=season, competition=season.competition)



    context = {
        'season': season,
        'stats': stats,
        }

    return render(request, "season/stats.html", context)
         
