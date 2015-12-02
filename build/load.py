import datetime
import os
import sys
import pymongo

from collections import defaultdict

#from utils import insert_sql, timer

os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'
import django
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.template.defaultfilters import slugify



connection = pymongo.Connection()
soccer_db = connection.soccer

from bios.models import Bio
from competitions.models import Competition, CompetitionRelationship, SuperSeason, Season
from organizations.models import Confederation
from places.models import Country, State, City, Stadium
from sources.models import Source, SourceUrl
from teams.models import Team, TeamAlias

from getters import *


def load1():

    # Watch out for contingencies here.
    # Places depend only on other places.
    # Bio depends on places.
    # Stadium depends on places and bios.
    # Teams depends on places
    # Standings depends on Bio, Team, Competition, and Season
    # Games depends on Team, Stadium, City, Bio.
    # etc.

    # Georgraphical data.
    #load_geo()


    generate_mongo_indexes()

    # Non-game data.
    load_sources()
    load_confederations()
    load_places()


    # Simple sport data

    load_competitions()
    load_seasons()
    load_teams()
    load_stadiums()
    load_bios()


    #load_salaries()




def generate_mongo_indexes():
    """
    """
    # Not sure why I need to do this, but it seems necessary.

    soccer_db.games.ensure_index("date")


def load_sources():

    sources = defaultdict(dict)
    source_urls = defaultdict(list)
    
    for source in soccer_db.sources.find():
        source.pop('_id')

        d = sources[source['name']]
        d['name'] = source['name']

        if source['author']:
            d['author'] = source['author']

        if source.get('base_url'):
            source_urls[source['name']].append(source['base_url'])

    source_ids = {}

    for source in sources.values():
        s = Source.objects.create(**source)
        source_ids[s.name] = s.id

    for name, surls in source_urls.items():
        sid = source_ids[name]
        for surl in surls:
            SourceUrl.objects.create(**{
                    'source_id': sid,
                    'url': surl,
                    })
        


@transaction.atomic
def load_confederations():
    for cc in soccer_db.confederations.find():
        cc.pop('_id')
        cc['slug'] = slugify(cc['name'])
        Confederation.objects.create(**cc)



def load_places():

    # Load countries
    for country in soccer_db.countries.find():
        country.pop('_id')
        country['slug'] = slugify(country['name'])
        
        try:
            country['confederation'] = Confederation.objects.get(name=country['confederation'])
        except:
            import pdb; pdb.set_trace()

        country['subconfederation'] = country['subconfederation'] or ''
        Country.objects.create(**country)

    # Load states
    for state in soccer_db.states.find():
        state.pop('_id')
        state['country'] = Country.objects.get(name=state['country'])
        state['slug'] = slugify(state['name'])
        State.objects.create(**state)


    # Load cities
    cg = make_city_pre_getter()
    city_set = set()

    for city in soccer_db.cities.find():
        c = cg(city['name'])

        if c['state']:
            c['state'] = State.objects.get(name=c['state'])


        if c['country']:
            c['country'] = Country.objects.get(name=c['country'])

        # Create slugs
        if c['state']:
            slug = "{} {}".format(c['name'], c['state'].abbreviation)

        elif c['country']:
            slug = "{} {}".format(c['name'], c['country'])

        else:
            slug = c['name']

        c['slug'] = slugify(slug)

        city_set.add(tuple(sorted(c.items())))

    for e in city_set:
        City.objects.create(**dict(e))





@transaction.atomic
def load_competitions():


    print("loading competitions")
    for c in soccer_db.competitions.find():
        c.pop('_id')
        Competition.objects.create(**c)

    for d in soccer_db.competition_relations.find():
        try:
            b = Competition.objects.get(name=d['before'])
        except:
            import pdb; pdb.set_trace()

        a = Competition.objects.get(name=d['after'])
        CompetitionRelationship.objects.create(before=b, after=a)




@transaction.atomic
def load_seasons():
    print("loading seasons")
    # This appears to just be loading superseasons...

    #competition_getter = make_competition_getter()

    l = []

    for s in soccer_db.seasons.find():
        #s.pop('_id')
        #competition_id = competition_getter(s['competition'])
        l.append({
                'name': s['name'],
                'slug': slugify(s['name']),
                #'slug': slugify(s['season']),
                #'competition_id': competition_id,
                'order': s['order'],
                'order2': s['order2'],
                })

    for ss in l:
        SuperSeason.objects.create(**ss)





