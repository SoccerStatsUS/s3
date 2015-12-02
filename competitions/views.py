from django.shortcuts import render, get_object_or_404

from .forms import CompetitionForm
from .models import Competition

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
    competition = get_object_or_404(Competition, slug=competition_slug)

    #games = competition.game_set.all()
    games = []

    stats = sx = []

    """
    stats = CompetitionStat.objects.filter(competition=competition)

    if stats.exclude(games_played=None).exists():
        sx = stats.exclude(games_played=None).order_by('-games_played', '-goals')[:25]
    else:
        sx = stats.exclude(games_played=None, goals=None).filter(competition=competition).order_by('-games_played', '-goals')[:25]


    recent_games = games.order_by('-date').exclude(date__gte=datetime.date.today()).exclude(date=None)
    if not recent_games.exists():
        recent_games = games.order_by('-date')

    """

    context = {
        'competition': competition,
        'stats': sx,
        #'games': recent_games.select_related()[:25],
        'games': games,
        #'big_winners': competition.alltime_standings().order_by('-wins')[:50],
        #'goal_data': json.dumps([(season.goals_per_game(), season.name) for season in competition.season_set.all()]),
        }
    return render(request, 
                  "competitions/detail.html",
                  context)



