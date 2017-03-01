import datetime
import os
import sys
import pymongo

from collections import defaultdict

from utils import insert_sql, timer

os.environ['DJANGO_SETTINGS_MODULE'] = 'build_settings'
import django
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.template.defaultfilters import slugify



# connection = pymongo.Connection()
connection = pymongo.MongoClient()
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

    load_drafts()
    load_transactions()

    #load_salaries()

    # Complex game data
    load_games()

    load_events()


def load3():
    load_game_stats()



def load4():
    #load_news();
    # Consider loading stats last so that we can generate 
    load_stats()
    #print hpy().heap()

    # Analysis data







def generate_mongo_indexes():
    """
    """
    # Not sure why I need to do this, but it seems necessary.

    soccer_db.games.ensure_index("date")



def load_events():
    """
    Load generic events.
    """
    # shots (including goals), fouls (including cards), substitutions, corner kicks, throw ins
    # passes and tackles would be the ultimate extension here.

    #load_substitutions()

    load_fouls()

    load_goals()
    load_assists()



@timer
@transaction.atomic
def load_drafts():
    print("\nloading drafts\n")

    competition_getter = make_competition_getter()
    season_getter = make_season_getter()

    team_getter = make_team_getter()

    # Create the set of drafts.

    """
    for draft in soccer_db.drafts.find().sort('team', 1):
        draft.pop('_id')

        if draft['competition']:
            competition_id = competition_getter(draft['competition'])        
        else:
            competition_id = None

        season_id = season_getter(draft['season'], competition_id)

        Draft.objects.create(**{
                'name': draft['name'],
                'season_id': season_id,
                'competition_id': competition_id,
                'start': draft.get('start'),
                'end': draft.get('end'),
                })
    """

    print("\nloading {} picks\n".format(soccer_db.picks.count()))

    #import pdb; pdb.set_trace()

    # Create picks
    picks = []
    for pick in soccer_db.picks.find():

        # draft, text, player, position, team

        c = pick.get('competition')
        if c:
            competition_id = competition_getter(pick.get('competition'))
        else:
            competition_id = None

        season_id = season_getter(pick.get('season'), competition_id)

        #draft = Draft.objects.get(name=pick.get('draft'), competition_id=competition_id, season_id=season_id)
        draft = None

        if pick['team'] == 'Sean_Irish_LAGalaxy/Geneva':
            pass #import pdb; pdb.set_trace()


        team_id = team_getter(pick['team'])

        if pick.get('former_team'):
            former_team_id = team_getter(pick['former_team'])
        else:
            former_team_id = None

        # Set the player reference.
        text = pick['text']

        # Draft picks were "drafted" in the MLS Allocation and Dispersal drafts.
        if "SuperDraft" in text:
            player_id = None
        elif text.lower() == 'pass':
            player_id = None
        else:
            player_id = Bio.objects.find(text).id

        """
        picks.append({
                #'draft_id': draft.id,
                'player_id': player_id,
                'team_id': team_id,
                'text': text,
                'position': pick.get('position') or '',
                'former_team_id': former_team_id,
                'number': pick['number'],
                })
        """

        picks.append({
            #'draft_id': draft.id,
            'ttype': 'draft pick',
            'date': pick['date'],
            'person_id': player_id,
            'team_to_id': team_id,
            'team_from_id': former_team_id,

            #'text': text,
            #'position': pick.get('position') or '',
            #'number': pick['number'],
                })


    #insert_sql("drafts_pick", list(picks))
    insert_sql("transactions_transaction", list(picks))



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
        




