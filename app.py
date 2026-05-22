"""
Cricket Score Calculator App - V2 with Player Tracking
A free, user-friendly cricket scoring app built with Streamlit.
"""

import streamlit as st
import random

# Page configuration
st.set_page_config(
    page_title="Cricket Score",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e7e34;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
        font-weight: bold;
        height: 3rem;
    }
    .striker-row {
        background-color: rgba(40, 167, 69, 0.15);
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .non-striker-row {
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #6c757d;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    defaults = {
        'setup_step': 'teams',  # 'teams', 'players', 'opening', 'playing'
        'team1_name': 'Team A',
        'team2_name': 'Team B',
        'total_overs': 6,
        'players_per_team': 11,
        'team1_players': [],
        'team2_players': [],
        'batting_team': 'Team A',
        'bowling_team': 'Team B',
        'runs': 0,
        'wickets': 0,
        'balls': 0,
        'extras': 0,
        'ball_history': [],
        'innings': 1,
        'team1_score': None,
        'team2_score': None,
        'target': None,
        'match_complete': False,
        'striker': None,
        'non_striker': None,
        'batsmen_stats': {},  # {player_name: {runs, balls, fours, sixes, out}}
        'next_batsman_index': 0,
        'awaiting_new_batsman': False,
        'current_bowler': None,
        'bowlers_stats': {},  # {bowler_name: {balls, runs, wickets, maidens, overs_bowled}}
        'awaiting_new_bowler': False,
        'over_runs': 0,  # Track runs in current over for maiden detection
        'consecutive_wides': 0,  # Track wides in a row for custom wide rule
        'toss_winner': None,  # Which team won the toss
        'toss_decision': None,  # 'Bat' or 'Bowl'
        'toss_done': False,  # Whether the coin has been flipped
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def calculate_overs(balls):
    """Convert balls into overs.balls format"""
    return f"{balls // 6}.{balls % 6}"


def calculate_run_rate(runs, balls):
    """Calculate current run rate"""
    if balls == 0:
        return 0.0
    overs = balls / 6
    return round(runs / overs, 2)


def calculate_required_run_rate(target, current_runs, total_overs, balls_bowled):
    """Calculate required run rate"""
    runs_needed = target - current_runs
    balls_remaining = (total_overs * 6) - balls_bowled
    if balls_remaining <= 0:
        return 0.0
    overs_remaining = balls_remaining / 6
    return round(runs_needed / overs_remaining, 2)


def get_strike_rate(runs, balls):
    """Calculate batsman's strike rate"""
    if balls == 0:
        return 0.0
    return round((runs / balls) * 100, 2)


def get_batting_team_players():
    """Get the list of players from the currently batting team"""
    if st.session_state.batting_team == st.session_state.team1_name:
        return st.session_state.team1_players
    return st.session_state.team2_players


def init_batsman_stats(player_name):
    """Initialize stats for a batsman"""
    if player_name not in st.session_state.batsmen_stats:
        st.session_state.batsmen_stats[player_name] = {
            'runs': 0,
            'balls': 0,
            'fours': 0,
            'sixes': 0,
            'out': False,
            'on_field': True,
        }

def get_bowling_team_players():
    """Get the list of players from the currently bowling team"""
    if st.session_state.bowling_team == st.session_state.team1_name:
        return st.session_state.team1_players
    return st.session_state.team2_players


def init_bowler_stats(player_name):
    """Initialize stats for a bowler"""
    if player_name not in st.session_state.bowlers_stats:
        st.session_state.bowlers_stats[player_name] = {
            'balls': 0,
            'runs': 0,
            'wickets': 0,
            'maidens': 0,
        }

def add_ball(runs_scored, is_wicket=False, extra_type=None):
    """Add a ball to the game"""

    # ===== CUSTOM EXTRAS RULES =====
    # Wide: count consecutive wides. Every even-numbered wide (2nd, 4th...) = 1 run, odd = 0 runs.
    # No Ball: 0 runs, ball does not count.
    if extra_type == 'Wide':
        st.session_state.consecutive_wides += 1
        runs_scored = 1 if st.session_state.consecutive_wides % 2 == 0 else 0
    elif extra_type == 'No Ball':
        runs_scored = 0
    else:
        # Any legal delivery resets the consecutive wide counter
        st.session_state.consecutive_wides = 0

    ball_data = {
        'over': calculate_overs(st.session_state.balls),
        'runs': runs_scored,
        'wicket': is_wicket,
        'extra': extra_type,
        'striker': st.session_state.striker,
        'bowler': st.session_state.current_bowler,
    }

    # Update bowler stats
    bowler = st.session_state.current_bowler
    if bowler and bowler in st.session_state.bowlers_stats:
        st.session_state.bowlers_stats[bowler]['runs'] += runs_scored
        if extra_type not in ['Wide', 'No Ball']:
            st.session_state.bowlers_stats[bowler]['balls'] += 1
            st.session_state.over_runs += runs_scored
        else:
            st.session_state.over_runs += runs_scored
        if is_wicket:
            st.session_state.bowlers_stats[bowler]['wickets'] += 1

    st.session_state.runs += runs_scored

    # Update batsman stats
    striker = st.session_state.striker
    if striker and striker in st.session_state.batsmen_stats:
        if extra_type not in ['Wide', 'No Ball']:
            st.session_state.batsmen_stats[striker]['balls'] += 1
        if extra_type is None:
            st.session_state.batsmen_stats[striker]['runs'] += runs_scored
            if runs_scored == 4:
                st.session_state.batsmen_stats[striker]['fours'] += 1
            elif runs_scored == 6:
                st.session_state.batsmen_stats[striker]['sixes'] += 1

    # Wides and no-balls don't count as a legal ball
    if extra_type in ['Wide', 'No Ball']:
        st.session_state.extras += 1
    else:
        st.session_state.balls += 1

    if is_wicket:
        st.session_state.wickets += 1

        if striker and striker in st.session_state.batsmen_stats:
            st.session_state.batsmen_stats[striker]['out'] = True
            st.session_state.batsmen_stats[striker]['on_field'] = False
        st.session_state.awaiting_new_batsman = True

    # Rotate strike on odd runs (legal deliveries only, except wickets)
    if not is_wicket and extra_type not in ['Wide', 'No Ball'] and runs_scored % 2 == 1:
        st.session_state.striker, st.session_state.non_striker = (
            st.session_state.non_striker, st.session_state.striker
        )

    # End of over - rotate strike, check maiden, prompt new bowler
    if st.session_state.balls > 0 and st.session_state.balls % 6 == 0 and extra_type not in ['Wide', 'No Ball']:

        if st.session_state.over_runs == 0 and bowler:
            st.session_state.bowlers_stats[bowler]['maidens'] += 1

        st.session_state.over_runs = 0

        if not st.session_state.awaiting_new_batsman:
            st.session_state.striker, st.session_state.non_striker = (
                st.session_state.non_striker, st.session_state.striker
            )

        max_balls = st.session_state.total_overs * 6
        if st.session_state.balls < max_balls:
            st.session_state.awaiting_new_bowler = True

    st.session_state.ball_history.append(ball_data)

    # Check if innings is over
    max_balls = st.session_state.total_overs * 6
    batting_team_size = len(get_batting_team_players())

    if (st.session_state.balls >= max_balls or
            st.session_state.wickets >= batting_team_size - 1):
        end_innings()

    # Check if chasing team won
    if (st.session_state.innings == 2 and
            st.session_state.target is not None and
            st.session_state.runs >= st.session_state.target):
        end_match()


def undo_last_ball():
    """Undo the last recorded ball"""
    if not st.session_state.ball_history:
        return

    last_ball = st.session_state.ball_history.pop()
    st.session_state.runs -= last_ball['runs']

    # Revert bowler stats
    bowler = last_ball.get('bowler')
    if bowler and bowler in st.session_state.bowlers_stats:
        st.session_state.bowlers_stats[bowler]['runs'] -= last_ball['runs']
        if last_ball['extra'] not in ['Wide', 'No Ball']:
            st.session_state.bowlers_stats[bowler]['balls'] -= 1
        if last_ball['wicket']:
            st.session_state.bowlers_stats[bowler]['wickets'] -= 1

    # Revert batsman stats
    striker = last_ball.get('striker')
    if striker and striker in st.session_state.batsmen_stats:
        if last_ball['extra'] not in ['Wide', 'No Ball']:
            st.session_state.batsmen_stats[striker]['balls'] -= 1
        if last_ball['extra'] is None:
            st.session_state.batsmen_stats[striker]['runs'] -= last_ball['runs']
            if last_ball['runs'] == 4:
                st.session_state.batsmen_stats[striker]['fours'] -= 1
            elif last_ball['runs'] == 6:
                st.session_state.batsmen_stats[striker]['sixes'] -= 1

    if last_ball['extra'] in ['Wide', 'No Ball']:
        st.session_state.extras -= 1
    else:
        st.session_state.balls -= 1

    if last_ball['wicket']:
        st.session_state.wickets -= 1
        # Restore the batsman
        if striker and striker in st.session_state.batsmen_stats:
            st.session_state.batsmen_stats[striker]['out'] = False
            st.session_state.batsmen_stats[striker]['on_field'] = True
        st.session_state.awaiting_new_batsman = False
        st.session_state.striker = striker

    # Recalculate consecutive_wides by walking back through history
    count = 0
    for ball in reversed(st.session_state.ball_history):
        if ball['extra'] == 'Wide':
            count += 1
        else:
            break
    st.session_state.consecutive_wides = count

    # Also revert the awaiting_new_bowler flag if we undid the last ball of an over
    st.session_state.awaiting_new_bowler = False


def end_innings():
    """End the current innings"""
    if st.session_state.innings == 1:
        st.session_state.team1_score = {
            'runs': st.session_state.runs,
            'wickets': st.session_state.wickets,
            'overs': calculate_overs(st.session_state.balls),
            'team': st.session_state.batting_team,
            'bowling_team': st.session_state.bowling_team,
            'batsmen_stats': dict(st.session_state.batsmen_stats),
            'bowlers_stats': dict(st.session_state.bowlers_stats),
        }
        st.session_state.target = st.session_state.runs + 1
        # Switch teams
        if st.session_state.batting_team == st.session_state.team1_name:
            st.session_state.batting_team = st.session_state.team2_name
            st.session_state.bowling_team = st.session_state.team1_name
        else:
            st.session_state.batting_team = st.session_state.team1_name
            st.session_state.bowling_team = st.session_state.team2_name

        # Reset for second innings
        st.session_state.runs = 0
        st.session_state.wickets = 0
        st.session_state.balls = 0
        st.session_state.extras = 0
        st.session_state.ball_history = []
        st.session_state.innings = 2
        st.session_state.batsmen_stats = {}
        st.session_state.bowlers_stats = {}
        st.session_state.current_bowler = None
        st.session_state.awaiting_new_bowler = False
        st.session_state.over_runs = 0
        st.session_state.striker = None
        st.session_state.non_striker = None
        st.session_state.next_batsman_index = 0
        st.session_state.awaiting_new_batsman = False
        st.session_state.setup_step = 'opening'
    else:
        end_match()


def end_match():
    """End the match"""
    st.session_state.team2_score = {
        'runs': st.session_state.runs,
        'wickets': st.session_state.wickets,
        'overs': calculate_overs(st.session_state.balls),
        'team': st.session_state.batting_team,
        'bowling_team': st.session_state.bowling_team,
        'batsmen_stats': dict(st.session_state.batsmen_stats),
        'bowlers_stats': dict(st.session_state.bowlers_stats),
    }
    st.session_state.match_complete = True


def reset_match():
    """Reset the entire match"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


# Header
st.markdown('<div class="main-header">🏏 Cricket Score</div>',
            unsafe_allow_html=True)

# ============ SETUP STEP 1: TEAMS ============
if st.session_state.setup_step == 'teams':
    st.subheader("⚙️ Step 1: Match Setup")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.team1_name = st.text_input(
            "Team 1 Name", value=st.session_state.team1_name)
    with col2:
        st.session_state.team2_name = st.text_input(
            "Team 2 Name", value=st.session_state.team2_name)

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.total_overs = st.number_input(
            "Total Overs", min_value=1, max_value=50,
            value=st.session_state.total_overs)
    with col2:
        st.session_state.players_per_team = st.number_input(
            "Players per Team", min_value=2, max_value=15,
            value=st.session_state.players_per_team)

    if st.button("➡️ Next: Coin Toss", type="primary"):
        st.session_state.setup_step = 'toss'
        st.rerun()

# ============ SETUP STEP: COIN TOSS ============
elif st.session_state.setup_step == 'toss':
    st.subheader("🪙 Coin Toss")

    if not st.session_state.toss_done:
        st.markdown(f"### {st.session_state.team1_name}  🆚  {st.session_state.team2_name}")
        st.markdown("<div style='text-align:center; font-size:5rem;'>🪙</div>", unsafe_allow_html=True)
        st.info("Click the button below to flip the coin!")

        if st.button("🪙 Flip the Coin!", type="primary"):
            winner = random.choice([st.session_state.team1_name, st.session_state.team2_name])
            st.session_state.toss_winner = winner
            st.session_state.toss_done = True
            st.rerun()
    else:
        st.success(f"🎉 **{st.session_state.toss_winner}** won the toss!")
        st.markdown(f"**{st.session_state.toss_winner}**, what would you like to do?")

        decision = st.radio(
            "Choose:",
            ["Bat", "Bowl"],
            horizontal=True
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Re-flip Coin"):
                st.session_state.toss_done = False
                st.session_state.toss_winner = None
                st.rerun()
        with col2:
            if st.button("➡️ Next: Add Players", type="primary"):
                st.session_state.toss_decision = decision
                # Set batting/bowling based on toss decision
                if decision == "Bat":
                    st.session_state.batting_team = st.session_state.toss_winner
                else:
                    # Toss winner bowls, so the other team bats
                    st.session_state.batting_team = (
                        st.session_state.team2_name
                        if st.session_state.toss_winner == st.session_state.team1_name
                        else st.session_state.team1_name
                    )
                st.session_state.bowling_team = (
                    st.session_state.team2_name
                    if st.session_state.batting_team == st.session_state.team1_name
                    else st.session_state.team1_name
                )
                st.session_state.setup_step = 'players'
                st.rerun()

# ============ SETUP STEP 2: PLAYERS ============
elif st.session_state.setup_step == 'players':
    st.subheader("👥 Step 2: Add Players")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 🏏 {st.session_state.team1_name}")
        team1_players_input = []
        for i in range(st.session_state.players_per_team):
            default_name = (
                st.session_state.team1_players[i]
                if i < len(st.session_state.team1_players)
                else f"Player {i+1}"
            )
            name = st.text_input(
                f"Player {i+1}",
                value=default_name,
                key=f"t1_player_{i}"
            )
            team1_players_input.append(name)

    with col2:
        st.markdown(f"### 🏏 {st.session_state.team2_name}")
        team2_players_input = []
        for i in range(st.session_state.players_per_team):
            default_name = (
                st.session_state.team2_players[i]
                if i < len(st.session_state.team2_players)
                else f"Player {i+1}"
            )
            name = st.text_input(
                f"Player {i+1}",
                value=default_name,
                key=f"t2_player_{i}"
            )
            team2_players_input.append(name)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Teams"):
            st.session_state.setup_step = 'teams'
            st.session_state.toss_done = False
            st.session_state.toss_winner = None
            st.session_state.toss_decision = None
            st.rerun()
    with col2:
        if st.button("➡️ Next: Choose Openers", type="primary"):
            st.session_state.team1_players = team1_players_input
            st.session_state.team2_players = team2_players_input
            st.session_state.setup_step = 'opening'
            st.rerun()

# ============ SETUP STEP 3: OPENING BATSMEN ============
elif st.session_state.setup_step == 'opening':
    if st.session_state.innings == 1:
        st.subheader("🎯 Choose Opening Players")
        st.success(
            f"🪙 {st.session_state.toss_winner} won the toss and chose to "
            f"{st.session_state.toss_decision.lower()}."
        )
    else:
        st.subheader(f"🎯 Innings 2: Choose Opening Batsmen for {st.session_state.batting_team}")
        st.info(f"Target: **{st.session_state.target}** runs in {st.session_state.total_overs} overs")

    batting_players = get_batting_team_players()

    st.markdown(f"**Batting Team: {st.session_state.batting_team}**")

    col1, col2 = st.columns(2)
    with col1:
        striker = st.selectbox(
            "🏏 Striker (on strike)",
            batting_players,
            index=0
        )
    with col2:
        non_striker_options = [p for p in batting_players if p != striker]
        non_striker = st.selectbox(
            "🏃 Non-Striker",
            non_striker_options,
            index=0
        )

    bowling_players = get_bowling_team_players()
    opening_bowler = st.selectbox(
        "⚾ Opening Bowler",
        bowling_players,
        index=0
    )

    if st.button("🚀 Start Match!", type="primary"):
        st.session_state.striker = striker
        st.session_state.non_striker = non_striker
        st.session_state.current_bowler = opening_bowler
        init_batsman_stats(striker)
        init_batsman_stats(non_striker)
        init_bowler_stats(opening_bowler)
        # Set next batsman index
        st.session_state.next_batsman_index = 2
        st.session_state.setup_step = 'playing'
        st.rerun()

# ============ MATCH COMPLETE ============
elif st.session_state.match_complete:
    st.balloons()
    st.header("🏆 Match Complete!")

    t1 = st.session_state.team1_score
    t2 = st.session_state.team2_score

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {t1['team']}")
        st.markdown(f"## {t1['runs']}/{t1['wickets']}")
        st.markdown(f"**Overs:** {t1['overs']}")

    with col2:
        st.markdown(f"### {t2['team']}")
        st.markdown(f"## {t2['runs']}/{t2['wickets']}")
        st.markdown(f"**Overs:** {t2['overs']}")

    st.markdown("---")

    # Determine winner
    if t1['runs'] > t2['runs']:
        margin = t1['runs'] - t2['runs']
        st.success(f"🎉 **{t1['team']} won by {margin} runs!**")
    elif t2['runs'] > t1['runs']:
        wickets_left = (st.session_state.players_per_team - 1) - t2['wickets']
        st.success(f"🎉 **{t2['team']} won by {wickets_left} wickets!**")
    else:
        st.warning("🤝 **Match Tied!**")

    # Show full scorecards
    st.markdown("---")
    st.subheader("📊 Full Scorecards")

    for innings_score in [t1, t2]:
        st.markdown(f"### {innings_score['team']} - {innings_score['runs']}/{innings_score['wickets']} ({innings_score['overs']} overs)")

        # Batting scorecard
        st.markdown("**🏏 Batting**")
        if innings_score.get('batsmen_stats'):
            data = []
            for name, stats in innings_score['batsmen_stats'].items():
                status = "out" if stats['out'] else "not out"
                sr = get_strike_rate(stats['runs'], stats['balls'])
                data.append({
                    'Batsman': name,
                    'Status': status,
                    'Runs': stats['runs'],
                    'Balls': stats['balls'],
                    '4s': stats['fours'],
                    '6s': stats['sixes'],
                    'SR': sr,
                })
            st.dataframe(data, use_container_width=True, hide_index=True)

        # Bowling scorecard
        bowling_team_name = innings_score.get('bowling_team', 'Bowling Team')
        st.markdown(f"**⚾ Bowling ({bowling_team_name})**")
        if innings_score.get('bowlers_stats'):
            bowl_data = []
            for name, stats in innings_score['bowlers_stats'].items():
                overs_str = f"{stats['balls'] // 6}.{stats['balls'] % 6}"
                econ = round((stats['runs'] / (stats['balls'] / 6)), 2) if stats['balls'] > 0 else 0.0
                bowl_data.append({
                    'Bowler': name,
                    'Overs': overs_str,
                    'Runs': stats['runs'],
                    'Wickets': stats['wickets'],
                    'Maidens': stats['maidens'],
                    'Econ': econ,
                })
            st.dataframe(bowl_data, use_container_width=True, hide_index=True)
        else:
            st.info("No bowling stats recorded")

        st.markdown("---")

    if st.button("🆕 Start New Match", type="primary"):
        reset_match()
        st.rerun()

# ============ ACTIVE MATCH - SCORING ============
elif st.session_state.setup_step == 'playing':

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Match Info")
        st.success(f"**{st.session_state.team1_name}** vs **{st.session_state.team2_name}**")
        st.info(f"Format: {st.session_state.total_overs} overs")
        st.info(f"Innings: {st.session_state.innings}/2")
        st.info(f"Batting: {st.session_state.batting_team}")
        st.info(f"Bowling: {st.session_state.bowling_team}")
        if st.session_state.toss_winner:
            st.caption(
                f"🪙 {st.session_state.toss_winner} won the toss & chose to "
                f"{st.session_state.toss_decision.lower()}"
            )

        st.markdown("---")
        if st.button("🔄 Reset Match"):
            reset_match()
            st.rerun()

    # Top stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Batting", st.session_state.batting_team)
    with col2:
        st.metric("Score", f"{st.session_state.runs}/{st.session_state.wickets}")
    with col3:
        st.metric("Overs", f"{calculate_overs(st.session_state.balls)}/{st.session_state.total_overs}")
    with col4:
        crr = calculate_run_rate(st.session_state.runs, st.session_state.balls)
        st.metric("Run Rate", crr)

    # Target info if 2nd innings
    if st.session_state.innings == 2 and st.session_state.target:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        runs_needed = st.session_state.target - st.session_state.runs
        balls_remaining = (st.session_state.total_overs * 6) - st.session_state.balls
        rrr = calculate_required_run_rate(
            st.session_state.target,
            st.session_state.runs,
            st.session_state.total_overs,
            st.session_state.balls
        )
        with col1:
            st.metric("Target", st.session_state.target)
        with col2:
            st.metric("Runs Needed", max(0, runs_needed))
        with col3:
            st.metric("Balls Left", max(0, balls_remaining))
        with col4:
            st.metric("Required RR", rrr)

    st.markdown("---")

    # ===== CURRENT BOWLER =====
    st.subheader("⚾ Current Bowler")

    if st.session_state.awaiting_new_bowler:
        st.warning("⚠️ End of over! Select the next bowler.")
        bowling_players = get_bowling_team_players()
        # Can't bowl consecutive overs
        available_bowlers = [p for p in bowling_players if p != st.session_state.current_bowler]
        new_bowler = st.selectbox("Select next bowler:", available_bowlers, key="new_bowler_select")
        if st.button("✅ Confirm New Bowler", type="primary"):
            st.session_state.current_bowler = new_bowler
            init_bowler_stats(new_bowler)
            st.session_state.awaiting_new_bowler = False
            st.rerun()
    else:
        bowler = st.session_state.current_bowler
        b_stats = st.session_state.bowlers_stats.get(bowler, {})
        overs_bowled = f"{b_stats.get('balls', 0) // 6}.{b_stats.get('balls', 0) % 6}"
        econ = round((b_stats.get('runs', 0) / (b_stats.get('balls', 0) / 6)), 2) if b_stats.get('balls', 0) > 0 else 0.0
        st.info(
            f"**⚾ {bowler}** | Overs: **{overs_bowled}** | "
            f"Runs: **{b_stats.get('runs', 0)}** | "
            f"Wickets: **{b_stats.get('wickets', 0)}** | "
            f"Maidens: **{b_stats.get('maidens', 0)}** | "
            f"Econ: **{econ}**"
        )

    st.markdown("---")

    # ===== BATSMEN ON FIELD =====
    st.subheader("🏏 Batsmen on Field")

    # Handle new batsman selection after wicket
    if st.session_state.awaiting_new_batsman:
        st.warning("⚠️ Wicket fallen! Select the next batsman.")
        batting_players = get_batting_team_players()
        available_batsmen = [
            p for p in batting_players
            if p != st.session_state.non_striker
            and (p not in st.session_state.batsmen_stats
                 or not st.session_state.batsmen_stats[p]['out'])
        ]

        if available_batsmen:
            new_batsman = st.selectbox("Select new batsman:", available_batsmen)
            if st.button("✅ Confirm New Batsman", type="primary"):
                st.session_state.striker = new_batsman
                init_batsman_stats(new_batsman)
                st.session_state.awaiting_new_batsman = False
                st.rerun()
        else:
            st.error("No more batsmen available - innings should end")
    else:
        # Display current batsmen
        striker_stats = st.session_state.batsmen_stats.get(st.session_state.striker, {})
        non_striker_stats = st.session_state.batsmen_stats.get(st.session_state.non_striker, {})

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="striker-row">
            <strong>🏏 {st.session_state.striker} *</strong> (on strike)<br>
            Runs: <b>{striker_stats.get('runs', 0)}</b> ({striker_stats.get('balls', 0)} balls)<br>
            4s: {striker_stats.get('fours', 0)} | 6s: {striker_stats.get('sixes', 0)} |
            SR: {get_strike_rate(striker_stats.get('runs', 0), striker_stats.get('balls', 0))}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="non-striker-row">
            <strong>🏃 {st.session_state.non_striker}</strong> (non-striker)<br>
            Runs: <b>{non_striker_stats.get('runs', 0)}</b> ({non_striker_stats.get('balls', 0)} balls)<br>
            4s: {non_striker_stats.get('fours', 0)} | 6s: {non_striker_stats.get('sixes', 0)} |
            SR: {get_strike_rate(non_striker_stats.get('runs', 0), non_striker_stats.get('balls', 0))}
            </div>
            """, unsafe_allow_html=True)

        # Swap strike button
        if st.button("🔄 Swap Strike"):
            st.session_state.striker, st.session_state.non_striker = (
                st.session_state.non_striker, st.session_state.striker
            )
            st.rerun()

    st.markdown("---")

    # Scoring buttons (only show if not awaiting new batsman or new bowler)
    if not st.session_state.awaiting_new_batsman and not st.session_state.awaiting_new_bowler:
        st.subheader("📝 Add Score")

        st.markdown("**Runs Scored:**")
        cols = st.columns(7)
        run_options = [0, 1, 2, 3, 4, 5, 6]
        for i, runs in enumerate(run_options):
            with cols[i]:
                label = f"{runs} Run" if runs <= 1 else f"{runs} Runs"
                if runs == 4:
                    label = "4️⃣ FOUR"
                elif runs == 6:
                    label = "6️⃣ SIX"
                if st.button(label, key=f"run_{runs}"):
                    add_ball(runs)
                    st.rerun()

        st.markdown("**Special:**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🎯 WICKET", type="primary"):
                add_ball(0, is_wicket=True)
                st.rerun()
        with col2:
            if st.button("Wide"):
                add_ball(0, extra_type='Wide')
                st.rerun()
        with col3:
            if st.button("No Ball"):
                add_ball(0, extra_type='No Ball')
                st.rerun()
        with col4:
            if st.button("↩️ UNDO"):
                undo_last_ball()
                st.rerun()

        # Manual controls
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏁 End Innings"):
                end_innings()
                st.rerun()
        with col2:
            if st.button("🛑 End Match"):
                end_match()
                st.rerun()
    # ===== BOWLING SCORECARD =====
    st.subheader("⚾ Bowling Figures")
    if st.session_state.bowlers_stats:
        bowling_data = []
        for name, stats in st.session_state.bowlers_stats.items():
            overs_str = f"{stats['balls'] // 6}.{stats['balls'] % 6}"
            econ = round((stats['runs'] / (stats['balls'] / 6)), 2) if stats['balls'] > 0 else 0.0
            bowling_data.append({
                'Bowler': name,
                'Overs': overs_str,
                'Runs': stats['runs'],
                'Wickets': stats['wickets'],
                'Maidens': stats['maidens'],
                'Econ': econ,
            })
        st.dataframe(bowling_data, use_container_width=True, hide_index=True)
    else:
        st.info("No bowling stats yet")

    # ===== SCORECARD =====
    st.markdown("---")
    st.subheader("📊 Batting Scorecard")


    if st.session_state.batsmen_stats:
        scorecard_data = []
        for name, stats in st.session_state.batsmen_stats.items():
            if stats['out']:
                status = "out"
            elif name == st.session_state.striker:
                status = "batting *"
            elif name == st.session_state.non_striker:
                status = "batting"
            else:
                status = "-"

            sr = get_strike_rate(stats['runs'], stats['balls'])
            scorecard_data.append({
                'Batsman': name,
                'Status': status,
                'Runs': stats['runs'],
                'Balls': stats['balls'],
                '4s': stats['fours'],
                '6s': stats['sixes'],
                'SR': sr,
            })
        st.dataframe(scorecard_data, use_container_width=True, hide_index=True)
    else:
        st.info("No batting stats yet")

    # Ball-by-ball history
    if st.session_state.ball_history:
        with st.expander("📜 Recent Balls"):
            recent_balls = st.session_state.ball_history[-12:]
            for ball in reversed(recent_balls):
                entry = f"Over {ball['over']}: {ball.get('striker', '?')} - {ball['runs']} run(s)"
                if ball['wicket']:
                    entry += " 🎯 WICKET"
                if ball['extra']:
                    entry += f" ({ball['extra']})"
                st.text(entry)

    # Show first innings summary if in second innings
    if st.session_state.innings == 2 and st.session_state.team1_score:
        with st.expander("📊 First Innings Summary"):
            t1 = st.session_state.team1_score
            st.info(f"**{t1['team']}**: {t1['runs']}/{t1['wickets']} in {t1['overs']} overs")
            if t1.get('batsmen_stats'):
                data = []
                for name, stats in t1['batsmen_stats'].items():
                    status = "out" if stats['out'] else "not out"
                    data.append({
                        'Batsman': name,
                        'Status': status,
                        'Runs': stats['runs'],
                        'Balls': stats['balls'],
                        '4s': stats['fours'],
                        '6s': stats['sixes'],
                        'SR': get_strike_rate(stats['runs'], stats['balls']),
                    })
                st.dataframe(data, use_container_width=True, hide_index=True)


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Built with ❤️ | Free to use forever 🏏"
    "</div>",
    unsafe_allow_html=True
)