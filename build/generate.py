
from django.db import transaction
from utils import insert_sql, timer

from competitions.models import Competition, Season
from stats.models import Stat, GameStat
from teams.models import Team


@timer
def generate():
    print("generating")
    generate_team_stats()
    generate_competition_stats()



@transaction.atomic
def generate_stats_generic(table, qs, make_key, update_dict):
    """
    Generate team, career, etc. stats.
    Maybe could improve this.
    """

    final_dict = {}
    excluded = ('player_id', 'team_id', 'competition_id', 'season_id', 'source_id') 

    for stat in qs.values():

        # Guard against unaddable values
        for k,v  in stat.items():
            if v in ('?', 'None', '-'):
                stat[k] = None

        # This determines what is filtered.
        # e.g., create all-time player stats with 
        # make_key = lambda s: s['player']
        key = make_key(stat) 
        # Create a new entry for this stat type
        if key not in final_dict:
            # This should set all necessary fields.
            final_dict[key] = stat
        else:
            d = final_dict[key]
            for key, value in stat.items():
                if key not in excluded: 
                    if not d[key]:
                        d[key] = value
                    else:
                        if value:
                            try:
                                d[key] += value
                            except:
                                import pdb; pdb.set_trace()
                                _ = 0


    for key, stat in final_dict.items():
        stat.pop('id')
        for e in update_dict.keys():
            if e in stat:
                stat.pop(e)


    insert_sql(table, list(final_dict.values()))

        
@timer
def generate_team_stats():
    print("generating team stats")
    for team in Team.objects.all():
        stats = Stat.objects.filter(team=team)
        make_key = lambda s: (s['player_id'], s['team_id'])
        update = {'competition_id': None, 'season_id': None }
        generate_stats_generic('stats_teamstat', stats, make_key, update)



@timer
def generate_competition_stats():
    print("generating competition stats")
    for competition in Competition.objects.all():
        stats = Stat.objects.filter(competition=competition)
        make_key = lambda s: (s['player_id'], s['competition_id'])
        update = {'team_id': None, 'season_id': None }
        generate_stats_generic('stats_competitionstat', stats, make_key, update)


                        
if __name__ == "__main__":
    generate()


