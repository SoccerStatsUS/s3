from django.db.models import Max, Min, Count, Sum, Avg
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Country, City, Stadium

from games.models import Game
from places.models import Stadium
from teams.models import Team



def country_index(request):
        """
        A list of all countries, by name
        """

        context = {
                #'countries': Country.objects.annotate(game_count=Count('game')).annotate(total_attendance=Sum('game__attendance')).order_by('-game_count'),
                'countries': Country.objects.order_by('name')
                }

        return render(request, 
                      "places/country_index.html",
                      context)




def country_detail(request, slug):
        """
        """

        country = get_object_or_404(Country, slug=slug)
        stadiums = Stadium.objects.filter(city__country=country)
        births = competitions = []
        #births = Bio.objects.filter(birthplace__country=country).order_by('birthdate')
        #competitions = Competition.objects.filter(scope='Country', area=country.name)
        cities = City.objects.filter(country=country)

        context = {
                'country': country,
                'births': births,
                'stadiums': stadiums,
                'competitions': competitions,
                'cities': cities,
                }
        return render(request, 
                      "places/country_detail.html",
                      context)




def state_detail(request, slug):
        """
        """

        state = get_object_or_404(State, slug=slug)
        births = Bio.objects.filter(birthplace__state=state)
        stadiums = Stadium.objects.filter(city__state=state)
        games = Game.objects.exclude(city=None).filter(city__state=state)
        
        context = {
                'state': state,
                'births': births,
                'stadiums': stadiums,
                'games': games,
                }
        return render_to_response("places/state_detail.html",
                                  context,
                                  context_instance=RequestContext(request))




def city_detail(request, slug):
        """
        """

        city = get_object_or_404(City, slug=slug)

        context = {
                'city': city,
                'teams': Team.objects.filter(city=city),
                'games': Game.objects.filter(city=city),
                'stadiums': city.stadium_set.annotate(game_count=Count('game')).annotate(total_attendance=Sum('game__attendance')).order_by('-game_count')
                }

        return render(request, 
                      "places/city_detail.html",
                      context)



def stadium_detail(request, slug):
        """
        Stadium detail view.
        """

        stadium = get_object_or_404(Stadium, slug=slug)

        # Compute average attendance.
        games = stadium.game_set.exclude(attendance=None)
        attendance_game_count = games.count()
        #average_attendance = games.aggregate(Avg('attendance'))['attendance__avg']
        #standings = StadiumStanding.objects.filter(stadium=stadium).order_by('-games')

        context = {
                'stadium': stadium,
                #'average_attendance': average_attendance,
                'attendance_game_count': attendance_game_count,
                #'standings': standings,
                'recent_games': stadium.game_set.all()[:25],
                }

        return render(request, 
                      "places/stadium_detail.html",
                      context)
