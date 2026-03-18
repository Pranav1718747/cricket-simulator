import random
from .models import PlayerMatchup

# ─────────────────────────────────────────────────────────────
# PITCH
# ─────────────────────────────────────────────────────────────
def get_pitch_modifiers(pitch_type):
    if pitch_type == 'Spin':
        return {'spin_skill_boost': 15, 'pace_skill_boost': -5, 'bat_power_boost': -10}
    elif pitch_type == 'Pace':
        return {'spin_skill_boost': -5, 'pace_skill_boost': 15, 'bat_power_boost': -5}
    elif pitch_type == 'Batting':
        return {'spin_skill_boost': -10, 'pace_skill_boost': -10, 'bat_power_boost': 15}
    return {'spin_skill_boost': 0, 'pace_skill_boost': 0, 'bat_power_boost': 0}


# ─────────────────────────────────────────────────────────────
# MATCHUP HISTORY
# ─────────────────────────────────────────────────────────────
def get_matchup_bonus(batsman, bowler):
    try:
        matchup = PlayerMatchup.objects.get(batsman=batsman, bowler=bowler)
        if matchup.balls_faced > 0:
            sr_dominance = (matchup.strike_rate - 120) / 40.0
            balls_per_wkt = matchup.balls_faced / matchup.dismissals if matchup.dismissals > 0 else 100
            wkt_dominance = (50 - balls_per_wkt) / 20.0
            return (sr_dominance * 10) - (wkt_dominance * 10)
    except PlayerMatchup.DoesNotExist:
        pass
    return 0


# ─────────────────────────────────────────────────────────────
# BALL-BY-BALL ENGINE
# ─────────────────────────────────────────────────────────────
def simulate_ball(batsman, bowler, over, conditions, active_form,
                  match_momentum, match_pressure=1.0, phase_aggression=1.0):

    # Base probabilities
    prob_dot = 28.0
    prob_1   = 34.0
    prob_2   = 10.0
    prob_4   = 16.0
    prob_6   = 7.0
    prob_w   = 5.0

    bat_power  = max(1, min(100, batsman.batting_power + active_form.get(batsman.name, 0)))
    bat_consist = max(1, min(100, batsman.batting_consistency + active_form.get(batsman.name, 0)))

    # Phase-specific bowling skill
    if over < 6:
        bowl_skill = bowler.powerplay_skill
    elif over < 15:
        bowl_skill = bowler.middle_overs_skill
    else:
        bowl_skill = bowler.death_bowling_skill

    bowl_skill = max(1, min(100, bowl_skill + active_form.get(bowler.name, 0)))

    # Pitch & conditions
    pitch_mods = get_pitch_modifiers(conditions.get('pitch_type', 'Balanced'))
    bat_power += pitch_mods['bat_power_boost']

    if conditions.get('dew_factor', False) and over >= 15:
        bowl_skill -= 20

    if bowler.is_spinner:
        bowl_skill += pitch_mods['spin_skill_boost']
        bat_consist += (batsman.spin_skill - 50) * 0.2
    else:
        bowl_skill += pitch_mods['pace_skill_boost']
        bat_consist += (batsman.pace_skill - 50) * 0.2

    matchup_shift = get_matchup_bonus(batsman, bowler)
    bat_power += matchup_shift
    bat_consist += matchup_shift

    power_diff  = bat_power - bowl_skill
    consist_diff = bat_consist - bowl_skill

    power_diff  += match_momentum
    consist_diff += match_momentum

    # Apply phase aggression (death = more aggressive)
    power_diff *= phase_aggression

    # Mutate probabilities
    scale = power_diff / 60.0
    prob_4 = max(3, prob_4 + scale * 8)
    prob_6 = max(1, prob_6 + scale * 5)
    prob_dot = max(5, prob_dot - scale * 5)

    # Wicket probability: harder bowler = more wickets
    skill_scale = consist_diff / 60.0
    prob_w = max(2, min(18, prob_w - skill_scale * 5))

    # Match pressure (chasing)
    if match_pressure > 1.0:
        prob_4 *= 1.15
        prob_6 *= 1.2
        prob_w *= 1.1

    # Death scoring spike
    if over >= 15:
        prob_4 *= 1.15
        prob_6 *= 1.3
        prob_dot *= 0.85

    # Powerplay boundaries boost
    if over < 6:
        prob_4 *= 1.1
        prob_6 *= 1.05

    total = prob_dot + prob_1 + prob_2 + prob_4 + prob_6 + prob_w
    r = random.uniform(0, total)

    if r < prob_w: return 'W'
    r -= prob_w
    if r < prob_dot: return 0
    r -= prob_dot
    if r < prob_1: return 1
    r -= prob_1
    if r < prob_2: return 2
    r -= prob_2
    if r < prob_4: return 4
    return 6


