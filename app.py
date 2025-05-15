import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi
from fuzzywuzzy import process
import requests
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary

# Load player data from FPL API
@st.cache_data
def load_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    data = requests.get(url).json()
    df = pd.DataFrame(data['elements'])

    status_map = {'a': 0.0, 'd': 0.3, 'i': 0.7, 's': 1.0, 'u': 1.0}
    df['status_risk'] = df['status'].map(status_map).fillna(0.5)
    max_minutes = 90 * df['minutes'].max() / df['minutes'].mean()
    df['minutes_risk'] = 1 - (df['minutes'] / max_minutes)
    df['rotation_risk_score'] = 0.6 * df['minutes_risk'] + 0.4 * df['status_risk']
    df['gw_planning_score'] = df['total_points'] * (1 - df['rotation_risk_score'])

    return df

df = load_data()
position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
df['Position'] = df['element_type'].map(position_map)
df['value_per_million'] = df['gw_planning_score'] / (df['now_cost'] / 10)

st.title("🌟 FPL Assistant Dashboard")

# Sidebar inputs
gw = st.sidebar.number_input("Current Gameweek", min_value=1, max_value=38, value=38)

st.sidebar.header("📊 Your Squad")
if st.sidebar.button("🔄 Optimize My Squad"):
    # Optimizer setup
    budget_limit = 1000
    position_limits = {1: 2, 2: 5, 3: 5, 4: 3}
    team_limit = 3
    squad_size = 15

    model = LpProblem("FPL_Squad_Optimization", LpMaximize)
    x = {i: LpVariable(f"player_{i}", cat=LpBinary) for i in df.index}
    model += lpSum(df.loc[i, 'gw_planning_score'] * x[i] for i in df.index)
    model += lpSum(x[i] for i in df.index) == squad_size
    model += lpSum(df.loc[i, 'now_cost'] * x[i] for i in df.index) <= budget_limit

    for pos, count in position_limits.items():
        model += lpSum(x[i] for i in df.index if df.loc[i, 'element_type'] == pos) == count

    for team_id in df['team'].unique():
        model += lpSum(x[i] for i in df.index if df.loc[i, 'team'] == team_id) <= team_limit

    model.solve()

    selected = [i for i in df.index if x[i].value() == 1.0]
    df['in_my_team'] = False
    df.loc[selected, 'in_my_team'] = True
    st.success("✅ Squad optimized!")
else:
    df['in_my_team'] = False

# Radar chart
st.subheader("🔍 Player Radar Comparison")
radar_players = st.multiselect("Compare up to 3 players:", options=df['web_name'])
radar_features = ['form', 'points_per_game', 'minutes', 'creativity', 'threat', 'rotation_risk_score']
if radar_players:
    plt.figure(figsize=(6, 6))
    num_vars = len(radar_features)
    angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)] + [0]
    for player_name in radar_players:
        match, score = process.extractOne(player_name, df['web_name'].unique())
        player = df[df['web_name'] == match]
        values = player[radar_features].values.flatten().tolist() + [player[radar_features].values.flatten()[0]]
        values = [(v - df[f].min()) / (df[f].max() - df[f].min()) if df[f].max() != df[f].min() else 0.5 for v, f in zip(values, radar_features + [radar_features[0]])]
        plt.polar(angles, values, label=match, linewidth=2)
        plt.fill(angles, values, alpha=0.1)
    plt.xticks(angles[:-1], radar_features, fontsize=8)
    plt.title("Player Radar Chart")
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    st.pyplot(plt)

# Top 10
st.subheader("🏆 Top 10 Players")
top_df = df.sort_values(by='gw_planning_score', ascending=False).head(10)
fig1, ax1 = plt.subplots(figsize=(8, 5))
sns.barplot(data=top_df, x='gw_planning_score', y='web_name', hue='Position', ax=ax1)
ax1.set_title("Top 10 Projected Players (GW Adjusted)")
st.pyplot(fig1)

# Your Squad
st.subheader("👥 Your Squad Performance")
my_squad_df = df[df['in_my_team'] == True].sort_values(by='gw_planning_score', ascending=False)
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.barplot(data=my_squad_df, x='gw_planning_score', y='web_name', hue='Position', ax=ax2)
ax2.set_title("Your Squad - GW Projected Points")
st.pyplot(fig2)

# Value picks
st.subheader("📊 Best Value Picks")
value_df = df.sort_values(by='value_per_million', ascending=False).head(10)
fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(data=value_df, x='value_per_million', y='web_name', hue='Position', ax=ax3)
ax3.set_title("Top 10 Value for Money Players")
st.pyplot(fig3)

# Transfer Suggestions
st.subheader("🔄 Transfer Suggestions")
suggestions = []
df_filtered = df[df['rotation_risk_score'] < 0.5]
for _, out_row in df[df['in_my_team'] == True].iterrows():
    candidates = df_filtered[(df_filtered['element_type'] == out_row['element_type']) & (~df_filtered['web_name'].isin(my_squad_df['web_name']))]
    for _, in_row in candidates.iterrows():
        if in_row['now_cost'] <= out_row['now_cost']:
            gain = in_row['gw_planning_score'] - out_row['gw_planning_score']
            suggestions.append({'OUT': out_row['web_name'], 'IN': in_row['web_name'], 'Gain': round(gain, 2)})

sorted_suggestions = sorted(suggestions, key=lambda x: x['Gain'], reverse=True)
used_in, used_out, final_suggestions = set(), set(), []
for s in sorted_suggestions:
    if s['IN'] not in used_in and s['OUT'] not in used_out:
        final_suggestions.append(s)
        used_in.add(s['IN'])
        used_out.add(s['OUT'])
    if len(final_suggestions) == 3:
        break

for s in final_suggestions:
    st.markdown(f"**OUT:** {s['OUT']} → **IN:** {s['IN']} | Gain: +{s['Gain']} pts")
