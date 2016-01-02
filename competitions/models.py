from django.db import models
from django.template.defaultfilters import slugify




AbstractCompetition = models.Model

"""
class AbstractCompetition(models.Model):

    # Anything that has a standing_set and a game_set 
    # mostly competitions and seasons.
"""



class CompetitionManager(models.Manager):

    def find(self, name):
        try:
            return Competition.objects.get(name=name)
        except:
            print("Creating competition {}".format(name))
            return Competition.objects.create(name=name)


    def as_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for e in self.get_queryset():
            d[e.name] = e.id
        return d






class Competition(AbstractCompetition):
    """
    A generic competition such as MLS Cup Playoffs, US Open Cup, or Friendly
    """
    # Should this be called Tournament? Probably not.

    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=15)
    
    slug = models.SlugField(max_length=150)

    international = models.BooleanField(default=False)
    ctype = models.CharField(max_length=255) # Competition type - cup, league, etc.
    code = models.CharField(max_length=255) # Code: soccer, indoor, Boston game, etc.
    level = models.IntegerField(null=True, blank=True) # 1st Divison, 2nd Vision, etc.
    scope = models.CharField(max_length=255)

    area = models.CharField(max_length=255)

    relationships = models.ManyToManyField('self',through='CompetitionRelationship',symmetrical=False)
    
    #international = models.BooleanField()

    objects = CompetitionManager()

    class Meta:
        ordering = ("name",)


    def __str__(self):
        return self.name



    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.abbreviation:
            self.abbreviation = self.make_abbreviation()
            
        super(Competition, self).save(*args, **kwargs)



    def make_abbreviation(self):
        
        if self.name is None:
            import pdb; pdb.set_trace()

        words = self.name.split(' ')
        first_letters = [e.strip()[0] for e in words if e.strip()]
        first_letters = [e for e in first_letters if e not in '-()']
        return "".join(first_letters)



class CompetitionRelationship(models.Model):
    before = models.ForeignKey('Competition', related_name='before')
    after = models.ForeignKey('Competition', related_name='after')




class SuperSeason(models.Model):
    """
    A larger version of season.
    eg 1996, 2004-2005
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    order = models.IntegerField()
    order2 = models.IntegerField()


    
    def previous(self):
        seasons = SuperSeason.objects.all()
        index = list(seasons).index(self)
        if index > 0:
            return seasons[index - 1]
        else:
            return None

    def next(self):
        seasons = SuperSeason.objects.all()
        index = list(seasons).index(self)
        next = index + 1
        if next < seasons.count():
            return seasons[next]
        else:
            return None




class SeasonManager(models.Manager):

    def find(self, name, competition):
        try:
            return Season.objects.get(name=name, competition=competition)
        except:
            #if type(competition) in (int, str, unicode):
            if type(competition) in (int, str):
                competition = Competition.objects.get(id=competition)
            
            try:
                ss = SuperSeason.objects.get(name=name)
            except:
                print("Creating Super Season %s" % name)
                if name in (None, ''):
                    import pdb; pdb.set_trace()
                ss = SuperSeason.objects.create(name=name, order=-1, order2=-1)

            return Season.objects.create(name=name, competition=competition, order=ss.order, super_season=ss)

    def as_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for name, competition, sid in self.get_queryset().values_list('name', 'competition', 'id'):
            d[(name, competition)] = sid
        return d




class Season(AbstractCompetition):
    """
    A season of a competition.
    """
    # Considering removing the competition dependency and making season refer to a given period of time.
    # A CompetitionSeason would then refer to a season/competition unit.

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    order = models.IntegerField(null=True, blank=True)
    order2 = models.IntegerField(null=True, blank=True)

    competition = models.ForeignKey(Competition, null=True)
    competition_original_name = models.CharField(max_length=255)

    objects = SeasonManager()

    minutes = models.IntegerField(null=True, blank=True)
    minutes_with_age = models.IntegerField(null=True, blank=True)
    age_minutes = models.FloatField(null=True, blank=True)

    super_season = models.ForeignKey(SuperSeason, null=False)


    class Meta:
        #ordering = ("order", "name", "competition")
        ordering = ("order", "super_season__order2", "competition")
        #ordering = ("super_season", )


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Season, self).save(*args, **kwargs)




    def previous_game(self, game):
        # This doesn't really work. 

        from games.models import Game

        if game.date is None:
            return None

        same_day_games = Game.objects.filter(season=self, date=game.date, id__lt=game.id).order_by('-id')
        if same_day_games.exists():
            return same_day_games[0]

        else:
            games = Game.objects.filter(season=self, date__lt=game.date).order_by('-date', '-id')
            if games.exists():
                return games[0]
            else:
                return None

    
    def next_game(self, game):
        from games.models import Game

        if game.date is None:
            return None

        same_day_games = Game.objects.filter(season=self, date=game.date, id__gt=game.id).order_by('id')
        if same_day_games.exists():
            return same_day_games[0]
        else:
            games = Game.objects.filter(season=self, date__gt=game.date).order_by('date', 'id')
            if games.exists():
                return games[0]
            else:
                return None



