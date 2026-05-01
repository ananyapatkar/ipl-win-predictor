import streamlit as st
import pickle
import pandas as pd

# ── Page config (must be first) ─────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

:root {
    --bg:     #04090F;
    --bg2:    #08111E;
    --card:   #0B1929;
    --card2:  #0F2035;
    --gold:   #F5C400;
    --orange: #FF5722;
    --cyan:   #00BCD4;
    --green:  #00E676;
    --red:    #FF1744;
    --muted:  #4A6080;
    --text:   #D6E4F0;
    --border: rgba(245,196,0,0.12);
}

html, body, .stApp { background: var(--bg) !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060E1A 0%, #08111E 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Rajdhani', sans-serif !important;
}
.stSelectbox > div > div:focus-within {
    border-color: rgba(245,196,0,0.5) !important;
    box-shadow: 0 0 0 2px rgba(245,196,0,0.08) !important;
}

label, .stSelectbox label, .stNumberInput label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #F5C400, #FF5722) !important;
    color: #04090F !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    padding: 0.55rem 1.8rem !important;
    box-shadow: 0 4px 18px rgba(255,87,34,0.28) !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,87,34,0.45) !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: var(--gold) !important;
}
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content:''; position:absolute; left:0; top:0; bottom:0;
    width:3px;
    background: linear-gradient(180deg, var(--gold), var(--orange));
}

.stDataFrame { border-radius: 12px !important; overflow: hidden !important; }
.stDataFrame th {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
.stDataFrame td {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.9rem !important;
}

.stMarkdown p { font-family: 'Rajdhani', sans-serif !important; color: var(--text) !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(245,196,0,0.25); border-radius: 2px; }

#MainMenu, footer, header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)


# ── UI helpers ───────────────────────────────────────────────────────────────────
def page_header(icon, title, subtitle):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(245,196,0,0.07),rgba(0,188,212,0.04));
                border:1px solid rgba(245,196,0,0.14);border-radius:14px;
                padding:1.4rem 1.8rem;margin-bottom:1.4rem;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-40px;right:-30px;width:200px;height:200px;
             background:radial-gradient(circle,rgba(245,196,0,0.06),transparent 70%);
             pointer-events:none;"></div>
        <h1 style="font-family:'Orbitron',sans-serif;font-size:1.55rem;font-weight:900;
                   background:linear-gradient(135deg,#F5C400,#FF5722);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   margin:0 0 0.25rem 0;letter-spacing:1px;">{icon} {title}</h1>
        <p style="font-family:'Rajdhani',sans-serif;color:#4A6080;font-size:0.82rem;
                  letter-spacing:2px;text-transform:uppercase;margin:0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def section_label(text):
    st.markdown(f"""
    <p style="font-family:'Rajdhani',sans-serif;font-size:0.7rem;font-weight:700;
              letter-spacing:3px;text-transform:uppercase;color:#F5C400;
              border-bottom:1px solid rgba(245,196,0,0.12);
              padding-bottom:0.4rem;margin:1.2rem 0 0.75rem 0;">{text}</p>
    """, unsafe_allow_html=True)

def info_row(label, value):
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:0.6rem 1rem;background:#0B1929;border-radius:8px;
                border:1px solid rgba(245,196,0,0.1);margin-bottom:0.4rem;">
        <span style="font-family:'Rajdhani',sans-serif;font-size:0.75rem;
                     letter-spacing:2px;text-transform:uppercase;color:#4A6080;">{label}</span>
        <span style="font-family:'Orbitron',sans-serif;font-size:0.95rem;
                     font-weight:600;color:#D6E4F0;">{value}</span>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# ORIGINAL LOGIC — completely untouched
# ════════════════════════════════════════════════════════════════════════════════

# Load model and columns
model = pickle.load(open('model.pkl', 'rb'))
columns = pickle.load(open('columns.pkl', 'rb'))
matches = pd.read_csv('matches.csv')

# Load dataset
deliveries = pd.read_csv('deliveries.csv')

# Create player features
player_stats = deliveries.groupby('batsman').agg({
    'batsman_runs': 'sum',
    'ball': 'count',
    'match_id': 'nunique'
}).reset_index()

player_stats.columns = ['player', 'runs', 'balls', 'matches']

# Strike rate
player_stats['strike_rate'] = (player_stats['runs'] / player_stats['balls']) * 100

# Runs per match (consistency)
player_stats['runs_per_match'] = player_stats['runs'] / player_stats['matches']

# Filter players (important)
player_stats = player_stats[player_stats['balls'] > 200]

from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=4, random_state=42)
features = player_stats[['strike_rate', 'runs_per_match']]
player_stats['cluster'] = kmeans.fit_predict(features)

