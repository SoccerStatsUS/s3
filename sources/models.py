from django.db import models



class Source(models.Model):
    """
    A source is usually a book or url.
    Or something.
    """

    name = models.CharField(max_length=1023)
    author = models.CharField(max_length=1023)
    #base_url = models.CharField(max_length=1023) 

    # Secondary data.
    games = models.IntegerField(null=True)
    stats = models.IntegerField(null=True)
    total = models.IntegerField(null=True)

    #objects = SourceManager()


    class Meta:
        ordering = ('name',)


    def __str__(self):
        return self.name


class SourceUrl(models.Model):
    
    source = models.ForeignKey(Source)
    url = models.CharField(max_length=1023)
