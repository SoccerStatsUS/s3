from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse

from .models import Bio



#@cache_page(60 * 60 * 12)
def person_index(request):

    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()
    stats = CareerStat.objects.order_by('-player__hall_of_fame', '-games_played').select_related()

    name_dict = OrderedDict()
    for letter in letters:
        name_dict[letter] = stats.filter(player__name__istartswith=letter)[:10]


    #most_games = CareerStat.objects.exclude(games_played=None).order_by('-games_played')[:25]
    #most_goals = CareerStat.objects.exclude(goals=None).order_by('-goals')[:25]

    context = {
        'name_dict': name_dict,
        #'most_games': most_games,
        #'most_goals': most_goals,
        }

    return render(request, 
                  "bios/index.html",
                  context)



def person_detail(request, slug):
    bio = get_object_or_404(Bio, slug=slug)
    return person_detail_abstract(request, bio)

def person_id_detail(request, pid):
    bio = get_object_or_404(Bio, id=pid)
    return person_detail_abstract(request, bio)

def person_detail_abstract(request, bio):
    """
    competition_stats = bio.competition_stats().order_by('competition__international', '-games_played')
    team_stats = bio.team_stats().order_by('-games_played')
    #league_stats = Stat.objects.filter(player=bio).filter(competition__ctype='League').order_by('season')
    league_stats = Stat.objects.filter(player=bio).order_by('season')
    domestic_stats = league_stats.filter(team__international=False).reverse()
    international_stats = league_stats.filter(team__international=True).reverse()
    """
    
    context = {
        "bio": bio,
        }

    """
        'recent_game_stats': bio.gamestat_set.order_by('game')[:10],
        'league_stats': league_stats,
        'domestic_stats': domestic_stats,
        'international_stats': international_stats,
        'competition_stats': competition_stats,
        'career_stat': bio.career_stat(),
        'team_stats': team_stats,
        'picks': bio.pick_set.exclude(draft__competition=None).order_by('draft__season', 'draft__start'),
        'coach_stats': bio.coachstat_set.order_by('season'),
        'positions': bio.position_set.order_by('start'),
        'refs': bio.ref_set()[:10]
        }
    """

    return render(request, 
                  "bios/detail.html",
                  context)