# ── Sidebar ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.2rem 0.5rem 1rem;
                border-bottom:1px solid rgba(245,196,0,0.12);margin-bottom:1rem;">
        <div style="font-size:2.2rem;margin-bottom:0.4rem;">🏏</div>
        <p style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:900;
                  background:linear-gradient(135deg,#F5C400,#FF5722);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  letter-spacing:2px;margin:0;">IPL ANALYTICS</p>
        <p style="font-family:'Rajdhani',sans-serif;font-size:0.65rem;color:#4A6080;
                  letter-spacing:3px;text-transform:uppercase;margin:0.2rem 0 0;">
                  Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-family:Rajdhani,sans-serif;font-size:0.65rem;font-weight:700;'
                'letter-spacing:3px;text-transform:uppercase;color:#4A6080;'
                'margin:0 0 0.4rem 0.2rem;">NAVIGATE</p>', unsafe_allow_html=True)

    # Original navigation — same options, same variable name
    page = st.sidebar.selectbox("Go to", [
        "Win Predictor",
        "Player Stats",
        "Venue Analysis",
        "Head-to-Head",
        "Player Clustering"
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="margin-top:2.5rem;padding:0.9rem;background:rgba(245,196,0,0.04);
                border:1px solid rgba(245,196,0,0.1);border-radius:10px;text-align:center;">
        <p style="font-family:'Rajdhani',sans-serif;font-size:0.62rem;color:#4A6080;
                  letter-spacing:2px;margin:0;text-transform:uppercase;">
            Powered by<br>
            <span style="color:#F5C400;">XGBoost · K-Means<br>Random Forest · LogReg</span>
        </p>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# WIN PREDICTOR
# ════════════════════════════════════════════════════════════════════════════════
if page == "Win Predictor":

    page_header("📡", "IPL LIVE WIN PREDICTOR",
                "Predict match outcome based on live match conditions")

    teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
             'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
             'Rajasthan Royals', 'Delhi Capitals']

    section_label("Teams")
    col1, col2 = st.columns(2)
    with col1:
        batting_team = st.selectbox("Batting Team", teams)
    with col2:
        bowling_team = st.selectbox("Bowling Team", teams)

    section_label("Match Situation")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        target = st.number_input("Target Score", min_value=1)
    with col4:
        current_score = st.number_input("Current Score", min_value=0)
    with col5:
        balls_left = st.number_input("Balls Left", min_value=1, max_value=120)
    with col6:
        wickets_left = st.number_input("Wickets Left", min_value=0, max_value=10)

    # Original calculations — untouched
    runs_left = target - current_score

    if (120 - balls_left) > 0:
        crr = (current_score * 6) / (120 - balls_left)
    else:
        crr = 0

    rrr = (runs_left * 6) / balls_left if balls_left > 0 else 0

    section_label("Live Metrics")
    info_row("Runs Left", str(int(runs_left)))
    info_row("Current Run Rate (CRR)", str(round(crr, 2)))
    info_row("Required Run Rate (RRR)", str(round(rrr, 2)))

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Predict Win Probability"):

        # Original model inference — untouched
        input_dict = {
            'runs_left': runs_left,
            'balls_left': balls_left,
            'wickets_left': wickets_left,
            'crr': crr,
            'rrr': rrr
        }

        for col in columns:
            if col.startswith('batting_team_'):
                input_dict[col] = 1 if col == 'batting_team_' + batting_team else 0
            elif col.startswith('bowling_team_'):
                input_dict[col] = 1 if col == 'bowling_team_' + bowling_team else 0
            else:
                input_dict[col] = input_dict.get(col, 0)

        input_df = pd.DataFrame([input_dict])
        input_df = input_df[columns]

        result = model.predict_proba(input_df)

        win_prob  = result[0][1] * 100
        lose_prob = result[0][0] * 100

        # Visual probability bar (UI-only addition)
        w = round(win_prob, 1)
        l = round(lose_prob, 1)
        st.markdown(f"""
        <div style="background:#0B1929;border:1px solid rgba(245,196,0,0.14);
                    border-radius:14px;padding:1.4rem 1.6rem;margin:0.75rem 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.6rem;">
                <span style="font-family:'Orbitron',sans-serif;font-size:0.78rem;
                             font-weight:600;color:#F5C400;">{batting_team}</span>
                <span style="font-family:'Orbitron',sans-serif;font-size:0.78rem;
                             font-weight:600;color:#00BCD4;">{bowling_team}</span>
            </div>
            <div style="position:relative;height:38px;border-radius:19px;
                        overflow:hidden;background:rgba(255,255,255,0.04);">
                <div style="position:absolute;left:0;top:0;bottom:0;width:{w}%;
                            background:linear-gradient(90deg,#F5C400,#FF5722);
                            display:flex;align-items:center;padding-left:0.75rem;">
                    <span style="font-family:'Orbitron',sans-serif;font-size:0.72rem;
                                 font-weight:700;color:#04090F;">{w}%</span>
                </div>
                <div style="position:absolute;right:0;top:0;bottom:0;width:{l}%;
                            background:linear-gradient(270deg,#00BCD4,#006070);
                            display:flex;align-items:center;justify-content:flex-end;
                            padding-right:0.75rem;">
                    <span style="font-family:'Orbitron',sans-serif;font-size:0.72rem;
                                 font-weight:700;color:#04090F;">{l}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Original outputs — untouched
        st.success(f"🏏 Winning Probability: {round(win_prob,2)}%")
        st.error(f"❌ Losing Probability: {round(lose_prob,2)}%")


# ════════════════════════════════════════════════════════════════════════════════
# PLAYER STATS
# ════════════════════════════════════════════════════════════════════════════════
elif page == "Player Stats":

    page_header("👤", "PLAYER PERFORMANCE DASHBOARD",
                "Career statistics · Season trends · Strike rates")

    players = deliveries['batsman'].dropna().unique()
    selected_player = st.selectbox("Select Player", sorted(players))

    player_data = deliveries[deliveries['batsman'] == selected_player]

    # Original stats — untouched
    total_runs     = player_data['batsman_runs'].sum()
    balls          = player_data.shape[0]
    strike_rate    = (total_runs / balls) * 100 if balls > 0 else 0
    dismissals     = player_data['player_dismissed'].notna().sum()
    average        = total_runs / dismissals if dismissals > 0 else total_runs
    matches_played = player_data['match_id'].nunique()

    section_label("Career Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Runs", total_runs)
    with col2:
        st.metric("Strike Rate", round(strike_rate, 2))
    with col3:
        st.metric("Batting Average", round(average, 2))
    with col4:
        st.metric("Matches Played", matches_played)

    section_label("Runs Per Match — Season Timeline")
    runs_per_match = player_data.groupby('match_id')['batsman_runs'].sum()
    st.line_chart(runs_per_match)


# ════════════════════════════════════════════════════════════════════════════════
# VENUE ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
elif page == "Venue Analysis":

    page_header("🏟️", "VENUE ANALYSIS",
                "Ground behaviour · Chasing vs defending · Historical trends")

    venues = matches['venue'].dropna().unique()
    selected_venue = st.selectbox("Select Venue", sorted(venues))

    venue_data = matches[matches['venue'] == selected_venue]

    # Original calculations — untouched
    total_matches  = venue_data.shape[0]
    avg_score      = venue_data['win_by_runs'].mean()
    chasing_wins   = venue_data[venue_data['win_by_wickets'] > 0].shape[0]
    defending_wins = venue_data[venue_data['win_by_runs'] > 0].shape[0]

    section_label("Venue Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Matches", total_matches)
    with col2:
        st.metric("Chasing Wins", chasing_wins)
    with col3:
        st.metric("Defending Wins", defending_wins)

    section_label("Win Type Distribution")
    chart_data = pd.DataFrame({
        'Type': ['Chasing', 'Defending'],
        'Wins': [chasing_wins, defending_wins]
    })
    st.bar_chart(chart_data.set_index('Type'))


# ════════════════════════════════════════════════════════════════════════════════
# HEAD-TO-HEAD
# ════════════════════════════════════════════════════════════════════════════════
elif page == "Head-to-Head":

    page_header("⚔️", "TEAM HEAD-TO-HEAD",
                "Rivalry stats · Win distribution · Historical record")

    teams = matches['team1'].dropna().unique()

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Select Team 1", sorted(teams))
    with col2:
        team2 = st.selectbox("Select Team 2", sorted(teams))

    if team1 != team2:

        h2h = matches[
            ((matches['team1'] == team1) & (matches['team2'] == team2)) |
            ((matches['team1'] == team2) & (matches['team2'] == team1))
        ]

        # Original calculations — untouched
        total_matches = h2h.shape[0]
        team1_wins    = h2h[h2h['winner'] == team1].shape[0]
        team2_wins    = h2h[h2h['winner'] == team2].shape[0]

        section_label("Head-to-Head Record")
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric(f"{team1} Wins", team1_wins)
        with col4:
            st.metric(f"{team2} Wins", team2_wins)
        with col5:
            st.metric("Total Matches", total_matches)

        section_label("Win Comparison")
        chart_data = pd.DataFrame({
            'Team': [team1, team2],
            'Wins': [team1_wins, team2_wins]
        })
        st.bar_chart(chart_data.set_index('Team'))

    else:
        st.warning("Please select two different teams")


# ════════════════════════════════════════════════════════════════════════════════
# PLAYER CLUSTERING
# ════════════════════════════════════════════════════════════════════════════════
elif page == "Player Clustering":

    page_header("🤖", "PLAYER CLUSTERING",
                "K-Means model · Role classification · Strike rate vs consistency")

    st.markdown("""
    <p style="font-family:'Rajdhani',sans-serif;color:#4A6080;font-size:0.85rem;
              letter-spacing:0.5px;margin-bottom:0.5rem;">
        Players grouped based on <b style="color:#F5C400;">Strike Rate</b> &amp;
        <b style="color:#00BCD4;">Consistency</b> &nbsp;·&nbsp; K = 4 clusters
    </p>
    """, unsafe_allow_html=True)

    section_label("Cluster Scatter Plot")

    # Original chart — untouched
    st.scatter_chart(
        player_stats,
        x='strike_rate',
        y='runs_per_match',
        color='cluster'
    )

    section_label("Explore by Cluster")
    selected_cluster = st.selectbox("Select Cluster", sorted(player_stats['cluster'].unique()))

    cluster_players = player_stats[player_stats['cluster'] == selected_cluster]

    st.dataframe(
        cluster_players[['player', 'runs', 'strike_rate', 'runs_per_match']].head(20),
        use_container_width=True,
        hide_index=True
    )


# ── Footer ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.2rem;margin-top:2.5rem;
            border-top:1px solid rgba(245,196,0,0.1);">
    <p style="font-family:'Rajdhani',sans-serif;font-size:0.65rem;color:#4A6080;
              letter-spacing:2.5px;text-transform:uppercase;margin:0;">
        🏏 IPL Analytics Platform &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp;
        XGBoost · K-Means · Scikit-learn
    </p>
</div>
""", unsafe_allow_html=True)
