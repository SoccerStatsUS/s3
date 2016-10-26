from django.db import models

from bios.models import Bio
from games.models import Game
from teams.models import Team

# events: fouls (red, yellow), shots (goals, saves), appearances (subs, starts), passes (assists, turnovers, linked-list), 


class EventManager(models.Manager):
    pass


class Event(models.Model):

    game = models.ForeignKey(Game, null=True)

    team = models.ForeignKey(Team, null=True)
    minute = models.IntegerField(null=True)    

    etype = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    subject = models.ForeignKey(Bio, related_name="event_committed")
    object = models.ForeignKey(Bio, related_name="event_against", null=True)


    objects = EventManager()    
