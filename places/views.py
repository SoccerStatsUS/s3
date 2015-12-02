from django.shortcuts import render

from django.http import HttpResponse

from .models import Country



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
        births = Bio.objects.filter(birthplace__country=country).order_by('birthdate')
        competitions = Competition.objects.filter(scope='Country', area=country.name)
        cities = City.objects.filter(country=country)

        context = {
                'country': country,
                'births': births,
                'stadiums': stadiums,
                'competitions': competitions,
                'cities': cities,
                }
        return render_to_response("places/country_detail.html",
                                  context,
                                  context_instance=RequestContext(request))