#@timer
@transaction.atomic
def load_teams():
    print("loading {} teams".format(soccer_db.teams.count()))

    cg = make_city_getter()
    names = set()

    for team in soccer_db.teams.find():
        team.pop('_id')

        founded = city = dissolved =None

        slug = slugify(team['name'])
        short_name = team.get('short_name') or team['name']

        if type(team['founded']) == int:
            try:
                founded = datetime.datetime(team['founded'], 1, 1)
            except:
                print("founded out of range %s" % team)

        if team['city']:
            city = cg(team['city'])

        if type(team['dissolved']) == int:
            dissolved = datetime.datetime(team['dissolved'] + 1, 1, 1)
            dissolved = dissolved - datetime.timedelta(days=1)

        if team['name'] not in names:

            if team['name'] == 'New York Giants':
                import pdb; pdb.set_trace()

            names.add(team['name'])
            Team.objects.create(**{
                    'name': team['name'],
                    'short_name': short_name,
                    'slug': slug,
                    'founded': founded,
                    'dissolved': dissolved,
                    'city': city,
                    'international': team.get('international', False),
                    })
        else:
            print("duplicate team name")
            print(team)


    for alias in soccer_db.name_maps.find():
        alias.pop('_id')
        t = Team.objects.find(name=alias['from_name'], create=True)

        TeamAlias.objects.create(**{
                'team': t,
                'name': alias['to_name'],
                'start': alias['start'],
                'end': alias['end'],
                })




#@timer
@transaction.atomic
def load_stadiums():
    print("loading stadiums")

    cg = make_city_getter()

    for stadium in soccer_db.stadiums.find():
        stadium.pop('_id')

        stadium['slug'] = slugify(stadium['name'])

        stadium['city'] = cg(stadium['location'])
        
        if 'renovations' in stadium:
            stadium.pop('renovations')
        if 'source' in stadium:
            stadium.pop('source')
        
        if stadium['architect']:
            stadium['architect'] = Bio.objects.find(stadium['architect'])

        if 'opened' in stadium and type(stadium['opened']) == int:
            stadium['year_opened'] = stadium.pop('opened')

        if 'closed' in stadium and type(stadium['closed']) == int:
            stadium['year_closed'] = stadium.pop('closed')

        try:
            Stadium.objects.create(**stadium)
        except:
            import pdb; pdb.set_trace()
        x = 5
        



#@timer
@transaction.atomic
def load_bios():
    print("loading bios")

    cg = make_city_getter()


    # Find which names are used so we can only load these bios.
    # Huh? This is unnecessary.
    #fields = [('lineups', 'name'), ('goals', 'goal'), ('stats', 'name'), ('awards', 'recipient'), ('picks', 'text')]
    #names = set()

    # Add names to names field where they have been used.
    #for coll, key in fields:
    #    names.update([e[key] for e in soccer_db[coll].find()])

    # Load bios.
    for bio in soccer_db.bios.find().sort('name', 1):

        #if bio['name'] not in names:
            #print("Skipping %s" % bio['name'])
        #    continue

        bio.pop('_id')

        if not bio['name']:
            import pdb; pdb.set_trace()
            print("NO BIO: %s" % str(bio))
            continue

        # nationality should be many-to-many
        if 'nationality' in bio:
            bio.pop('nationality')

        bd = {}

        for key in 'name', 'height', 'birthdate', 'height', 'weight':
            if key in bio:
                bd[key] = bio[key] or None

        if bio.get('birthplace'):
            bd['birthplace'] = cg(bio['birthplace'])

        if bio.get('deathplace'):
            bd['deathplace'] = cg(bio['deathplace'])

        """
        # Having unexpected problems here...
        bd['hall_of_fame'] = bio.get('hall_of_fame')
        if bd['hall_of_fame'] not in (True, False):
            bd['hall_of_fame'] = False
        """

        Bio.objects.create(**bd)

    bio_getter = make_bio_getter()
    bio_ct_id = ContentType.objects.get(app_label='bios', model='bio').id

    """
    images = []
    for bio in soccer_db.bios.find().sort('name', 1):
        if bio.get('img'):
            bid = bio_getter(bio['name'])
            fn = bio['img'].rsplit('/')[-1]
            
            images.append({
                    'filename': fn,
                    'content_type_id': bio_ct_id,
                    'object_id': bid,
                    })

    insert_sql("images_image", images)
    """




if __name__ == "__main__":
    if sys.argv[1] == '1':
        load1()
    elif sys.argv[1] == '2':
        load2()
    elif sys.argv[1] == '3':
        load3()
    elif sys.argv[1] == '4':
        load4()
    elif sys.argv[1] == '5':
        update()

    else:
        raise

