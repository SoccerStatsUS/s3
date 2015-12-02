from django.db import models

from bios.models import Bio
from competitions.models import Competition, Season
from places.models import Country, State, City, Stadium
from sources.models import Source
from teams.models import Team



class GameManager(models.Manager):


    def games(self):
        l = [e['date'] for e in Game.objects.values("date").distinct()]
        return [e for e in l if e is not None]

    def game_years(self):
        return sorted(set([e.year for e in Game.objects.games()]))



    def with_lineups(self):
        from lineups.models import Appearance
        gids = [e[0] for e in set(Appearance.objects.values_list("game"))]
        return Game.objects.filter(id__in=gids)


    def all_blocks(self):
        """
        All date blocks for Beineke +/- analysis.
        """
        l = []
        for g in Game.objects.with_lineups().exclude(date__year=2007):
            print(g)
            l.extend(g.section_list())
        return l



    def on(self, month, day):
        """
        Return a random game from a given day.
        """
        # Split this into two functions.
        games = Game.objects.filter(date__month=month, date__day=day)
        if games:
            c = games.count()
            i = random.randint(0, c-1)
            return games[i]
        else:
            return None


    def id_dict(self):
        """
        Returns a dict mapping a team/date combination to a game id.
        """
        d = {}
        for eid, dt, t1, t2 in self.get_queryset().values_list('id', 'date', 'team1', 'team2'):
            key = (t1, dt)
            d[key] = eid
            key2 = (t2, dt)
            d[key2] = eid
        return d