def load_transactions():

    print("loading {} transactions".format(soccer_db.transactions.count()))

    transactions = []

    for t in soccer_db.transactions.find():
        try:
            t.pop('_id')

            if t.get('team_from'):
                team_from = Team.objects.find(t['team_from'], create=True)
                team_from_id = team_from.id
            else:
                team_from_id= None

            if t.get('team_to'):
                team_to = Team.objects.find(t['team_to'], create=True)
                team_to_id = team_to.id
            else:
                team_to_id = None

            person = Bio.objects.find(t['person'])

            transactions.append({
                'ttype': t['ttype'],
                'person_id': person.id,
                'team_to_id': team_to_id,
                'team_from_id': team_from_id,
                'date': t['date'],
                })
        except:
            import pdb; pdb.set_trace()

    insert_sql("transactions_transaction", transactions)



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
        if slug =='':
            import pdb; pdb.set_trace()

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

        #import pdb; pdb.set_trace()

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

        if bio.get('name') == 'Mauro Diaz':
            import pdb; pdb.set_trace()
        x = 5

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




#@timer
@transaction.atomic
def load_games():
    print("\n loading {} games\n".format(soccer_db.games.count()))

    stadium_getter = make_stadium_getter()
    team_getter = make_team_getter()
    competition_getter = make_competition_getter()    
    source_getter = make_source_getter()
    bio_getter = make_bio_getter()

    city_getter = make_city_getter()
    country_getter = make_country_getter()

    season_getter = make_season_getter()

    games = []
    game_sources = []

    for game in soccer_db.games.find().sort('date', 1):

        if game.get('city') == 'Columbus Crew Stadium':
            import pdb; pdb.set_trace()

        # Apply stadium / state / country information.

        stadium_id = city_id = country_id = None
        if game.get('stadium'):

            
            stadium_id = stadium_getter(game['stadium'])
            s = Stadium.objects.get(id=stadium_id)
            if s.city:
                city_id = s.city.id
            else:
                city_id = None

        elif game.get('city'):
            city_id = city_getter(game['city']).id

        elif game.get('location'):

            country_id = country_getter(game['location'])
            if country_id is None:
                city_id = city_getter(game['location']).id

        competition_id = competition_getter(game['competition'])
        #game['competition'] = Competition.objects.get(id=game['competition'])

        #season_id = Season.objects.find(game['season'], competition_id).id # this!!
        season_id = season_getter(game['season'], competition_id)

        if game['season'] is None:
            import pdb; pdb.set_trace()

        team1_id = team_getter(game['team1'])
        team2_id = team_getter(game['team2'])

        home_team_id = None
        if game.get('home_team'):
            home_team_id = team_getter(game['home_team'])

        goals = (game['team1_score'] or 0) + (game['team2_score'] or 0)

        referee_id = linesman1_id = linesman2_id = linesman3_id = None
        if game['referee']:
            referee_id = bio_getter(game['referee'])

        if game.get('linesman1'):
            linesman1_id = bio_getter(game['linesman1'])

        if game.get('linesman2'):
            linesman2_id = bio_getter(game['linesman2'])

        if game.get('linesman3'):
            linesman3_id = bio_getter(game['linesman3'])


        if game.get('sources'):
            sources = sorted(set(game.get('sources')))
        elif game.get('source'):
            sources = [game['source']]
        else:
            sources = []

        
        for source in sources:
            if source.strip() == '':
                continue
            elif source.startswith('http'):
                source_url = source
            else:
                source_url = ''
            source_id = source_getter(source)
            t = (game['date'], team1_id, source_id, source_url)
            game_sources.append(t)

        result_unknown = game.get('result_unknown') or False
        not_played = game.get('not_played') or False
        forfeit = game.get('forfeit') or False
        minigame = game.get('minigame') or False
        indoor = game.get('indoor') or False

        minutes = game.get('minutes') or 90

        neutral = game.get('neutral') or False
        attendance = game.get('attendance')

        stage = game.get('stage') or ''
        group = game.get('group') or ''
        rnd = game.get('round') or ''


        # There are lots of problems with the NASL games, 
        # And probably ASL as well. Need to spend a couple
        # of hours repairing those schedules.

        if game['shootout_winner']:
            shootout_winner = team_getter(game['shootout_winner'])
        else:
            shootout_winner = None

        location = game.get('location', '')

        location = location or ''


        if 'gid' not in game:
            game['gid'] = get_id_by_time()


        games.append({
                'date': game['date'],
                'has_date': bool(game['date']),

                'team1_id': team1_id,
                'team1_original_name': game['team1_original_name'],
                'team2_id': team2_id,
                'team2_original_name': game['team2_original_name'],

                'team1_score': game['team1_score'],
                'official_team1_score': game.get('official_team1_score'),
                'team2_score': game['team2_score'],
                'official_team2_score': game.get('official_team2_score'),

                'shootout_winner_id': shootout_winner,

                'team1_result': game['team1_result'],
                'team2_result': game['team2_result'],

                'result_unknown': result_unknown,
                'not_played': not_played,
                'forfeit': forfeit,

                'goals': goals,
                'minigame': minigame,
                'indoor': indoor,

                'minutes': minutes,
                'competition_id': competition_id,
                'season_id': season_id,
                'stage': stage,
                'group': group,
                'round': rnd,


                'home_team_id': home_team_id,
                'neutral': neutral,

                'stadium_id': stadium_id,
                'city_id': city_id,
                'country_id': country_id,
                'location': location,
                'notes': game.get('notes', ''),
                'video': game.get('video', ''),
                'attendance': attendance,
                
                'referee_id': referee_id,
                'linesman1_id': linesman1_id,
                'linesman2_id': linesman2_id,
                'linesman3_id': linesman3_id,

                'merges': game['merges'],
                'gid': game['gid'],
                })


    print("Inserting {} games results.".format(len(games)))
    # Broke on massive attendance. 
    # Watch out for crazy integer values.
    insert_sql("games_game", games)

    print("Inserting games sources.")
    game_getter = make_game_getter()
    
    l = []
    for date, team_id, source_id, source_url in game_sources:

        # Don't call game_getter without date. Need to give games unique id's.
        if date:
            game_id = game_getter(team_id, date)
            if game_id:
                l.append({
                        'game_id': game_id,
                        'source_id': source_id,
                        'source_url': source_url,
                        })

    insert_sql("games_gamesource", l)




