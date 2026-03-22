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
    allround  = [p for p in players if p.role in ['All-rounder', 'Batting All-rounder', 'Bowling All-rounder'] and p not in openers and p not in finishers]
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

    ars = [p for p in pool if p.role in ['All-rounder', 'Batting All-rounder', 'Bowling All-rounder'] and p not in selected]
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

def generate_bowling_strategy(bowling_pool):
    """
    Dynamically generates a 20-over bowling plan based on player skills and match phases.
    Uses weighted randomness to choose bowlers, respecting the 4-over limit and phase constraints.
    """
    xi = list(bowling_pool)
    overs_bowled = {p.name: 0 for p in xi}
    plan = []
    prev_bowler_name = None

    # Categorize for the roles_map (representative only)
    pacers = sorted([p for p in xi if not p.is_spinner and 'spinner' not in (p.bowling_style or '').lower()], 
                    key=lambda p: (p.powerplay_skill + p.death_bowling_skill), reverse=True)
    spinners = sorted([p for p in xi if p.is_spinner or 'spinner' in (p.bowling_style or '').lower()], 
                      key=lambda p: p.middle_overs_skill, reverse=True)
    ars = sorted([p for p in xi if p.role in ['All-rounder', 'Batting All-rounder', 'Bowling All-rounder']], key=lambda p: p.star_rating, reverse=True)

    for over_idx in range(20):
        phase = get_phase(over_idx)
        
        candidates = []
        weights = []
        
        for p in xi:
            # Constraints
            limit = 2 if p.role == 'Batting All-rounder' else 4
            if overs_bowled[p.name] >= limit: continue
            if p.name == prev_bowler_name: continue
            
            # Base Skill for phase
            if phase == 'powerplay':
                skill = p.powerplay_skill
            elif phase == 'middle':
                skill = p.middle_overs_skill
            else:
                skill = p.death_bowling_skill
            
            # Weighting logic: Sharp exponent to favor specialists heavily
            remaining = limit - overs_bowled[p.name]
            weight = (skill ** 3) * (remaining ** 1.2)
            
            is_pacer = not p.is_spinner and 'spinner' not in (p.bowling_style or '').lower()
            is_spinner = p.is_spinner or 'spinner' in (p.bowling_style or '').lower()
            
            # Phase strictly constraints
            if phase == 'powerplay':
                if not is_pacer: weight *= 0.001 # Part-timers/spinners very unlikely in PP
            elif phase == 'death':
                if not is_pacer: weight = 0      # NO non-pacers in Death
                else: weight *= 5.0              # Massive boost for pacers in Death
            elif phase == 'middle':
                if is_spinner:
                    weight *= 2.0 # Favor spinners in Middle
                elif not is_pacer and p.role not in ['All-rounder', 'Batting All-rounder', 'Bowling All-rounder']:
                    weight *= 0.1 # Part-time batsmen unlikely in Middle
            
            candidates.append(p)
            weights.append(max(0, weight))

        if not candidates or sum(weights) == 0:
            # Emergency fallback: 
            # 1. Try to find ANYONE who hasn't reached their limit yet
            absolute_fallbacks = [p for p in xi if overs_bowled[p.name] < (2 if p.role == 'Batting All-rounder' else 4)]
            
            if absolute_fallbacks:
                # Prioritize those who didn't bowl the previous over
                preferred = [p for p in absolute_fallbacks if p.name != prev_bowler_name]
                selected_bowler = random.choice(preferred if preferred else absolute_fallbacks)
            else:
                # 2. Complete overflow: No one has valid overs left. 
                # Pick someone who didn't bowl last, prioritizing pure bowlers.
                fallbacks = [p for p in xi if p.name != prev_bowler_name]
                priority_fallbacks = [p for p in fallbacks if p.role == 'Bowler']
                if not priority_fallbacks:
                    priority_fallbacks = [p for p in fallbacks if p.role != 'Batting All-rounder']
                
                if priority_fallbacks:
                    selected_bowler = random.choice(priority_fallbacks)
                elif fallbacks:
                    selected_bowler = random.choice(fallbacks)
                else:
                    selected_bowler = random.choice(xi)
        else:
            selected_bowler = random.choices(candidates, weights=weights, k=1)[0]
        
        plan.append(selected_bowler.name)
        overs_bowled[selected_bowler.name] += 1
        prev_bowler_name = selected_bowler.name

    return plan, {
        'p1': pacers[0].name if pacers else (xi[0].name if len(xi) > 0 else 'None'),
        'p2': pacers[1].name if len(pacers) > 1 else (xi[1].name if len(xi) > 1 else 'None'),
        'p3': pacers[2].name if len(pacers) > 2 else (xi[2].name if len(xi) > 2 else 'None'),
        'sp': spinners[0].name if spinners else (xi[3].name if len(xi) > 3 else 'None'),
        'ar1': ars[0].name if ars else (xi[4].name if len(xi) > 4 else 'None'),
        'ar2': ars[1].name if len(ars) > 1 else (xi[5].name if len(xi) > 5 else 'None'),
    }


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
    all_rounders   = [p for p in raw_bowling if p.role in ['All-rounder', 'Batting All-rounder', 'Bowling All-rounder']]
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

    # Generate the pre-planned strategy
    bowling_plan, role_map = generate_bowling_strategy(bowling_pool)
    
    # Tracking for dynamic AR adjustments
    ar_stats = { role_map['ar1']: {'runs': 0, 'overs': 0}, role_map['ar2']: {'runs': 0, 'overs': 0} }
    ar_adjustment_made = False

    for over in range(overs_max):
        phase = get_phase(over)
        
        # Phase aggression for batters
        if phase == 'powerplay': phase_aggression = 1.15
        elif phase == 'middle':  phase_aggression = 1.0
        else:                    phase_aggression = 1.25

        # ── DYNAMIC AR ADJUSTMENT (Middle Overs Only) ────────────────
        if phase == 'middle' and not ar_adjustment_made:
            for ar_name in [role_map['ar1'], role_map['ar2']]:
                if ar_name == 'None': continue
                stats = ar_stats.get(ar_name)
                if stats and stats['overs'] >= 1:
                    avg_runs = stats['runs'] / stats['overs']
                    if avg_runs >= 12: # Expensive - swap with anyone who has capacity
                        other_ar = role_map['ar2'] if ar_name == role_map['ar1'] else role_map['ar1']
                        
                        # Find potential replacements from the entire pool
                        for i in range(over + 1, 15):
                            if bowling_plan[i] == ar_name:
                                # Prioritize the other AR, then any bowler with room
                                for candidate in [other_ar] + [p.name for p in bowling_pool]:
                                    if candidate == 'None' or candidate == ar_name: continue
                                    
                                    cand_p = next((p for p in bowling_pool if p.name == candidate), None)
                                    if not cand_p: continue
                                    
                                    limit = 2 if cand_p.role == 'Batting All-rounder' else 4
                                    if bowling_plan.count(candidate) < limit:
                                        bowling_plan[i] = candidate
                                        ar_adjustment_made = True
                                        break
                                if ar_adjustment_made: break
                        if ar_adjustment_made: break
                    elif avg_runs <= 6 and stats['overs'] == 1:
                        # Good performance - try to give them more overs by taking from others if they have room
                        other_ar = role_map['ar2'] if ar_name == role_map['ar1'] else role_map['ar1']
                        current_overs = bowling_plan.count(ar_name)
                        limit = 2 if next(p for p in bowling_pool if p.name == ar_name).role == 'Batting All-rounder' else 4
                        
                        if current_overs < limit:
                            for i in range(over + 1, 15):
                                if bowling_plan[i] == other_ar:
                                    bowling_plan[i] = ar_name
                                    ar_adjustment_made = True
                                    break
                        if ar_adjustment_made: break

        # ── BOWLER SELECTION ─────────────────────────────────────────
        bowler_name = bowling_plan[over]
        bowler = next(p for p in bowling_pool if p.name == bowler_name)
        
        recent_bowlers.append(bowler.name)
        if bowler.name not in scorecard['bowlers']:
            scorecard['bowlers'][bowler.name] = {'overs': 0.0, 'runs': 0, 'wickets': 0}
        
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

        # Update AR stats for dynamic adjustment
        if bowler.name in ar_stats:
            ar_stats[bowler.name]['overs'] += 1
            ar_stats[bowler.name]['runs'] += over_runs

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
        'bowling_strategy': {
            'team_a': generate_bowling_strategy(players_a)[0],
            'team_b': generate_bowling_strategy(players_b)[0],
            'roles_a': generate_bowling_strategy(players_a)[1],
            'roles_b': generate_bowling_strategy(players_b)[1],
        },
        'match_meta': {
            'team_a_strength': strength_a,
            'team_b_strength': strength_b,
            'strength_diff': diff,
            'match_type': match_type,
            'match_description': match_desc,
            'batting_first_team': first_bat_team.name,
        }
    }
