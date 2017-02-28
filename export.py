#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict


### Export game results to a text file.

def export_games(game_list):
    game_list = game_list.select_related()

    competitions = set([e.competition.name for e in game_list])
    seasons = set([e.season.name for e in game_list])

    # Check for rounds, groups, etc.


def format_date(dt):

    if dt is None:
        return ''
    else:
        # Do something about hours / minutes.
        return dt.strftime("%m/%d/%Y")

def export_game(g):
    date_string = format_date(g.date)
    

    attendance = g.attendance

    t1 = g.team1
    t2 = g.team2
    t1s = g.team1_score
    t2s = g.team2_score

    refs = get_referees(g)

    # Check for more.
    if g.stadium:
        location = g.stadium
    elif g.location:
        location = g.location
        

    s1 = "{}; {}; {}-{}; {}; {}; {}".format(date_string, t1, t1s, t2s, t2, location, refs)

    if g.attendance:
        s1 += "; {}".format(g.attendance)

    l = [s1,]

    if g.goal_set.exists():
        t1_goals = g.goal_set.filter(team=g.team1)
        t2_goals = g.goal_set.filter(team=g.team2)
        l.append(format_both_goals(t1_goals, t2_goals))

    if g.gamestat_set.exists():
        t1gs = g.gamestat_set.filter(team=t1)
        gss1 = format_gamestats(t1gs, t1)
        t2gs = g.gamestat_set.filter(team=t2)
        gss2 = format_gamestats(t2gs, t2)

        l.append(gss1)
        l.append(gss2)

    if False:
        format_misconduct(misconduct) # Fix this.

    for source in g.sources.all():
        # do something.
        # sources are surprisingly confusing.
        #l.append(s)
        pass

    return "\n".join(l)


def format_source(s):
    return 'Source: '

    


def format_goals(gs):
    if len(gs) == 0:
        return ''

    s = u''
    for goal in gs.order_by('minute'):
        if goal.own_goal:
            gs = u"Own goal ({})".format(goal.own_goal_player.name)
        else:
            gs = u"{} ({})".format(goal.player.name, goal.assist_string())

        if goal.minute:
            gs += " {}".format(goal.minute)

        s += gs
        s += ', '

    return s[:-2] # trim last 

def format_both_goals(g1, g2):
    return u"{}; {}".format(format_goals(g1), format_goals(g2))
    

def format_gamestats(gsx, team):
    ons = defaultdict(list)
    for gs in gsx:
        if gs.on != 0:
            ons[gs.on].append(gs.player.name)

    used = set()

    s = u'{}:'.format(team)
    for gs in gsx:
        if gs.off == 90:
            s += u' {},'.format(gs.player.name)
        else:
            options = ons[gs.off]
            for opt in options:
                if opt not in used:
                    used.add(opt)
                    s += u' {} ({} {}),'.format(gs.player.name, opt, gs.off)
                    break

    return s[:-1]
            
        
        
def format_misconduct(ms):
    return []


    
    

def get_referees(g):
    ref = g.referee
    a1 = g.linesman1
    a2 = g.linesman2
    a3 = g.linesman3

    if a1 == a2 == a3 == None:
        l = [ref]
    elif ref and a1 and a2 and a3:
        l =  [ref, a1, a2, a3]
    else:
        import pdb; pdb.set_trace()
        x = 5

    return ",".join([e.name for e in l])


    


