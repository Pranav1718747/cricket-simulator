from django.db import models

class Player(models.Model):
    ROLE_CHOICES = (
        ('Batsman', 'Batsman'),
        ('Bowler', 'Bowler'),
        ('All-rounder', 'All-rounder'),
        ('Batting All-rounder', 'Batting All-rounder'),
        ('Bowling All-rounder', 'Bowling All-rounder'),
        ('Wicketkeeper', 'Wicketkeeper'),
    )
    
    BOWLING_STYLE_CHOICES = (
        ('Swing Specialist', 'Swing Specialist'),
        ('Death Specialist', 'Death Specialist'),
        ('Spinner', 'Spinner'),
        ('All-Round Pacer', 'All-Round Pacer'),
        ('All-Round Spinner', 'All-Round Spinner'),
        ('None', 'None')
    )
    
    TACTICAL_ROLE_CHOICES = (
        ('Anchor', 'Anchor'),
        ('Finisher', 'Finisher'),
        ('Power Hitter', 'Power Hitter'),
        ('Standard', 'Standard')
    )
    
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    tactical_role = models.CharField(max_length=50, choices=TACTICAL_ROLE_CHOICES, default='Standard')
    bowling_style = models.CharField(max_length=50, choices=BOWLING_STYLE_CHOICES, default='None')
    star_rating = models.FloatField(default=2.5) # The base tier multiplier
    
    # --- V2 Granular Attributes (0-100 scale) ---
    # Batting
    batting_power = models.IntegerField(default=50)
    batting_consistency = models.IntegerField(default=50)
    spin_skill = models.IntegerField(default=50) # How well they play spin
    pace_skill = models.IntegerField(default=50) # How well they play pace
    
    # Bowling
    powerplay_skill = models.IntegerField(default=50) # Overs 1-6
    middle_overs_skill = models.IntegerField(default=50) # Overs 7-15
    death_bowling_skill = models.IntegerField(default=50) # Overs 16-20
    is_spinner = models.BooleanField(default=False)
    
    # General
    fielding_skill = models.IntegerField(default=50)
    
    # --- Legacy Real World Stats Engine ---
    
    # Batting stats
    batting_avg = models.FloatField(default=0.0)
    strike_rate = models.FloatField(default=0.0)
    
    # Bowling stats
    bowling_avg = models.FloatField(default=0.0)
    economy = models.FloatField(default=0.0)
    
    # Career stats
    matches = models.IntegerField(default=0)
    runs = models.IntegerField(default=0)
    wickets = models.IntegerField(default=0)
    
    # IPL specific stats
    ipl_matches = models.IntegerField(default=0)
    ipl_runs = models.IntegerField(default=0)
    ipl_batting_avg = models.FloatField(default=0.0)
    ipl_strike_rate = models.FloatField(default=0.0)
    ipl_wickets = models.IntegerField(default=0)
    ipl_bowling_avg = models.FloatField(default=0.0)
    ipl_economy = models.FloatField(default=0.0)
    
    # Hidden form or rating points
    form_rating = models.FloatField(default=5.0)

    def __str__(self):
        return f"{self.name} ({self.country})"

class PlayerMatchup(models.Model):
    batsman = models.ForeignKey(Player, related_name='matchups_as_batsman', on_delete=models.CASCADE)
    bowler = models.ForeignKey(Player, related_name='matchups_as_bowler', on_delete=models.CASCADE)
    
    balls_faced = models.IntegerField(default=0)
    runs_scored = models.IntegerField(default=0)
    dismissals = models.IntegerField(default=0)
    strike_rate = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('batsman', 'bowler')

    def __str__(self):
        return f"{self.batsman.name} vs {self.bowler.name}"

class Team(models.Model):
    name = models.CharField(max_length=255)
    players = models.ManyToManyField(Player, related_name='teams')

    def __str__(self):
        return self.name

class Match(models.Model):
    team_a = models.ForeignKey(Team, related_name='matches_as_team_a', on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name='matches_as_team_b', on_delete=models.CASCADE)
    
    # V2 Environment / Conditions
    PITCH_CHOICES = (
        ('Batting', 'Batting'),
        ('Spin', 'Spin'),
        ('Pace', 'Pace'),
        ('Balanced', 'Balanced')
    )
    pitch_type = models.CharField(max_length=50, choices=PITCH_CHOICES, default='Balanced')
    dew_factor = models.BooleanField(default=False)
    home_advantage_team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='home_matches')
    
    # Logs and Tracking
    scorecard = models.JSONField(default=dict, blank=True)
    simulation_log = models.JSONField(default=list, blank=True)
    
    winner = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name} - {self.created_at.strftime('%Y-%m-%d')}"