# ─────────────────────────────────────────────────────────────
# TEAM STRENGTH
# ─────────────────────────────────────────────────────────────
def compute_team_strength(players):
    """Average star rating of the playing XI."""
    if not players:
        return 0.0
    return round(sum(p.star_rating for p in players[:11]) / min(len(players), 11), 2)


def get_match_type(diff):
    """Return match type label and description based on strength difference."""
    if diff <= 0.3:
        return 'THRILLER', 'Very close match — expect a last-over finish!'
    elif diff <= 0.7:
        return 'COMPETITIVE', 'Competitive match — result in the last 2–3 overs.'
    elif diff <= 1.2:
        return 'SLIGHT ADVANTAGE', 'Slightly one-sided — stronger team likely wins around overs 16–18.'
    else:
        return 'DOMINATING', 'Strong team expected to dominate.'


# ─────────────────────────────────────────────────────────────
# BATTING ORDER
# ─────────────────────────────────────────────────────────────
def sort_batting_order(players):
    openers   = [p for p in players if p.tactical_role == 'Opener'][:2]
    anchors   = [p for p in players if p.tactical_role == 'Anchor' and p not in openers]
    power_hit = [p for p in players if p.tactical_role == 'Power Hitter']
    finishers = [p for p in players if p.tactical_role == 'Finisher']
    keepers   = [p for p in players if p.role == 'Wicketkeeper'][:1]
    allround  = [p for p in players if p.role == 'All-rounder' and p not in openers and p not in finishers]
    bowlers   = [p for p in players if p.role == 'Bowler']

    ordered = []
    for p in openers:
        if p not in ordered: ordered.append(p)
        if len(ordered) == 2: break
    for p in anchors:
        if p not in ordered: ordered.append(p)
        if len(ordered) == 4: break
    for p in power_hit:
        if p not in ordered: ordered.append(p)
    for p in keepers:
        if p not in ordered: ordered.append(p)
    for p in finishers:
        if p not in ordered: ordered.append(p)
    for p in allround:
        if p not in ordered: ordered.append(p)
    for p in bowlers:
        if p not in ordered: ordered.append(p)
    for p in players:
        if p not in ordered: ordered.append(p)

    return ordered[:11]


# ─────────────────────────────────────────────────────────────
# AUTO XI SELECTION
# ─────────────────────────────────────────────────────────────
def _auto_select_xi(player_pool, exclude):
    pool = [p for p in player_pool if p not in exclude]
    selected = []

    keepers = [p for p in pool if p.role == 'Wicketkeeper']
    if keepers: selected.append(keepers[0])

    bowlers = [p for p in pool if p.role == 'Bowler' and p not in selected]
    selected += bowlers[:4]

    ars = [p for p in pool if p.role == 'All-rounder' and p not in selected]
    selected += ars[:2]

    rest = [p for p in pool if p not in selected]
    selected += rest[:11 - len(selected)]

    return selected[:11]


# ─────────────────────────────────────────────────────────────
# BOWLING PHASE RULES
# ─────────────────────────────────────────────────────────────
def get_phase(over):
    if over < 6:   return 'powerplay'
    if over < 15:  return 'middle'
    return 'death'


