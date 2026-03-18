from django.contrib import admin
from .models import Player, Team, Match

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'role', 'batting_avg', 'strike_rate', 'bowling_avg', 'economy')
    search_fields = ('name', 'country', 'role')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team_a', 'team_b', 'winner', 'created_at')
