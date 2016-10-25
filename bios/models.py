from django.db import models
from django.template.defaultfilters import slugify


class BioManager(models.Manager):

    def born_on(self, month, day):
        """
        Returns a random person born on this day.
        """
        # Should split into two methods.
        b = self.get_queryset().filter(birthdate__month=month, birthdate__day=day)
        if b:
            c = b.count()
            i = random.randint(0, c-1)
            return b[i]
        else:
            return None
        
        

    def bio_dict(self):
        """
        Dict mapping names to bio id's.
        """
        d = {}
        for name, eid in self.get_queryset().values_list('name', 'id'):
            d[name] = eid
        return d

    def bio_dictx(self):
        """
        Dict mapping names to bio id's.
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
        
        bios = Bio.objects.filter(name=name)
        if bios:
            return bios[0]
        else:
            #return Bio.objects.create(name=name, hall_of_fame=False)
            return Bio.objects.create(name=name)


    def duplicate_slugs(self):
        """
        Returns all bios with duplicate slugs.
        """
        # Used to find problem bios.
        d = defaultdict(list)
        for e in self.get_queryset():
            d[e.slug].append(e.name)
        return [k for (k, v) in d.items() if len(v) > 1]


    def reverse_names(self):
        """
        Returns all bios with duplicate slugs.
        """

        # Do this in pairs.

        #def rv(s):
        #    first, last = s.split(' ', 1)
        #    return "%s %s" % (last, first)

        regular_names = set(self.get_queryset().values_list('name', flat=True))

        reversed_names = set()
        for e in self.get_queryset().filter(name__contains=' ').values_list('name', flat=True):
            reversed_names.add(s)

        tmp = regular_names.intersection(reversed_names)
        final = set()

    def id_to_slug(self, pid):
        return Bio.objects.get(id=pid).slug

    # id_to_slug = lru_cache(id_to_slug, {}, 2)


class Bio(models.Model):

    """
    Player or anybody else bio.
    """
    
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, unique=False)

    height = models.IntegerField(null=True, blank=True)

    birthdate = models.DateField(null=True, blank=True)
    birthplace = models.ForeignKey('places.City', null=True, blank=True, related_name='birth_set')
    birth_country = models.ForeignKey('places.Country', null=True, blank=True, related_name='citizen_set')

    deathdate = models.DateField(null=True, blank=True)
    deathplace = models.ForeignKey('places.City', null=True, blank=True, related_name='death_set')


    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

    # these should be a many-to-many associated with specific dates.
    #hometown = models.ForeignKey('places.City', null=True, blank=True, related_name='birth_set') 
    #position = models.ForeignKey('positions.Position', null=True, blank=True, related_name='birth_set') 
    #position = models.CharField('positions.Position', null=True, blank=True, related_name='birth_set') 

    # what is this??
    #awards = generic.GenericRelation('awards.AwardItem')
    #images = generic.GenericRelation('images.Image')



    objects = BioManager()


    class Meta:
        pass
        #ordering = ('name',)


    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        # Is this a good idea?
        if not self.slug:
            self.slug = slugify(self.name)
            
        super(Bio, self).save(*args, **kwargs)



    def career_stat(self):
        """
        Summary stats for a player's entire career.
        """
        from stats.models import CareerStat

        try:
            return CareerStat.objects.get(player=self)
        except:
            return None

    def competition_stats(self):
        """
        Summary stats for a player in a given competition (e.g. MLS)
        """
        from stats.models import CompetitionStat

        return CompetitionStat.objects.filter(player=self)

    def team_stats(self):
        """
        Summary stats for a player in a given competition (e.g. MLS)
        """
        from stats.models import TeamStat

        return TeamStat.objects.filter(player=self)

