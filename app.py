"""
Cricket Score Calculator App
A free, user-friendly cricket scoring app built with Streamlit.
"""

import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Cricket Score Calculator",
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
    .score-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1e7e34;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .stButton button {
        width: 100%;
        font-weight: bold;
        height: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    defaults = {
        'team1_name': 'Team A',
        'team2_name': 'Team B',
        'total_overs': 20,
        'batting_team': 'Team A',
        'runs': 0,
        'wickets': 0,
        'balls': 0,
        'extras': 0,
        'ball_history': [],
        'innings': 1,
        'team1_score': None,
        'team2_score': None,
        'target': None,
        'match_started': False,
        'match_complete': False,
        'current_batsmen': {'striker': 'Batsman 1', 'non_striker': 'Batsman 2'},
        'batsmen_stats': {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def calculate_overs(balls):
    """Convert balls into overs.balls format (e.g., 13 balls = 2.1 overs)"""
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


def add_ball(runs_scored, is_wicket=False, extra_type=None):
    """Add a ball to the game"""
    ball_data = {
        'over': calculate_overs(st.session_state.balls),
        'runs': runs_scored,
        'wicket': is_wicket,
        'extra': extra_type,
    }

    st.session_state.runs += runs_scored

    # Wides and no-balls don't count as a legal ball
    if extra_type in ['Wide', 'No Ball']:
        st.session_state.extras += 1
    else:
        st.session_state.balls += 1

    if is_wicket:
        st.session_state.wickets += 1

    st.session_state.ball_history.append(ball_data)

    # Check if innings is over
    max_balls = st.session_state.total_overs * 6
    if st.session_state.balls >= max_balls or st.session_state.wickets >= 10:
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

    if last_ball['extra'] in ['Wide', 'No Ball']:
        st.session_state.extras -= 1
    else:
        st.session_state.balls -= 1

    if last_ball['wicket']:
        st.session_state.wickets -= 1


def end_innings():
    """End the current innings"""
    if st.session_state.innings == 1:
        st.session_state.team1_score = {
            'runs': st.session_state.runs,
            'wickets': st.session_state.wickets,
            'overs': calculate_overs(st.session_state.balls),
            'team': st.session_state.batting_team,
        }
        st.session_state.target = st.session_state.runs + 1
        # Switch teams
        st.session_state.batting_team = (
            st.session_state.team2_name
            if st.session_state.batting_team == st.session_state.team1_name
            else st.session_state.team1_name
        )
        st.session_state.runs = 0
        st.session_state.wickets = 0
        st.session_state.balls = 0
        st.session_state.extras = 0
        st.session_state.ball_history = []
        st.session_state.innings = 2
    else:
        end_match()


def end_match():
    """End the match"""
    st.session_state.team2_score = {
        'runs': st.session_state.runs,
        'wickets': st.session_state.wickets,
        'overs': calculate_overs(st.session_state.balls),
        'team': st.session_state.batting_team,
    }
    st.session_state.match_complete = True


def reset_match():
    """Reset the entire match"""
    keys_to_reset = [
        'runs', 'wickets', 'balls', 'extras', 'ball_history',
        'innings', 'team1_score', 'team2_score', 'target',
        'match_started', 'match_complete'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    init_session_state()


# Header
st.markdown('<div class="main-header">🏏 Cricket Score Calculator</div>',
            unsafe_allow_html=True)

# Sidebar - Match setup
with st.sidebar:
    st.header("⚙️ Match Setup")

    if not st.session_state.match_started:
        st.session_state.team1_name = st.text_input(
            "Team 1 Name", value=st.session_state.team1_name)
        st.session_state.team2_name = st.text_input(
            "Team 2 Name", value=st.session_state.team2_name)
        st.session_state.total_overs = st.number_input(
            "Total Overs", min_value=1, max_value=50,
            value=st.session_state.total_overs)

        batting_first = st.radio(
            "Who bats first?",
            [st.session_state.team1_name, st.session_state.team2_name]
        )

        if st.button("🚀 Start Match", type="primary"):
            st.session_state.batting_team = batting_first
            st.session_state.match_started = True
            st.rerun()
    else:
        st.success(f"Match: {st.session_state.team1_name} vs {st.session_state.team2_name}")
        st.info(f"Format: {st.session_state.total_overs} overs")
        st.info(f"Innings: {st.session_state.innings}/2")

        if st.button("🔄 Reset Match"):
            reset_match()
            st.rerun()

    st.markdown("---")
    st.markdown("### 📖 Quick Guide")
    st.markdown("""
    - Click run buttons to add runs
    - Use **Wicket** for dismissals
    - Use **Extras** for wides/no-balls
    - **Undo** corrects mistakes
    """)


# Main content
if not st.session_state.match_started:
    st.info("👈 Please set up your match in the sidebar to begin scoring.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - Live score tracking
        - Run rate calculations
        - Wicket tracking
        - Extras (wides, no-balls)
        - Undo button for corrections
        """)
    with col2:
        st.markdown("### 📊 Match Stats")
        st.markdown("""
        - Current Run Rate (CRR)
        - Required Run Rate (RRR)
        - Ball-by-ball history
        - Target calculation
        - Innings comparison
        """)
    with col3:
        st.markdown("### 🆓 Free Forever")
        st.markdown("""
        - No ads
        - No login required
        - Works on mobile
        - Open source
        - Deploy free
        """)

elif st.session_state.match_complete:
    # Match complete - show results
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
        wickets_left = 10 - t2['wickets']
        st.success(f"🎉 **{t2['team']} won by {wickets_left} wickets!**")
    else:
        st.warning("🤝 **Match Tied!**")

    if st.button("🆕 Start New Match", type="primary"):
        reset_match()
        st.rerun()

else:
    # Active match - scoring interface
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

    # Scoring buttons
    st.subheader("📝 Add Score")

    # Runs section
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

    # Wickets and extras
    st.markdown("**Special:**")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🎯 WICKET", type="primary"):
            add_ball(0, is_wicket=True)
            st.rerun()

    with col2:
        if st.button("Wide (+1)"):
            add_ball(1, extra_type='Wide')
            st.rerun()

    with col3:
        if st.button("No Ball (+1)"):
            add_ball(1, extra_type='No Ball')
            st.rerun()

    with col4:
        if st.button("Bye (+1)"):
            add_ball(1, extra_type='Bye')
            st.rerun()

    with col5:
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

    # Ball-by-ball history
    if st.session_state.ball_history:
        st.markdown("---")
        st.subheader("📜 Ball-by-Ball History")

        # Show last 12 balls
        recent_balls = st.session_state.ball_history[-12:]
        history_display = []
        for ball in reversed(recent_balls):
            entry = f"Over {ball['over']}: {ball['runs']} run(s)"
            if ball['wicket']:
                entry += " 🎯 WICKET"
            if ball['extra']:
                entry += f" ({ball['extra']})"
            history_display.append(entry)

        for entry in history_display:
            st.text(entry)

    # Show first innings summary if in second innings
    if st.session_state.innings == 2 and st.session_state.team1_score:
        st.markdown("---")
        st.subheader("📊 First Innings Summary")
        t1 = st.session_state.team1_score
        st.info(f"**{t1['team']}**: {t1['runs']}/{t1['wickets']} in {t1['overs']} overs")


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Built with ❤️ using Streamlit | Free to use forever 🏏"
    "</div>",
    unsafe_allow_html=True
)
