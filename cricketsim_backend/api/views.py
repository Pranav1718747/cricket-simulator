from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Player, Team, Match
from .serializers import PlayerSerializer, TeamSerializer, MatchSerializer
from .simulation import simulate_match

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    
    def get_queryset(self):
        queryset = Player.objects.all()
        role = self.request.query_params.get('role', None)
        if role is not None:
            queryset = queryset.filter(role=role)
        return queryset

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all().order_by('-created_at')
    serializer_class = MatchSerializer

    @action(detail=False, methods=['post'])
    def simulate(self, request):
        team_a_id = request.data.get('team_a_id')
        team_b_id = request.data.get('team_b_id')
        pitch_type = request.data.get('pitch_type', 'Balanced')
        dew_factor = request.data.get('dew_factor', False)
        
        if not team_a_id or not team_b_id:
            return Response({'error': 'team_a_id and team_b_id are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            team_a = Team.objects.get(id=team_a_id)
            team_b = Team.objects.get(id=team_b_id)
        except Team.DoesNotExist:
            return Response({'error': 'One or both teams not found.'}, status=status.HTTP_404_NOT_FOUND)
            
        conditions = {
            'pitch_type': pitch_type,
            'dew_factor': dew_factor
        }
            
        player_ids_a = request.data.get('player_ids_a', [])
        player_ids_b = request.data.get('player_ids_b', [])
        batting_first = request.data.get('batting_first', 'team_a')
        
        # Run simulation with V2 Engine
        result = simulate_match(team_a, team_b, conditions, player_ids_a, player_ids_b, batting_first)
        
        # Save match to DB
        match = Match.objects.create(
            team_a=team_a,
            team_b=team_b,
            pitch_type=pitch_type,
            dew_factor=dew_factor,
            scorecard=result['scorecard'],
            simulation_log=result['log'],
            winner=result['winner']
        )
        
        serializer = self.get_serializer(match)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
