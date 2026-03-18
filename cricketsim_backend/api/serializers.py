from rest_framework import serializers
from .models import Player, Team, Match

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    player_ids = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(),
        many=True,
        write_only=True,
        source='players'
    )
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'players', 'player_ids']

class MatchSerializer(serializers.ModelSerializer):
    team_a = TeamSerializer(read_only=True)
    team_b = TeamSerializer(read_only=True)
    team_a_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        write_only=True,
        source='team_a'
    )
    team_b_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        write_only=True,
        source='team_b'
    )
    
    class Meta:
        model = Match
        fields = ['id', 'team_a', 'team_b', 'team_a_id', 'team_b_id', 'scorecard', 'simulation_log', 'winner', 'created_at']