#@timer
@transaction.atomic
def load_stats():
    print("\nloading stats\n")

    @timer
    def f():
        return 


    team_getter, bio_getter, competition_getter, season_getter, source_getter = (
        make_team_getter(), make_bio_getter(), make_competition_getter(), make_season_getter(), make_source_getter(),)
                
    print("\nprocessing\n")

    l = []    
    i = 0
    # for i, stat in enumerate(soccer_db.stats.find(timeout=False)): # no timeout because this query takes forever.
    for i, stat in enumerate(soccer_db.stats.find(no_cursor_timeout=True)):


        if i % 50000 == 0:
            print(i)

        if stat['name'] == '':
            #import pdb; pdb.set_trace()
            continue


        team_id = team_getter(stat['team'])
        bio_id = bio_getter(stat['name'])
        competition_id = competition_getter(stat['competition'])
        season_id = season_getter(stat['season'], competition_id)


        # cf game_sources stuff.
        """
        # change to sources!
        if stat.get('sources'): 
            sources = sorted(set(stat.get('sources')))
        elif stat.get('source'):
            sources = [stat['source']]
        else:
            sources = []

        for source in sources:
            if source.strip() == '':
                continue
            elif source.startswith('http'):
                source_url = source
            else:
                source_url = ''
            source_id = source_getter(source)
            #t = (game['date'], team1_id, source_id, source_url)
            #stat_sources.append(t)
        """

        if stat.get('source'):
            source_id = source_getter(stat['source'])

        else:
            source_id = None

        def c2i(key):
            # Coerce an integer

            if key in stat and stat[key] != None:
                if type(stat[key]) != int:
                    import pdb; pdb.set_trace()
                return stat[key]

            else:
                return None

        l.append({
            'player_id': bio_id,
            'team_id': team_id,
            'competition_id': competition_id,
            'season_id': season_id,
            'games_started': c2i('games_started'),
            'games_played': c2i('games_played'),
            'minutes': c2i('minutes'),
            'goals': c2i('goals'),
            'assists': c2i('assists'),
            'shots': c2i('shots'),
            'shots_on_goal': c2i('shots_on_goal'),
            'fouls_committed': c2i('fouls_committed'),
            'fouls_suffered': c2i('fouls_suffered'),
            'yellow_cards': c2i('yellow_cards'),
            'red_cards': c2i('red_cards'),
            'source_id': source_id,
            })

    print(i)

    insert_sql("stats_stat", l)