def bowler_allowed_in_phase(bowler, phase, pp_non_pacer_overs):
    """Basic eligibility rules for match phases."""
    is_pacer = 'pacer' in (bowler.bowling_style or '').lower() or 'specialist' in (bowler.bowling_style or '').lower()
    if 'spinner' in (bowler.bowling_style or '').lower(): is_pacer = False

    if phase == 'powerplay':
        # Pacers only. Max 1 over of spin/all-rounder.
        if not is_pacer:
            return pp_non_pacer_overs < 1
        return True
    elif phase == 'middle':
        return True
    elif phase == 'death':
        # ONLY PACERS.
        return is_pacer

    return True


def score_bowler_for_phase(bowler, phase, over, recent_bowler_names=None, overs_bowled_by_him=0):
    """Higher score = more preferred for this phase. Includes variety penalty and specialist-preservation."""
    style = (bowler.bowling_style or '').lower()
    is_ar = bowler.role == 'All-rounder'
    score = bowler.star_rating * 10

    # Phase specific skill bonuses
    if phase == 'powerplay':
        if 'swing' in style:    score += 50
        if 'death' in style:    
            score -= 50  # Save for end
            if overs_bowled_by_him >= 1: score -= 100 # Definitely save
        if 'spin' in style or is_ar: score -= 30
        
    elif phase == 'middle':
        if 'spinner' in style:   score += 50 # Spinners dominate middle
        if is_ar:                score += 40 # ARs used in middle
        if 'death' in style and overs_bowled_by_him >= 2: 
            score -= 80 # Strictly save him for the death phase
            
    elif phase == 'death':
        if 'death' in style:    score += 150
        if not is_ar:           score += 50
        if 'spinner' in style:  score -= 999 # Hard NO per latest request
        if is_ar:               score -= 100 # Prefer pure pacers

    # variety penalty
    if recent_bowler_names:
        if len(recent_bowler_names) >= 2 and recent_bowler_names[-2] == bowler.name:
            score -= 40 # Don't bring back too quickly
            
    return score


