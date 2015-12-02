from django.db import models

from organizations.models import Confederation
from bios.models import Bio


class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    #population = models.IntegerField(null=True)
    code = models.CharField(max_length=15)

    #confederation = models.CharField(max_length=15)
    confederation = models.ForeignKey(Confederation, null=True)

    subconfederation = models.CharField(max_length=15)

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
