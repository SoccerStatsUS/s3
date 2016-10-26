from collections import defaultdict, OrderedDict, Counter

from django.shortcuts import render, get_object_or_404

from .models import Event

from teams.models import Team

#@cache_page(60 * 60 * 12)
def event_index(request):
    """
    Teams shown by letter.
    """
    # This is not good but not sure how to fix.
    # Need to broaden team standing generation so we use that
    # to pull all teams.
    
    events = Event.objects.order_by('-game__date').select_related()

    context = {
        'events': events,
        }

    return render(request, 
                  "events/index.html",
                  context)



def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {
        'event': event,
        }
    return render(request, 
                              "events/detail.html",
                              context)