# ─────────────────────────────────────────────────────────────
# MAIN INNINGS SIMULATION
# ─────────────────────────────────────────────────────────────
def simulate_innings(batting_team, bowling_team, conditions, active_form,
                     target=None, match_type='COMPETITIVE', strength_diff=0.5,
                     ordered_batters=None, ordered_bowlers=None):
    balls_log = []
    
    # Use explicit ordering if provided (from frontend selection)
    if ordered_batters:
        raw_batting = ordered_batters
    else:
        raw_batting = list(batting_team.players.all())

    if ordered_bowlers:
        raw_bowling = ordered_bowlers
    else:
        raw_bowling = list(bowling_team.players.all())

    # Auto-assign if team has no players
    if not raw_batting or not raw_bowling:
        from .models import Player
        all_players = list(Player.objects.all().order_by('-star_rating'))
        if not raw_batting:
            raw_batting = _auto_select_xi(all_players, exclude=[])
        if not raw_bowling:
            bat_names = {p.name for p in raw_batting}
            remaining = [p for p in all_players if p.name not in bat_names]
            raw_bowling = _auto_select_xi(remaining, exclude=[])

    # Batting order: EXACTLY as the user selected — no reordering
    batting_players = list(raw_batting)

    # Separate bowler pools
    pure_bowlers   = [p for p in raw_bowling if p.role == 'Bowler']
    all_rounders   = [p for p in raw_bowling if p.role == 'All-rounder']
    bowling_pool   = pure_bowlers + all_rounders

    score, wickets = 0, 0
    overs_max = 20

    striker_idx = 0
    non_striker_idx = 1
    recent_bowlers = [] 
    has_batted = [0, 1]
    pp_non_pacer_overs = 0
    match_momentum = 0.0

    scorecard = {
        'team_name': batting_team.name,
        'batsmen': {
            p.name: {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'out': False}
            for p in batting_players
        },
        'bowlers': {
            p.name: {'overs': 0.0, 'runs': 0, 'wickets': 0}
            for p in (pure_bowlers + all_rounders)
        },
        'total_runs': 0,
        'wickets': 0,
        'overs': 0.0
    }

    def get_next_batter(current_over, wkts):
        available = [i for i in range(len(batting_players)) if i not in has_batted]
        if not available: return None
        return available[0]  # Strict order — next in selected list

    for over in range(overs_max):
        phase = get_phase(over)

        # Phase aggression for batters
        if phase == 'powerplay': phase_aggression = 1.15
        elif phase == 'middle':  phase_aggression = 1.0
        else:                    phase_aggression = 1.25

        # ── BOWLER SELECTION ─────────────────────────────────────────
        # Rules:
        #  - Pure bowlers: can bowl in any phase, must complete their 4-over allotment
        #  - All-rounders: bowl ONLY in middle (6-14) and max 1 over in death (15-19)
        #                  NOT allowed in powerplay

        def is_under_quota(p):
            return scorecard['bowlers'].get(p.name, {'overs': 0.0})['overs'] < 4.0

        def get_candidates(pool, relax_phase=False):
            last_bowler_name = recent_bowlers[-1] if recent_bowlers else None
            
            # PACE PRESERVATION CHECK
            pacers = [p for p in bowling_pool if 'pacer' in (p.bowling_style or '').lower() or 'specialist' in (p.bowling_style or '').lower()]
            # Filter out spinners from 'specialist' check
            pacers = [p for p in pacers if 'spinner' not in (p.bowling_style or '').lower()]
            
            total_pacer_quota_left = sum([4.0 - scorecard['bowlers'][p.name]['overs'] for p in pacers])
            
            death_overs_left = 5 if over < 15 else max(0, 20 - over)
            
            # If we are low on pace overs, we MUST save them for death
            # Hard preservation: if we have EXPLICITLY just enough for the death, block pacers from bowling now
            needs_hard_preservation = total_pacer_quota_left <= death_overs_left

            # Check phase restrictions strictly
            def check_rules(p):
                if not is_under_quota(p): return False
                if p.name == last_bowler_name: return False
                
                style = (p.bowling_style or '').lower()
                is_pacer = 'pacer' in style or 'death specialist' in style or 'swing' in style
                if 'spinner' in style: is_pacer = False

                if not relax_phase:
                    # Powerplay Rule: Pacers primary. 1-2 Non-pacer exception if preservation needed.
                    if phase == 'powerplay':
                        if not is_pacer:
                            # If we MUST save for death, we can allow more exceptions in PP
                            limit = 2 if needs_hard_preservation else 1
                            if pp_non_pacer_overs >= limit: return False
                        elif needs_hard_preservation:
                            return False # Block pacer to force the non-pacer exception
                    
                    # Middle Phase: If hard preservation is active, block pacers to save for death
                    if phase == 'middle' and is_pacer and needs_hard_preservation:
                        return False

                    # Death Rule: Pacers only
                    if phase == 'death' and not is_pacer:
                        return False

                return True

            eligible = [p for p in pool if check_rules(p)]
            if not eligible:
                # If we have NO pacer for death but we blocked non-pacers, we have to relax
                eligible = [p for p in pool if is_under_quota(p) and p.name != last_bowler_name]

            # Strategic Scoring:
            def strategic_score(p):
                base = score_bowler_for_phase(p, phase, over, recent_bowlers, scorecard['bowlers'][p.name]['overs'])
                is_pacer = 'pacer' in (p.bowling_style or '').lower() or 'specialist' in (p.bowling_style or '').lower()
                if 'spinner' in (p.bowling_style or '').lower(): is_pacer = False
                
                # If we need preservation and it's NOT death, penalize pacers heavily
                if needs_hard_preservation and phase != 'death' and is_pacer:
                    base -= 500
                
                return base

            return sorted(eligible, key=strategic_score, reverse=True)

        candidates = get_candidates(bowling_pool)
        
        # If middle phase, filter for spinners/ARs if possible to make them dominant
        if phase == 'middle' and not recent_bowlers[-1:] == []:
             pref = [c for c in candidates if 'spinner' in (c.bowling_style or '').lower() or c.role == 'All-rounder']
             if pref: candidates = pref

        # Register new bowlers in scorecard
        for p in candidates:
            if p.name not in scorecard['bowlers']:
                scorecard['bowlers'][p.name] = {'overs': 0.0, 'runs': 0, 'wickets': 0}

        bowler = candidates[0]  # Pick best-ranked for this phase
        recent_bowlers.append(bowler.name)
        bowler_stats = scorecard['bowlers'][bowler.name]

        over_runs = 0
        over_boundaries = 0
        over_wickets = 0
        over_desc_parts = []

        for ball_in_over in range(1, 7):
            if wickets >= 10: break

            striker = batting_players[striker_idx]
            match_pressure = 1.0
            balls_left = max(1, (overs_max - over) * 6 - ball_in_over + 1)
            if target:
                run_req = target - score
                rr_required = (run_req / balls_left) * 6
                if rr_required > 12:   match_pressure = 1.4
                elif rr_required > 9:  match_pressure = 1.2
                elif rr_required > 7:  match_pressure = 1.1

            outcome = simulate_ball(
                striker, bowler, over, conditions, active_form,
                match_momentum, match_pressure, phase_aggression
            )

            ball_desc = f"{over}.{ball_in_over} {bowler.name} → {striker.name}: "
            batsman_stats = scorecard['batsmen'][striker.name]
            batsman_stats['balls'] += 1

            if outcome == 'W':
                wickets += 1
                over_wickets += 1
                batsman_stats['out'] = True
                bowler_stats['wickets'] += 1
                ball_desc += f"OUT! {striker.name} dismissed!"
                next_idx = get_next_batter(over, wickets)
                if next_idx is not None:
                    striker_idx = next_idx
                    has_batted.append(next_idx)
            else:
                runs = int(outcome)
                score += runs
                over_runs += runs
                batsman_stats['runs'] += runs
                bowler_stats['runs'] += runs

                if runs == 4:
                    batsman_stats['fours'] += 1
                    over_boundaries += 1
                    ball_desc += "FOUR!"
                elif runs == 6:
                    batsman_stats['sixes'] += 1
                    over_boundaries += 1
                    ball_desc += "SIX!"
                elif runs == 0:
                    ball_desc += "dot ball."
                else:
                    ball_desc += f"{runs} run{'s' if runs > 1 else ''}."

                if runs % 2 != 0:
                    striker_idx, non_striker_idx = non_striker_idx, striker_idx

            score_str = f"{score}/{wickets}"
            over_desc_parts.append(ball_desc + f" [{score_str}]")

            balls_log.append({
                'over': f"{over}.{ball_in_over}",
                'bowler': bowler.name,
                'batsman': striker.name,
                'outcome': outcome,
                'description': ball_desc,
                'score': score_str
            })

            if target and score > target:
                break

        # ── END-OF-OVER SUMMARY ───────────────────────────────────
        over_summary = f"  End of Over {over+1}: {score}/{wickets} | {bowler.name} bowled — {over_runs} runs"
        if over_wickets > 0:
            over_summary += f", {over_wickets} wkt{'s' if over_wickets > 1 else ''}"
        balls_log.append({
            'over': f"{over}.END",
            'bowler': bowler.name,
            'batsman': '',
            'outcome': 'END',
            'description': over_summary,
            'score': f"{score}/{wickets}"
        })

        # ── MOMENTUM UPDATE ────────────────────────────────────────
        if over_boundaries >= 3:   match_momentum = min(30, match_momentum + 5)
        elif over_boundaries >= 2: match_momentum = min(30, match_momentum + 2)
        if over_wickets >= 2:      match_momentum = max(-30, match_momentum - 10)
        elif over_wickets == 1:    match_momentum = max(-30, match_momentum - 3)
        if over_wickets == 0 and over_boundaries <= 1:
            if match_momentum > 0: match_momentum = max(0, match_momentum - 2)
            else: match_momentum = min(0, match_momentum + 2)

        striker_idx, non_striker_idx = non_striker_idx, striker_idx
        bowler_stats['overs'] += 1.0

        is_pacer = 'pacer' in (bowler.bowling_style or '').lower() or 'specialist' in (bowler.bowling_style or '').lower()
        if 'spinner' in (bowler.bowling_style or '').lower(): is_pacer = False

        if phase == 'powerplay' and not is_pacer:
            pp_non_pacer_overs += 1

        if wickets >= 10 or (target and score > target):
            overs_bowled = over + (ball_in_over / 6.0)
            scorecard['overs'] = round(overs_bowled, 1)
            break
    else:
        scorecard['overs'] = 20.0

    scorecard['total_runs'] = score
    scorecard['wickets'] = wickets
    return score, wickets, scorecard, balls_log


