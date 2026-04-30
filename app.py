import streamlit as st
import pickle
import pandas as pd

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

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", [
    "Win Predictor",
    "Player Stats",
    "Venue Analysis",
    "Head-to-Head",
    "Player Clustering"   
])

# -------------------- WIN PREDICTOR --------------------
if page == "Win Predictor":

    st.title("🏏 IPL Live Win Predictor")
    st.markdown("Predict match outcome based on live match conditions")

    teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
             'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
             'Rajasthan Royals', 'Delhi Capitals']

    batting_team = st.selectbox("Batting Team", teams)
    bowling_team = st.selectbox("Bowling Team", teams)

    target = st.number_input("Target Score", min_value=1)
    current_score = st.number_input("Current Score", min_value=0)

    balls_left = st.number_input("Balls Left", min_value=1, max_value=120)
    wickets_left = st.number_input("Wickets Left", min_value=0, max_value=10)

    # Calculations
    runs_left = target - current_score

    if (120 - balls_left) > 0:
        crr = (current_score * 6) / (120 - balls_left)
    else:
        crr = 0

    rrr = (runs_left * 6) / balls_left if balls_left > 0 else 0

    st.write(f"Runs Left: {runs_left}")
    st.write(f"CRR: {round(crr,2)}")
    st.write(f"RRR: {round(rrr,2)}")

    if st.button("Predict Win Probability"):

        input_dict = {
            'runs_left': runs_left,
            'balls_left': balls_left,
            'wickets_left': wickets_left,
            'crr': crr,
            'rrr': rrr
        }

        # Encode teams
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

        win_prob = result[0][1] * 100
        lose_prob = result[0][0] * 100

        st.success(f"🏏 Winning Probability: {round(win_prob,2)}%")
        st.error(f"❌ Losing Probability: {round(lose_prob,2)}%")

# -------------------- PLAYER STATS --------------------
elif page == "Player Stats":

    st.title("📊 Player Performance Dashboard")

    players = deliveries['batsman'].dropna().unique()
    selected_player = st.selectbox("Select Player", sorted(players))

    player_data = deliveries[deliveries['batsman'] == selected_player]

    # Stats
    total_runs = player_data['batsman_runs'].sum()
    balls = player_data.shape[0]
    strike_rate = (total_runs / balls) * 100 if balls > 0 else 0
    dismissals = player_data['player_dismissed'].notna().sum()
    average = total_runs / dismissals if dismissals > 0 else total_runs
    matches_played = player_data['match_id'].nunique()

    # Display
    st.metric("Total Runs", total_runs)
    st.metric("Strike Rate", round(strike_rate, 2))
    st.metric("Batting Average", round(average, 2))
    st.metric("Matches Played", matches_played)

    # Graph
    runs_per_match = player_data.groupby('match_id')['batsman_runs'].sum()
    st.line_chart(runs_per_match)

elif page == "Venue Analysis":

    st.title("🏟️ Venue Analysis")

    venues = matches['venue'].dropna().unique()
    selected_venue = st.selectbox("Select Venue", sorted(venues))

    venue_data = matches[matches['venue'] == selected_venue]

    total_matches = venue_data.shape[0]

    # Avg 1st innings score
    avg_score = venue_data['win_by_runs'].mean()

    # Chasing wins vs defending
    chasing_wins = venue_data[venue_data['win_by_wickets'] > 0].shape[0]
    defending_wins = venue_data[venue_data['win_by_runs'] > 0].shape[0]

    st.metric("Total Matches", total_matches)
    st.metric("Chasing Wins", chasing_wins)
    st.metric("Defending Wins", defending_wins)

    # Bar chart
    chart_data = pd.DataFrame({
        'Type': ['Chasing', 'Defending'],
        'Wins': [chasing_wins, defending_wins]
    })

    st.bar_chart(chart_data.set_index('Type'))

elif page == "Head-to-Head":

    st.title("🤝 Team Head-to-Head Comparison")

    teams = matches['team1'].dropna().unique()

    team1 = st.selectbox("Select Team 1", sorted(teams))
    team2 = st.selectbox("Select Team 2", sorted(teams))

    if team1 != team2:

        h2h = matches[
            ((matches['team1'] == team1) & (matches['team2'] == team2)) |
            ((matches['team1'] == team2) & (matches['team2'] == team1))
        ]

        total_matches = h2h.shape[0]

        team1_wins = h2h[h2h['winner'] == team1].shape[0]
        team2_wins = h2h[h2h['winner'] == team2].shape[0]

        st.metric(f"{team1} Wins", team1_wins)
        st.metric(f"{team2} Wins", team2_wins)
        st.metric("Total Matches", total_matches)

        # Bar chart
        chart_data = pd.DataFrame({
            'Team': [team1, team2],
            'Wins': [team1_wins, team2_wins]
        })

        st.bar_chart(chart_data.set_index('Team'))

    else:
        st.warning("Please select two different teams")
elif page == "Player Clustering":

    st.title("🧠 Player Clustering (K-Means)")

    st.write("Players grouped based on Strike Rate & Consistency")

    st.scatter_chart(
        player_stats,
        x='strike_rate',
        y='runs_per_match',
        color='cluster'
    )

    # Show cluster data
    selected_cluster = st.selectbox("Select Cluster", sorted(player_stats['cluster'].unique()))

    cluster_players = player_stats[player_stats['cluster'] == selected_cluster]

    st.write(cluster_players[['player', 'runs', 'strike_rate', 'runs_per_match']].head(20))