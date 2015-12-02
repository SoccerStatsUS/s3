from django.db import models

from organizations.models import Confederation


class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    #population = models.IntegerField(null=True)
    code = models.CharField(max_length=15)

    #confederation = models.CharField(max_length=15)
    confederation = models.ForeignKey(Confederation, null=True)

    subconfederation = models.CharField(max_length=15)


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