# ─────────────────────────────────────────────────────────────
# MATCH ORCHESTRATOR
# ─────────────────────────────────────────────────────────────
def simulate_match(team_a, team_b, conditions=None, player_ids_a=None, player_ids_b=None, batting_first='team_a'):
    if not conditions:
        conditions = {'pitch_type': 'Balanced', 'dew_factor': False}

    # Fetch players with potential ordering
    def get_ordered_players(team, explicit_ids):
        all_p = {p.id: p for p in team.players.all()}
        if explicit_ids:
            # Filter and order by IDs sent from frontend
            return [all_p[pid] for pid in explicit_ids if pid in all_p]
        return list(team.players.all().order_by('-star_rating'))

    players_a = get_ordered_players(team_a, player_ids_a)
    players_b = get_ordered_players(team_b, player_ids_b)

    if not players_a or not players_b:
        from .models import Player
        all_players = list(Player.objects.all().order_by('-star_rating'))
        if not players_a:
            players_a = _auto_select_xi(all_players, exclude=[])
        if not players_b:
            bat_names = {p.name for p in players_a}
            remaining = [p for p in all_players if p.name not in bat_names]
            players_b = _auto_select_xi(remaining, exclude=[])

    strength_a = compute_team_strength(players_a)
    strength_b = compute_team_strength(players_b)
    diff = abs(strength_a - strength_b)
    match_type, match_desc = get_match_type(diff)

    # Pre-match form
    active_form = {}
    for p in players_a + players_b:
        active_form[p.name] = random.randint(-10, 10)

    # Determine batting order based on toss
    if batting_first == 'team_b':
        first_bat_team, first_bowl_team = team_b, team_a
        first_bat_players, first_bowl_players = players_b, players_a
        second_bat_team, second_bowl_team = team_a, team_b
        second_bat_players, second_bowl_players = players_a, players_b
    else:
        first_bat_team, first_bowl_team = team_a, team_b
        first_bat_players, first_bowl_players = players_a, players_b
        second_bat_team, second_bowl_team = team_b, team_a
        second_bat_players, second_bowl_players = players_b, players_a

    # Innings 1
    score1, wkts1, sc1, log1 = simulate_innings(
        first_bat_team, first_bowl_team, conditions, active_form,
        match_type=match_type, strength_diff=diff,
        ordered_batters=first_bat_players, ordered_bowlers=first_bowl_players
    )

    # Innings 2
    score2, wkts2, sc2, log2 = simulate_innings(
        second_bat_team, second_bowl_team, conditions, active_form,
        target=score1, match_type=match_type, strength_diff=diff,
        ordered_batters=second_bat_players, ordered_bowlers=second_bowl_players
    )

    if score2 > score1:
        winner = f"{second_bat_team.name} won by {10 - wkts2} wicket{'s' if (10-wkts2) != 1 else ''}"
    elif score1 > score2:
        winner = f"{first_bat_team.name} won by {score1 - score2} run{'s' if (score1-score2) != 1 else ''}"
    else:
        winner = "Match Tied!"

    return {
        'scorecard': {'innings_1': sc1, 'innings_2': sc2},
        'log': {'innings_1': log1, 'innings_2': log2},
        'winner': winner,
        'match_meta': {
            'team_a_strength': strength_a,
            'team_b_strength': strength_b,
            'strength_diff': diff,
            'match_type': match_type,
            'match_description': match_desc,
            'batting_first_team': first_bat_team.name,
        }
    }
