import datetime

from django.db import models
from django.template.defaultfilters import slugify

from places.models import City



class AbstractTeamManager(models.Manager):
    """
    An abstract Team Manager.
    """

    def recent_games(self, delta=datetime.timedelta(days=100)):
        """
        Returns a queryset of games played within a given timedelta.
        """
        since = datetime.date.today() - delta
        return self.get_queryset().filter(date__gte=since)

    def team_dict(self):
        """
        A dict mapping a team's name and short name to an id.
        """
        d = {}
        for e in self.get_queryset():
            d[e.name] = e.id
            d[e.short_name] = e.id
        return d

    def duplicate_slugs(self):
        """
        Returns all teams with duplicate slugs.
        """
        # Used to find problem teams.
        d = defaultdict(list)
        for e in self.get_queryset():
            d[e.slug].append(e.name)
        return [(k, v) for (k, v) in d.items() if len(v) > 1]

            
    def find(self, name, create=False):
        """
        Given a team name, determine the actual team.
        """
        # This seems to duplicate alias functionality that is implemented in soccerdata.
        # Also, this looks a lot more time-consuming.

        #from soccer.teams.aliases import mapping
        teams = Team.objects.filter(name=name)
        if teams:
            return teams[0]

        teams = Team.objects.filter(short_name=name)
        if teams:
            return teams[0]

        if create:

            try:
                print("Creating team {}".format(name))
            except:
                print("Created a team.")

            team = Team.objects.create(
                name=name, 
                short_name=name, 
                )
            return team
        else:
            # Don't want to be creating teams all the time.
            raise



class TeamManager(AbstractTeamManager):
    """
    Normal Team Manager used for Team.objects.
    """


class Team(models.Model):
    """
    A collection of players for a competition.
    """
    # Squads for, e.g. Champions League, World Cup?
    # Rolling roster for any team.
    # retirements.


    name = models.CharField(max_length=200, unique=True)

    # Affiliate team. e.g.
    # Portland Timbers Reserves -> Portland Timbers (reserve -> main)
    # Chicago Fire Select -> Chicago Fire (? affiliation)
    # United States -> United States U-20 (youth team)
    affiliate = models.ForeignKey('self', null=True)

    # Let's get rid of short name! It's really just another alias.
    # No way, it's useful when you want to display a better name.
    # Let's just be clear that it's very optional.
    short_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=100, unique=False)

    founded = models.DateField(null=True)
    dissolved = models.DateField(null=True)

    city = models.ForeignKey(City, null=True, blank=True)
    #city = models.CharField(max_length=255)

    # Have some virtual teams from USMNT drafts.
    real = models.BooleanField(default=True)
    defunct = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    international = models.BooleanField(default=False)

    objects = TeamManager()
    #defuncts = DefunctTeamManager()
    #reals = RealTeamManager()

    #awards = generic.GenericRelation('awards.AwardItem')


    class Meta:
        ordering = ('short_name',)

    def __str__(self):
        return self.short_name


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.short_name)
            
        super(Team, self).save(*args, **kwargs)



    def game_set(self):
        from games.models import Game
        return Game.objects.filter(models.Q(team1=self) | models.Q(team2=self))






class TeamAlias(models.Model):        
    team = models.ForeignKey(Team)
    name = models.CharField(max_length=200, unique=True)
    
    start = models.DateField()
    end = models.DateField()

    class Meta:
        ordering = ('start',)


    def start_text(self):
        if self.start.month == 1 and self.start.day == 1:
            return self.start.year
        else:
            return self.start
    

    def end_text(self):
        if self.end.month == 12 and self.end.day == 31:
            return self.end.year
        else:
            return self.end
    
