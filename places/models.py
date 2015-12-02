from django.db import models
from django.template.defaultfilters import slugify

from organizations.models import Confederation
from bios.models import Bio




class CountryManager(models.Manager):

    def find(self, s):

        try:
            return Country.objects.get(name=s)
        except:
            return Country.objects.create(name=s)


    def country_dict(self):
        """
        A dict mapping a team's name and short name to an id.
        """
        d = {}
        for e in self.get_queryset():
            d[e.name] = e.id
        return d

    def id_dict(self):
        """
        A dict mapping a team's name and short name to an id.
        """
        d = {}
        for e in self.get_queryset():
            d[e.id] = e.name
        return d



class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    #population = models.IntegerField(null=True)
    code = models.CharField(max_length=15)

    #confederation = models.CharField(max_length=15)
    confederation = models.ForeignKey(Confederation, null=True)

    subconfederation = models.CharField(max_length=15)

    objects = CountryManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)



class State(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    abbreviation = models.CharField(max_length=5)
    country = models.ForeignKey(Country, null=True, blank=True)
    joined = models.DateField(null=True)



class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    slug = models.SlugField(max_length=100)



class StadiumManager(models.Manager):

    def as_dict(self):
        """
        Dict mapping names to stadium id's.
        """
        d = {}
        for e in self.get_queryset():
            d[e.name] = e.id
        return d


    def find(self, name, create=True):
        """
        Given a team name, determine the actual team.
        """
        # Not here?
        if name == '':
            import pdb; pdb.set_trace()
        
        stadiums = Stadium.objects.filter(name=name)
        if stadiums:
            return stadiums[0]
        else:
            slug = slugify(name)
            return Stadium.objects.create(name=name, slug=slug)




class Stadium(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False, max_length=100)
    
    short_name = models.CharField(max_length=255)

    address = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    city = models.ForeignKey(City, null=True, blank=True)
    #location = models.PointField()

    opened = models.DateField(null=True)
    year_opened = models.IntegerField(null=True)

    closed = models.DateField(null=True)
    year_closed = models.IntegerField(null=True)
    
    architect = models.ForeignKey(Bio, null=True)

    capacity = models.IntegerField(null=True)

    width = models.CharField(max_length=255)
    length = models.CharField(max_length=255)
    measure = models.CharField(max_length=255)

    cost = models.DecimalField(max_digits=31, decimal_places=2, null=True)
    denomination = models.CharField(max_length=255)

    notes = models.CharField(max_length=255)
    

    objects = StadiumManager()    

    def __str__(self):
        return self.name


