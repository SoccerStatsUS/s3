from django.db import models


class Bio(models.Model):

    """
    Player or anybody else bio.
    """
    
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, unique=False)

    height = models.IntegerField(null=True, blank=True)

    birthdate = models.DateField(null=True, blank=True)
    #birthplace = models.ForeignKey('places.City', null=True, blank=True, related_name='birth_set')
    #birth_country = models.ForeignKey('places.Country', null=True, blank=True, related_name='citizen_set')

    deathdate = models.DateField(null=True, blank=True)
    #deathplace = models.ForeignKey('places.City', null=True, blank=True, related_name='death_set')

    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

    #awards = generic.GenericRelation('awards.AwardItem')
    #images = generic.GenericRelation('images.Image')