class Game(models.Model):
    """
    Represents a completed game.
    """

    # Need both a date and a datetime field? Not sure.

    # This is used to uniquely identify games without dates, etc.
    gid = models.CharField(max_length=255)
    #gid = models.CharField(max_length=255, unique=True) # We got a duplicate, figure out why!


    # Organizational data
    round = models.CharField(max_length=255)
    group = models.CharField(max_length=255)
    stage = models.CharField(max_length=255)

    

    starter_count = models.IntegerField(null=True, blank=True)
    goal_count = models.IntegerField(null=True, blank=True)

    date = models.DateField(null=True)
    has_date = models.BooleanField()
    
    team1 = models.ForeignKey(Team, related_name='t1_games')
    team1_original_name = models.CharField(max_length=255)
    team2 = models.ForeignKey(Team, related_name='t2_games')
    team2_original_name = models.CharField(max_length=255)

    team1_score = models.IntegerField(null=True)
    official_team1_score = models.IntegerField(null=True)
    team2_score = models.IntegerField(null=True)    
    official_team2_score = models.IntegerField(null=True)

    team1_result = models.CharField(max_length=5)
    team2_result = models.CharField(max_length=5)

    shootout_winner = models.ForeignKey(Team, null=True, related_name='something')
    #some_field = models.IntegerField(null=True)    


    # Games not played, games with result unknown, games with result not recorded yet.
    result_unknown = models.BooleanField(default=False)
    not_played = models.BooleanField(default=False) 

    # Was the game forfeited?
    forfeit = models.BooleanField(default=False)

    # Goals scored in the game.
    goals = models.IntegerField()

    # Minigames were played in MLS, APSL, USL, and probably others.
    minigame = models.BooleanField(default=False)
    indoor = models.BooleanField(default=False)

    minutes = models.IntegerField(default=90)

    # This should probably be a many-to-many?
    competition = models.ForeignKey(Competition)
    season = models.ForeignKey(Season)

    home_team = models.ForeignKey(Team, null=True, related_name='home_games')
    neutral = models.BooleanField(default=False)

    stadium = models.ForeignKey(Stadium, null=True)
    city = models.ForeignKey(City, null=True)
    country = models.ForeignKey(Country, null=True)
    location = models.CharField(max_length=255)

    video = models.CharField(max_length=255)
    notes = models.TextField()

    attendance = models.IntegerField(null=True, blank=True)
    #effective_attendance = models.IntegerField(null=True, blank=True) # account for doubleheaders

    referee = models.ForeignKey(Bio, null=True, blank=True, related_name="games_refereed")
    linesman1 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman1_games")
    linesman2 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman2_games")
    linesman3 = models.ForeignKey(Bio, null=True, blank=True, related_name="linesman3_games")

    merges = models.IntegerField()

    sources = models.ManyToManyField(Source, through='GameSource')

    objects = GameManager()

    class Meta:
        ordering = ('-date',)

        # This no longer seems to be true.
        # unique_together = [('team1', 'date', 'minigame'), ('team2', 'date', 'minigame')]

    def __str__(self):
        return u"%s: %s v %s" % (self.date, self.team1, self.team2)



    # Calendar functions
    def team1_previous_game(self):
        return self.team1.previous_game(self)

    def team1_next_game(self):
        return self.team1.next_game(self)

    def team2_previous_game(self):
        return self.team2.previous_game(self)

    def team2_next_game(self):
        return self.team2.next_game(self)

    def season_previous_game(self):
        return self.season.previous_game(self)

    def season_next_game(self):
        return self.season.next_game(self)


    # Home / Away data
    def away_team(self):
        if self.home_team is None:
            return None
        elif self.home_team == self.team1:
            return self.team2
        else:
            return self.team1


    def home_score(self):
        if self.home_team is None:
            return None
        elif self.home_team == self.team1:
            return self.team1_score
        else:
            return self.team2_score


    def away_score(self):
        if self.home_team is None:
            return None
        elif self.home_team == self.team1:
            return self.team2_score
        else:
            return self.team1_score

    
    def winner(self):
        # Need to hook this in more intelligently with team1_result

        if self.shootout_winner:
            return self.shootout_winner

        if self.team1_score > self.team2_score:
            return self.team1
        elif self.team1_score == self.team2_score:
            return None
        else:
            return self.team2


    def get_completeness(self):
        """Returns how complete a game's data collection is."""
        if self.starter_count == 22:
            return 2
        elif self.starter_count == 0 and self.goal_count == 0:
            return 0
        return 1

    # Colors representing game properties.
    def color_code(self):
        # completeness_color_code
        return ['red', 'yellow', 'green'][self.get_completeness()]


    def color_code_result(self):
        # result color code
        return {
            'win': 'green',
            'tie': 'yellow',
            'loss': 'red',
            }[self.result()]

    def lineup_color_code(self):
        # Merge this and color_code
        if self.not_played or self.result_unknown:
            return ''

        if self.date and self.date > datetime.date.today():
            return ''

        if self.team1_result == '':
            return ''

        return ['red', 'yellow', ''][self.lineup_quality()]

    def goal_color_code(self):
        # Merge this and color_code
        if self.not_played or self.result_unknown:
            return ''

        if self.date and self.date > datetime.date.today():
            return ''

        if self.team1_result == '':
            return ''


        return ['red', 'yellow', ''][self.goal_quality()]


    # Strings representing result

    def score(self):
        """Returns a score string."""
        return "%s - %s" % (self.team1_score, self.team2_score)

    def score_or_result_generic(self, func):
        """Returns a score string."""

        if self.result_unknown:
            return '?'

        if self.not_played:
            return 'np'

        if self.date is not None and self.date > datetime.date.today():
            return 'v'

        if self.team1_result == self.team2_result == '':
            return 'v'

        return func()


    def result_string(self):
        s = "%s - %s" % (self.team1_score_or_result, self.team2_score_or_result)
        return s

    def score_or_result(self):
        return self.score_or_result_generic(self.result_string)

    def reverse_result_string(self):
        return "%s - %s" % (self.team2_score_or_result, self.team1_score_or_result)

    def reverse_score_or_result(self):
        return self.score_or_result_generic(self.reverse_result_string)

    def game_string(self):
        return "%s %s %s" % (self.team1, self.result_string(), self.team2)
        


    @property
    def team1_score_or_result(self):
        if self.team1_score is not None:
            if self.shootout_winner == self.team1:
                return "(SO) %s" % self.team1_score
            else:
                return self.team1_score
        return self.team1_result.capitalize()

    @property
    def team2_score_or_result(self):
        if self.team2_score is not None:
            if self.shootout_winner == self.team2:
                return "%s (SO)" % self.team2_score
            else:
                return self.team2_score
        return self.team2_result.capitalize()


    # Queries
    def team1_lineups(self):
        return self.appearance_set.filter(team=self.team1)

    def team2_lineups(self):
        return self.appearance_set.filter(team=self.team2)

    def team1_gamestats(self):
        return self.gamestat_set.filter(team=self.team1)

    def team2_gamestats(self):
        return self.gamestat_set.filter(team=self.team2)

    def team1_starters(self):
        return self.team1_lineups().filter(on=0).exclude(off=0)

    def team2_starters(self):
        return self.team2_lineups().filter(on=0).exclude(off=0)

    # Game data
    def lineup_quality(self):
        if self.starter_count == 22:
            return 2
        elif self.starter_count > 0:
            return 1
        return 0


    def goal_quality(self):

        if self.team1_score is None or self.team2_score is None:
            return 0

        score_goals = self.team1_score + self.team2_score
        if self.goal_count == score_goals:
            return 2
        elif self.goal_count > 0:
            return 1
        else:
            return 0


    def starter_numbers(self):
        """A convenience method for making sure game lineups are good."""
        return "%s:%s" % (self.team1_starter_count, self.team2_starter_count)


    # Need tests for these.
    def zipped_lineups(self):
        # FIX THIS; TRUNACATING TEAM LINEUPS
        t1l, t2l = self.team1_lineups(), self.team2_lineups()
        t1c, t2c = t1l.count(), t2l.count()
        if t1c == t2c:
            return zip(t1l, t2l)
        else:
            m = max(t1c, t2c)
            l1, l2 = pad_list(list(t1l), m), pad_list(list(t2l), m)
            return zip(l1, l2)

    def zipped_gamestats(self):
        # FIX THIS; TRUNACATING TEAM LINEUPS
        t1l, t2l = self.team1_gamestats(), self.team2_gamestats()
        t1c, t2c = t1l.count(), t2l.count()
        if t1c == t2c:
            return zip(t1l, t2l)
        else:
            m = max(t1c, t2c)
            l1, l2 = pad_list(list(t1l), m), pad_list(list(t2l), m)
            return zip(l1, l2)

    def goal_string(self):
        from goals.models import Goal
        goals = Goal.objects.filter(game=self).order_by('minute', 'team')
        fmt = lambda g: "%s: %s %s" % (g.team, g.player, g.minute) if g.minute else "%s: %s" % (g.team, g.player)
        if goals.exists():
            return "\n".join([fmt(goal) for goal in goals])
        else:
            return ""

    # These should hang off of Team, not Game.
    def previous_games(self, team):
        assert team in (self.team1, self.team2)
        if self.date:
            return Game.objects.team_filter(team).filter(season=self.season).filter(date__lt=self.date).order_by('date')
        else:
            return []

    # Metainformation
    # Should be cached?
    def streak(self, team):
        """
        Returns a team's results streak, counting this game.
        e.g. 3 wins in a row.
        """

        result = self.result(team)
        s = 1

        games = self.previous_games(team).order_by('-date')
        for e in games:
            r = e.result(team)
            if r != result:
                return s
            else:
                s += 1

        return s

    def series(self):
        """
        Returns the result of the series between two teams in the same season.
        """
        return Game.objects.filter(season=self.season).filter(
            models.Q(team1=self.team1) | models.Q(team2=self.team1)).filter(
            models.Q(team1=self.team2) | models.Q(team2=self.team2))

    # Standings functions

    def standings(self, team):
        """
        Returns a season's standings as of the current game.
        """
        from collections import defaultdict
        d = defaultdict(int)
        for game in self.previous_games(team):
            d[game.result(team)] += 1
        d[self.result(team)] += 1
        return (d['win'], d['tie'], d['loss'])


    def home_standings(self):
        return None
        from standings.models import Standing
        try:
            return Standing.objects.get(date=self.date, season=self.season, team=self.team1)
        except:
            return None

    def away_standings(self):
        return None
        from standings.models import Standing
        try:
            return Standing.objects.get(date=self.date, season=self.season, team=self.team2)
        except:
            return None

    def home_standings_string(self):
        s = self.home_standings()
        if s:
            return "%s-%s-%s" % (s.wins, s.ties, s.losses)
        else:
            return ''

    def away_standings_string(self):
        s = self.away_standings()
        if s:
            return "%s-%s-%s" % (s.wins, s.ties, s.losses)
        else:
            return ''

    # More string / streak stuff.

    def streaks(self):
        return [(self.result(e), self.streak(e)) for  e in (self.team1, self.team2)]

    def streak_string(self, t):
        """
        """
        d = {
            'tie': 'ties',
            'loss': 'losses',
            'win': 'wins',
            }
        stype, count = t
        if count != 1:
            stype = d[stype]
        return "%s %s" % (count, stype)

    def home_streak_string(self):
        return self.streak_string(self.streaks()[0])
    
    def away_streak_string(self):
        return self.streak_string(self.streaks()[1])

    def goals_for(self, team):
        """
        Goals for a given team in a given game.
        """
        # Not a great system.
        assert team in (self.team1, self.team2)
        
        if team == self.team1:
            score = self.team1_score
        else:
            score = self.team2_score

        return int(score)


    def goals_against(self, team):
        """
        """
        assert team in (self.team1, self.team2)

        if team == self.team1:
            score = self.team2_score
        else:
            score = self.team1_score

        return int(score)


    def margin(self, team):
        try:
            return self.goals_for(team) - self.goals_against(team)
        except TypeError:
            return None

    def result(self, team):
        """
        Returns a string indicating the result of a game
        (win, loss, or tie)
        """
        assert team in (self.team1, self.team2)
        
        try:
            team1_score = int(self.official_team1_score or self.team1_score)
            team2_score = int(self.official_team2_score or self.team2_score)
        except:
            return None

        if team1_score == team2_score: 
            return 't'
        if team1_score > team2_score: 
            if team == self.team1:
                return 'w'
            else:
                return 'l'
        else:
            if team == self.team1:
                return 'l'
            else:
                return 'w'

        raise

    def same_day_games(self):
        """
        Returns all games played on the same date (excluding this one).
        """
        if self.date:
            return Game.objects.filter(date=self.date).exclude(id=self.id).order_by('competition__level', 'competition__name')
        else:
            return []


    def opponent(self, team):
        """
        Given a team, returns the opponent.
        """
        if team == self.team1:
            return self.team2
        elif team == self.team2:
            return self.team1
        else:
            raise




class GameSource(models.Model):
    """
    A many-to-many mapping of a source to a single game.
    """
    # A separate model is used to include source_url, which is unique to each mapping.


    game = models.ForeignKey(Game)
    source = models.ForeignKey(Source)
    source_url = models.CharField(max_length=1023)