def load_fouls():

    print("loading fouls")
    print(soccer_db.fouls.count())



    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    game_getter = make_game_getter()
    gid_getter = make_gid_getter()

    l = []

    def create_foul(foul):
        
        if foul['team'] is None:
            return {}

        team_id = team_getter(foul['team'])

        bio_id = None

        bio_id = bio_getter(foul['name'])

        if foul['type'] == 'red':
            ftype = 'red'
        elif foul['type'] == 'yellow':
            ftype = 'yellow'
        else:
            import pdb; pdb.set_trace()

        if not foul['date']:
            return {}

        # Coerce to date to match dict.
        d = datetime.date(foul['date'].year, foul['date'].month, foul['date'].day)

        # Try gid first, fall back on team/date.
        game_id = None

        if 'gid' in foul:
            game_id = gid_getter(foul['gid'])

        if game_id is None:
            game_id = game_getter(team_id, d)

        if not game_id:
            print("Cannot create %s" % goal)
            return {}
        else:
            return {
                'game_id': game_id, 
                'team_id': team_id, 
                'minute': foul['minute'],
                
                'etype': ftype,
                #'team_original_name': '',

                'subject_id': bio_id, #player,

                'description': '',

                }

    i = 0 # if no goals.
    fouls = []
    for i, foul in enumerate(soccer_db.fouls.find()):
        if i % 50000 == 0:
            print(i)

        f = create_foul(foul)
        if f:
            fouls.append(f)

    insert_sql('events_event', fouls)


@timer
@transaction.atomic
def load_goals():
    print("\nloading goals\n")

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    game_getter = make_game_getter()
    gid_getter = make_gid_getter()

    l = []


    def create_goal(goal):

        team_id = team_getter(goal['team'])
        bio_id = ogbio_id = None

        if goal['goal']:
            bio_id = bio_getter(goal['goal'])

        if goal.get('own_goal_player'):
            ogbio_id = bio_getter(goal['own_goal_player'])


        # Tough to apply a goal without a date...
        if not goal['date']:
            return {}

        # Coerce to date to match dict.
        d = datetime.date(goal['date'].year, goal['date'].month, goal['date'].day)

        # Try gid first, fall back on team/date.
        game_id = None

        if 'gid' in goal:
            game_id = gid_getter(goal['gid'])

        if game_id is None:
            game_id = game_getter(team_id, d)

        if not game_id:
            print("Cannot create %s" % goal)
            return {}
        else:
            return {
                'date': goal['date'],
                'minute': goal['minute'],
                'team_id': team_id, 
                #'team_original_name': '',

                'player_id': bio_id, #player,
                'own_goal_player_id': ogbio_id,

                'game_id': game_id, 

                'own_goal': goal.get('own_goal', False),
                'penalty': goal.get('penalty', False),
                }

    i = 0 # if no goals.
    goals = []
    for i, goal in enumerate(soccer_db.goals.find()):
        if i % 50000 == 0:
            print(i)

        g = create_goal(goal)
        if g:
            goals.append(g)

    print(i)
    insert_sql('goals_goal', goals)

    events = []

    for goal in goals:
        event = {
            'game_id': goal['game_id'],
            'team_id': goal['team_id'],
            'minute': goal['minute'],
            'etype': 'goal',
            'subject_id': goal['player_id'],
            'object_id': None, 
            'description': '',
        }
        if goal['player_id']:
            events.append(event)


    insert_sql('events_event', events)

        
