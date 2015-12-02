from django.db import models
from django.template.defaultfilters import slugify


class Competition(models.Model):
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
