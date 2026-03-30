import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Football Player Analytics Dashboard",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Football Player Analytics Dashboard")
st.markdown("Analyze player performance, club statistics, goals, assists, passing, defending, and more.")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    # Change the file path if needed
    file_path = "dataset - 2020-09-24.csv"
    df = pd.read_csv(file_path)
    return df

df = load_data()

# -----------------------------
# DATA CLEANING
# -----------------------------
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["Appearances"] = pd.to_numeric(df["Appearances"], errors="coerce")
df["Goals"] = pd.to_numeric(df["Goals"], errors="coerce")
df["Assists"] = pd.to_numeric(df["Assists"], errors="coerce")
df["Passes"] = pd.to_numeric(df["Passes"], errors="coerce")
df["Tackles"] = pd.to_numeric(df["Tackles"], errors="coerce")
df["Shots on target"] = pd.to_numeric(df["Shots on target"], errors="coerce")
df["Saves"] = pd.to_numeric(df["Saves"], errors="coerce")
df["Clean sheets"] = pd.to_numeric(df["Clean sheets"], errors="coerce")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filter Players")

clubs = sorted(df["Club"].dropna().unique().tolist())
positions = sorted(df["Position"].dropna().unique().tolist())
nationalities = sorted(df["Nationality"].dropna().unique().tolist())

selected_clubs = st.sidebar.multiselect("Select Club(s)", clubs, default=clubs)
selected_positions = st.sidebar.multiselect("Select Position(s)", positions, default=positions)
selected_nationalities = st.sidebar.multiselect("Select Nationality(s)", nationalities, default=nationalities)

min_age = int(df["Age"].min()) if df["Age"].notna().any() else 16
max_age = int(df["Age"].max()) if df["Age"].notna().any() else 45

age_range = st.sidebar.slider("Select Age Range", min_age, max_age, (min_age, max_age))

filtered_df = df[
    (df["Club"].isin(selected_clubs)) &
    (df["Position"].isin(selected_positions)) &
    (df["Nationality"].isin(selected_nationalities)) &
    (df["Age"].between(age_range[0], age_range[1], inclusive="both"))
].copy()

# -----------------------------
# KPIs
# -----------------------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Players", len(filtered_df))
col2.metric("Total Clubs", filtered_df["Club"].nunique())
col3.metric("Total Goals", int(filtered_df["Goals"].fillna(0).sum()))
col4.metric("Total Assists", int(filtered_df["Assists"].fillna(0).sum()))
col5.metric("Avg Age", round(filtered_df["Age"].mean(), 1) if not filtered_df.empty else 0)

# -----------------------------
# TOP PLAYERS TABLE
# -----------------------------
st.subheader("🏅 Top Players")

sort_option = st.selectbox(
    "Sort players by",
    ["Goals", "Assists", "Passes", "Tackles", "Shots on target", "Saves", "Clean sheets", "Appearances"]
)

top_players = filtered_df.sort_values(by=sort_option, ascending=False).head(15)

st.dataframe(
    top_players[
        [
            "Name", "Club", "Position", "Nationality", "Age",
            "Appearances", "Goals", "Assists", "Passes", "Tackles",
            "Shots on target", "Saves", "Clean sheets"
        ]
    ],
    use_container_width=True
)

# -----------------------------
# CHARTS ROW 1
# -----------------------------
st.subheader("📊 Club & Player Insights")

c1, c2 = st.columns(2)

with c1:
    club_goals = (
        filtered_df.groupby("Club", as_index=False)["Goals"]
        .sum()
        .sort_values("Goals", ascending=False)
        .head(10)
    )
    fig_club_goals = px.bar(
        club_goals,
        x="Club",
        y="Goals",
        title="Top 10 Clubs by Total Goals",
        text_auto=True
    )
    fig_club_goals.update_layout(xaxis_title="Club", yaxis_title="Goals")
    st.plotly_chart(fig_club_goals, use_container_width=True)

with c2:
    pos_goals = (
        filtered_df.groupby("Position", as_index=False)["Goals"]
        .sum()
        .sort_values("Goals", ascending=False)
    )
    fig_pos_goals = px.pie(
        pos_goals,
        names="Position",
        values="Goals",
        title="Goals Contribution by Position"
    )
    st.plotly_chart(fig_pos_goals, use_container_width=True)

# -----------------------------
# CHARTS ROW 2
# -----------------------------
c3, c4 = st.columns(2)

with c3:
    top_scorers = filtered_df.sort_values("Goals", ascending=False).head(10)
    fig_top_scorers = px.bar(
        top_scorers,
        x="Name",
        y="Goals",
        color="Club",
        title="Top 10 Goal Scorers",
        text_auto=True
    )
    fig_top_scorers.update_layout(xaxis_title="Player", yaxis_title="Goals")
    st.plotly_chart(fig_top_scorers, use_container_width=True)