@timer
@transaction.atomic
def load_assists():
    print("\nloading assists\n")

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    goal_getter = make_goal_getter()

    def create_assists(goal):

        #if goal['competition'] == 'Major League Soccer'  and goal['season'] == '1996':
        #    import pdb; pdb.set_trace()
        


        if not goal['assists']:
            return []

        if goal['assists'] == ['']:
            return []



        team_id = team_getter(goal['team'])
        bio_id = ogbio_id = None

        if goal['goal']:
            bio_id = bio_getter(goal['goal'])


        if not goal['date']:
            return {}

        d = datetime.date(goal['date'].year, goal['date'].month, goal['date'].day)

        goal_id = goal_getter(team_id, bio_id, goal['minute'], d)
        if not goal_id:
            #import pdb; pdb.set_trace()
            print("Cannot create assists for %s" % goal)
            return []

        seen = set()

        for assister in goal['assists']:
            assist_ids = [bio_getter(e) for e in goal['assists']]
            for i, assist_id in enumerate(assist_ids, start=1):
                if assist_id and assist_id not in seen:
                    seen.add(assist_id)
                    assists.append({
                        'player_id': assist_id,
                        'goal_id': goal_id,
                        'order': i,
                        })

    assists = []

    i = 0
    for i, goal in enumerate(soccer_db.goals.find()):
        if i % 50000 == 0:
            print(i)
        create_assists(goal)

    print(i)
    print(len(assists))
    insert_sql('goals_assist', assists)



#@timer
@transaction.atomic
def load_game_stats():
    print("\nloading game stats\n")

    team_getter = make_team_getter()
    bio_getter = make_bio_getter()
    source_getter = make_source_getter()
    game_getter = make_game_getter()
    gid_getter = make_gid_getter()
    game_result_getter = make_game_result_getter()

    birthdate_dict = dict(Bio.objects.exclude(birthdate=None).values_list("id", "birthdate"))
    
    print("\nprocessing")

    l = []    
    i = 0
    #for i, stat in enumerate(soccer_db.gstats.find(timeout=False)): # no timeout because this query takes forever.
    for i, stat in enumerate(soccer_db.gstats.find(no_cursor_timeout=True)):        
        if i % 50000 == 0:
            print(i)

        if stat['player'] == '':
            #import pdb; pdb.set_trace()
            continue

        
        try:
            bio_id = bio_getter(stat['player'])
        except:
            continue

        if bio_id is None:
            continue


        bd = birthdate_dict.get(bio_id)
        if stat['date'] and bd:
            # Coerce bd from datetime.date to datetime.time
            bdt = datetime.datetime.combine(bd, datetime.time())
            age = (stat['date'] - bdt).days / 365.25
        else:
            age = None

        team_id = team_getter(stat['team'])


        if 'gid' in stat:
            game_id = gid_getter(stat['gid'])
        else:
            game_id = game_getter(team_id, stat['date'])

        #game_id = game_getter(team_id, stat['date'])


        result = game_result_getter(team_id, stat['date'])

        if game_id is None or team_id is None:
            continue


        def c2i(key, coerce_none=True):
            # Coerce an integer

            if key in stat and stat[key] != None:
                if type(stat[key]) != int:
                    import pdb; pdb.set_trace()
                return stat[key]

            elif key in stat and stat[key] == None:
                return 0

            else:
                return None

        l.append({
            'player_id': bio_id,
            'team_id': team_id,
            'game_id': game_id,
            'games_started': c2i('games_started'),
            'games_played': c2i('games_played'),
            'minutes': c2i('minutes'),
            'goals': c2i('goals'),
            'assists': c2i('assists'),
            'shots': c2i('shots'),
            'shots_on_goal': c2i('shots_on_goal'),
            'fouls_committed': c2i('fouls_committed'),
            'fouls_suffered': c2i('fouls_suffered'),
            'yellow_cards': c2i('yellow_cards'),
            'red_cards': c2i('red_cards'),
            'on': c2i('on', False),
            'off': c2i('off', False),
            'age': age,
            'result': result,
            })

    print(i)


    insert_sql("stats_gamestat", l)



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

