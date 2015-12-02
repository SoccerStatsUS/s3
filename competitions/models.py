from django.db import models
from django.template.defaultfilters import slugify




AbstractCompetition = models.Model

"""
class AbstractCompetition(models.Model):

    # Anything that has a standing_set and a game_set 
    # mostly competitions and seasons.
"""






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

    class Meta:
        ordering = ("name",)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.abbreviation:
            self.abbreviation = self.make_abbreviation()
            
        super(Competition, self).save(*args, **kwargs)


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

    #objects = SeasonManager()

    minutes = models.IntegerField(null=True, blank=True)
    minutes_with_age = models.IntegerField(null=True, blank=True)
    age_minutes = models.FloatField(null=True, blank=True)

    super_season = models.ForeignKey(SuperSeason, null=False)


    class Meta:
        #ordering = ("order", "name", "competition")
        ordering = ("order", "super_season__order2", "competition")
        #ordering = ("super_season", )