with c4:
    top_assists = filtered_df.sort_values("Assists", ascending=False).head(10)
    fig_top_assists = px.bar(
        top_assists,
        x="Name",
        y="Assists",
        color="Club",
        title="Top 10 Players by Assists",
        text_auto=True
    )
    fig_top_assists.update_layout(xaxis_title="Player", yaxis_title="Assists")
    st.plotly_chart(fig_top_assists, use_container_width=True)

# -----------------------------
# CHARTS ROW 3
# -----------------------------
c5, c6 = st.columns(2)

with c5:
    scatter_df = filtered_df.dropna(subset=["Goals", "Assists", "Appearances"])
    fig_scatter = px.scatter(
        scatter_df,
        x="Goals",
        y="Assists",
        size="Appearances",
        color="Position",
        hover_data=["Name", "Club"],
        title="Goals vs Assists"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with c6:
    age_distribution = px.histogram(
        filtered_df,
        x="Age",
        nbins=15,
        title="Player Age Distribution"
    )
    age_distribution.update_layout(xaxis_title="Age", yaxis_title="Count")
    st.plotly_chart(age_distribution, use_container_width=True)

# -----------------------------
# CHARTS ROW 4
# -----------------------------
st.subheader("🛡️ Defensive & Passing Analysis")

c7, c8 = st.columns(2)

with c7:
    top_defenders = filtered_df.sort_values("Tackles", ascending=False).head(10)
    fig_tackles = px.bar(
        top_defenders,
        x="Name",
        y="Tackles",
        color="Club",
        title="Top 10 Players by Tackles",
        text_auto=True
    )
    fig_tackles.update_layout(xaxis_title="Player", yaxis_title="Tackles")
    st.plotly_chart(fig_tackles, use_container_width=True)

with c8:
    top_passers = filtered_df.sort_values("Passes", ascending=False).head(10)
    fig_passes = px.bar(
        top_passers,
        x="Name",
        y="Passes",
        color="Club",
        title="Top 10 Players by Passes",
        text_auto=True
    )
    fig_passes.update_layout(xaxis_title="Player", yaxis_title="Passes")
    st.plotly_chart(fig_passes, use_container_width=True)

# -----------------------------
# GOALKEEPER SECTION
# -----------------------------
st.subheader("🧤 Goalkeeper Performance")

goalkeepers = filtered_df[filtered_df["Position"].str.contains("Goalkeeper", case=False, na=False)].copy()

if not goalkeepers.empty:
    g1, g2 = st.columns(2)

    with g1:
        top_saves = goalkeepers.sort_values("Saves", ascending=False).head(10)
        fig_saves = px.bar(
            top_saves,
            x="Name",
            y="Saves",
            color="Club",
            title="Top Goalkeepers by Saves",
            text_auto=True
        )
        st.plotly_chart(fig_saves, use_container_width=True)

    with g2:
        top_clean_sheets = goalkeepers.sort_values("Clean sheets", ascending=False).head(10)
        fig_clean = px.bar(
            top_clean_sheets,
            x="Name",
            y="Clean sheets",
            color="Club",
            title="Top Goalkeepers by Clean Sheets",
            text_auto=True
        )
        st.plotly_chart(fig_clean, use_container_width=True)
else:
    st.info("No goalkeepers found for the selected filters.")

# -----------------------------
# PLAYER COMPARISON
# -----------------------------
st.subheader("⚔️ Player Comparison")

player_names = filtered_df["Name"].dropna().unique().tolist()

if len(player_names) >= 2:
    p1, p2 = st.columns(2)

    with p1:
        player_1 = st.selectbox("Select Player 1", player_names, index=0)

    with p2:
        player_2 = st.selectbox("Select Player 2", player_names, index=1)

    row1 = filtered_df[filtered_df["Name"] == player_1].iloc[0]
    row2 = filtered_df[filtered_df["Name"] == player_2].iloc[0]

    comparison_metrics = ["Goals", "Assists", "Passes", "Tackles", "Shots on target", "Appearances"]

    radar_df = pd.DataFrame({
        "Metric": comparison_metrics,
        player_1: [row1.get(m, 0) if pd.notna(row1.get(m, 0)) else 0 for m in comparison_metrics],
        player_2: [row2.get(m, 0) if pd.notna(row2.get(m, 0)) else 0 for m in comparison_metrics],
    })

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=radar_df[player_1],
        theta=radar_df["Metric"],
        fill='toself',
        name=player_1
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=radar_df[player_2],
        theta=radar_df["Metric"],
        fill='toself',
        name=player_2
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Player Comparison Radar Chart"
    )

    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.warning("Not enough players available for comparison.")

# -----------------------------
# RAW DATA
# -----------------------------
with st.expander("📂 View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# DOWNLOAD FILTERED DATA
# -----------------------------
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_football_players.csv",
    mime="text/csv"
)
