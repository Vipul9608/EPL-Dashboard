import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Premier League 2020-21 Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #252b3b);
        border: 1px solid #3a3f52;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #00d4aa; }
    .metric-label { font-size: 0.85rem; color: #888; margin-top: 4px; }
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e0e0e0;
        border-left: 4px solid #00d4aa;
        padding-left: 10px;
        margin: 20px 0 10px 0;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1f2e, #252b3b);
        border: 1px solid #3a3f52;
        border-radius: 12px;
        padding: 12px 16px;
    }
    div[data-testid="stMetric"] label { color: #888 !important; }
    div[data-testid="stMetric"] div { color: #00d4aa !important; font-size: 1.6rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("dataset_-_2020-09-24.csv")
    # Clean percentage columns
    for col in ["Tackle success %", "Cross accuracy %"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace("%", ""), errors="coerce")
    df["Club"] = df["Club"].str.replace("-", " ")
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg", width=160)
    st.markdown("## 🔍 Filters")

    clubs = ["All Clubs"] + sorted(df["Club"].unique().tolist())
    selected_club = st.selectbox("Club", clubs)

    positions = ["All Positions"] + sorted(df["Position"].unique().tolist())
    selected_pos = st.selectbox("Position", positions)

    min_apps, max_apps = int(df["Appearances"].min()), int(df["Appearances"].max())
    app_range = st.slider("Min Appearances", min_apps, max_apps, 5)

    st.markdown("---")
    st.markdown("**Season:** 2020–21")
    st.markdown("**Players:** 571 | **Clubs:** 20")
    st.markdown("*Premier League Stats*")

# ── Filter data ───────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_club != "All Clubs":
    filtered = filtered[filtered["Club"] == selected_club]
if selected_pos != "All Positions":
    filtered = filtered[filtered["Position"] == selected_pos]
filtered = filtered[filtered["Appearances"] >= app_range]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# ⚽ Premier League 2020–21 Dashboard")
st.markdown(f"Showing **{len(filtered)}** players | Club: **{selected_club}** | Position: **{selected_pos}** | Min Appearances: **{app_range}**")
st.divider()

# ── KPI Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🏟️ Players", len(filtered))
c2.metric("⚽ Total Goals", int(filtered["Goals"].sum()))
c3.metric("🎯 Total Assists", int(filtered["Assists"].sum()))
c4.metric("🟨 Yellow Cards", int(filtered["Yellow cards"].sum()))
c5.metric("🟥 Red Cards", int(filtered["Red cards"].sum()))

st.divider()

# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "⚽ Attacking", "🛡️ Defending", "🔄 Passing", "👤 Player Explorer"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Goals by Club</div>', unsafe_allow_html=True)
        club_goals = filtered.groupby("Club")["Goals"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(
            club_goals, x="Goals", y="Club", orientation="h",
            color="Goals", color_continuous_scale="teal",
            template="plotly_dark"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=420, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Player Distribution by Position</div>', unsafe_allow_html=True)
        pos_counts = filtered["Position"].value_counts().reset_index()
        pos_counts.columns = ["Position", "Count"]
        colors = ["#00d4aa", "#4ecdc4", "#44a1a0", "#247b7b"]
        fig2 = px.pie(
            pos_counts, names="Position", values="Count",
            color_discrete_sequence=colors, hole=0.5, template="plotly_dark"
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=420,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Age Distribution</div>', unsafe_allow_html=True)
        fig3 = px.histogram(
            filtered, x="Age", nbins=20, color_discrete_sequence=["#00d4aa"],
            template="plotly_dark"
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=300,
            bargap=0.05
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Top Nationalities</div>', unsafe_allow_html=True)
        top_nat = filtered["Nationality"].value_counts().head(10).reset_index()
        top_nat.columns = ["Nationality", "Count"]
        fig4 = px.bar(
            top_nat, x="Count", y="Nationality", orientation="h",
            color="Count", color_continuous_scale="teal", template="plotly_dark"
        )
        fig4.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=300, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">Wins vs Losses by Club</div>', unsafe_allow_html=True)
    wl = filtered.groupby("Club")[["Wins", "Losses"]].max().reset_index().sort_values("Wins", ascending=False)
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(name="Wins", x=wl["Club"], y=wl["Wins"], marker_color="#00d4aa"))
    fig5.add_trace(go.Bar(name="Losses", x=wl["Club"], y=wl["Losses"], marker_color="#e05c5c"))
    fig5.update_layout(
        barmode="group", template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=350,
        legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="right", x=1)
    )
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ATTACKING
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Top 15 Goal Scorers</div>', unsafe_allow_html=True)
        top_scorers = filtered.nlargest(15, "Goals")[["Name", "Club", "Goals", "Assists"]]
        fig = px.bar(
            top_scorers, x="Goals", y="Name", orientation="h",
            color="Goals", color_continuous_scale="teal",
            hover_data=["Club", "Assists"], template="plotly_dark"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=420, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Top 15 Assist Providers</div>', unsafe_allow_html=True)
        top_assists = filtered.nlargest(15, "Assists")[["Name", "Club", "Assists", "Goals"]]
        fig2 = px.bar(
            top_assists, x="Assists", y="Name", orientation="h",
            color="Assists", color_continuous_scale="purples",
            hover_data=["Club", "Goals"], template="plotly_dark"
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=420, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Goals vs Shots on Target</div>', unsafe_allow_html=True)
        att = filtered[filtered["Shots on target"].notna() & (filtered["Goals"] > 0)]
        fig3 = px.scatter(
            att, x="Shots on target", y="Goals", color="Position",
            hover_data=["Name", "Club"], size="Goals",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            template="plotly_dark"
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=340
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Goal Breakdown by Type</div>', unsafe_allow_html=True)
        goal_types = {
            "Right Foot": filtered["Goals with right foot"].sum(),
            "Left Foot": filtered["Goals with left foot"].sum(),
            "Headed": filtered["Headed goals"].sum(),
            "Penalties": filtered["Penalties scored"].sum(),
            "Freekicks": filtered["Freekicks scored"].sum(),
        }
        gt_df = pd.DataFrame(list(goal_types.items()), columns=["Type", "Goals"])
        fig4 = px.pie(
            gt_df, names="Type", values="Goals", hole=0.4,
            color_discrete_sequence=px.colors.sequential.Teal,
            template="plotly_dark"
        )
        fig4.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=340,
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">Shooting Accuracy % — Top Players (min 20 shots)</div>', unsafe_allow_html=True)
    shooters = filtered[filtered["Shots"] >= 20].nlargest(20, "Shooting accuracy %")[["Name", "Club", "Shooting accuracy %", "Goals", "Shots"]]
    fig5 = px.bar(
        shooters, x="Shooting accuracy %", y="Name", orientation="h",
        color="Shooting accuracy %", color_continuous_scale="greens",
        hover_data=["Club", "Goals", "Shots"], template="plotly_dark"
    )
    fig5.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
        height=420, yaxis=dict(categoryorder="total ascending")
    )
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — DEFENDING
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Top Tacklers</div>', unsafe_allow_html=True)
        tacklers = filtered[filtered["Tackles"].notna()].nlargest(15, "Tackles")[["Name", "Club", "Tackles", "Tackle success %"]]
        fig = px.bar(
            tacklers, x="Tackles", y="Name", orientation="h",
            color="Tackles", color_continuous_scale="blues",
            hover_data=["Club", "Tackle success %"], template="plotly_dark"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=420, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Most Interceptions</div>', unsafe_allow_html=True)
        intercept = filtered[filtered["Interceptions"].notna()].nlargest(15, "Interceptions")[["Name", "Club", "Interceptions", "Clearances"]]
        fig2 = px.bar(
            intercept, x="Interceptions", y="Name", orientation="h",
            color="Interceptions", color_continuous_scale="reds",
            hover_data=["Club", "Clearances"], template="plotly_dark"
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=420, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Clean Sheets by Club</div>', unsafe_allow_html=True)
        cs = filtered.groupby("Club")["Clean sheets"].max().sort_values(ascending=False).reset_index()
        fig3 = px.bar(
            cs, x="Clean sheets", y="Club", orientation="h",
            color="Clean sheets", color_continuous_scale="blues", template="plotly_dark"
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=400, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Cards by Club</div>', unsafe_allow_html=True)
        cards = filtered.groupby("Club")[["Yellow cards", "Red cards"]].sum().reset_index().sort_values("Yellow cards", ascending=False)
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(name="Yellow", x=cards["Club"], y=cards["Yellow cards"], marker_color="#f0c040"))
        fig4.add_trace(go.Bar(name="Red", x=cards["Club"], y=cards["Red cards"], marker_color="#e05c5c"))
        fig4.update_layout(
            barmode="stack", template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=400,
            xaxis_tickangle=-40,
            legend=dict(orientation="h", y=1.1, xanchor="right", x=1)
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">Aerial Battles — Won vs Lost (Top 15 Players)</div>', unsafe_allow_html=True)
    aerial = filtered[filtered["Aerial battles won"].notna()].nlargest(15, "Aerial battles won")[["Name", "Club", "Aerial battles won", "Aerial battles lost"]]
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(name="Won", x=aerial["Name"], y=aerial["Aerial battles won"], marker_color="#00d4aa"))
    fig5.add_trace(go.Bar(name="Lost", x=aerial["Name"], y=aerial["Aerial battles lost"], marker_color="#e05c5c"))
    fig5.update_layout(
        barmode="group", template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=340,
        xaxis_tickangle=-35,
        legend=dict(orientation="h", y=1.1, xanchor="right", x=1)
    )
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — PASSING
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Most Passes (Top 15)</div>', unsafe_allow_html=True)
        passers = filtered.nlargest(15, "Passes")[["Name", "Club", "Passes", "Passes per match", "Big chances created"]]
        fig = px.bar(
            passers, x="Passes", y="Name", orientation="h",
            color="Passes", color_continuous_scale="purples",
            hover_data=["Club", "Passes per match"], template="plotly_dark"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=420, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Big Chances Created (Top 15)</div>', unsafe_allow_html=True)
        creators = filtered[filtered["Big chances created"].notna()].nlargest(15, "Big chances created")[["Name", "Club", "Big chances created", "Assists"]]
        fig2 = px.bar(
            creators, x="Big chances created", y="Name", orientation="h",
            color="Big chances created", color_continuous_scale="oranges",
            hover_data=["Club", "Assists"], template="plotly_dark"
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=420, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Passes per Match by Position</div>', unsafe_allow_html=True)
        fig3 = px.box(
            filtered[filtered["Passes per match"].notna()],
            x="Position", y="Passes per match",
            color="Position", color_discrete_sequence=px.colors.qualitative.Vivid,
            template="plotly_dark"
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0), height=340, showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Total Crosses by Club (Top 10)</div>', unsafe_allow_html=True)
        crosses = filtered.groupby("Club")["Crosses"].sum().nlargest(10).reset_index()
        fig4 = px.bar(
            crosses, x="Crosses", y="Club", orientation="h",
            color="Crosses", color_continuous_scale="teal", template="plotly_dark"
        )
        fig4.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            height=340, yaxis=dict(categoryorder="total ascending")
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">Passes vs Assists Scatter (All Players)</div>', unsafe_allow_html=True)
    pass_df = filtered[filtered["Passes"] > 0]
    fig5 = px.scatter(
        pass_df, x="Passes", y="Assists", color="Position",
        hover_data=["Name", "Club", "Passes per match"],
        color_discrete_sequence=px.colors.qualitative.Vivid,
        template="plotly_dark", opacity=0.75
    )
    fig5.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=360
    )
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — PLAYER EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">🔎 Search & Compare Players</div>', unsafe_allow_html=True)

    search = st.text_input("Search player name", "")
    player_df = filtered.copy()
    if search:
        player_df = player_df[player_df["Name"].str.contains(search, case=False, na=False)]

    sort_by = st.selectbox("Sort by", ["Goals", "Assists", "Passes", "Tackles", "Appearances", "Age"])
    player_df = player_df.sort_values(sort_by, ascending=False)

    display_cols = ["Name", "Club", "Position", "Age", "Nationality", "Appearances", "Goals", "Assists", "Passes", "Yellow cards", "Red cards"]
    st.dataframe(
        player_df[display_cols].reset_index(drop=True),
        use_container_width=True, height=350
    )

    st.divider()
    st.markdown('<div class="section-header">📊 Radar Chart — Player Comparison</div>', unsafe_allow_html=True)

    all_names = sorted(df["Name"].unique().tolist())
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        player1 = st.selectbox("Player 1", all_names, index=0)
    with col_p2:
        player2 = st.selectbox("Player 2", all_names, index=min(1, len(all_names)-1))

    radar_cols = ["Goals", "Assists", "Passes per match", "Tackles", "Interceptions", "Aerial battles won", "Shots on target", "Big chances created"]

    def get_radar_values(name, cols):
        row = df[df["Name"] == name][cols].iloc[0]
        return row.fillna(0).tolist()

    p1_vals = get_radar_values(player1, radar_cols)
    p2_vals = get_radar_values(player2, radar_cols)

    # Normalize per column max
    maxes = [max(df[c].max(), 1) for c in radar_cols]
    p1_norm = [v / m * 100 for v, m in zip(p1_vals, maxes)]
    p2_norm = [v / m * 100 for v, m in zip(p2_vals, maxes)]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=p1_norm + [p1_norm[0]], theta=radar_cols + [radar_cols[0]],
        fill="toself", name=player1, line_color="#00d4aa", fillcolor="rgba(0,212,170,0.2)"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=p2_norm + [p2_norm[0]], theta=radar_cols + [radar_cols[0]],
        fill="toself", name=player2, line_color="#e05c5c", fillcolor="rgba(224,92,92,0.2)"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#888"), gridcolor="#333"),
            angularaxis=dict(tickfont=dict(color="#ccc"), gridcolor="#333")
        ),
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.1, xanchor="center", x=0.5),
        height=480, margin=dict(l=60, r=60, t=20, b=60)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Raw stats side-by-side
    st.markdown('<div class="section-header">Raw Stats Comparison</div>', unsafe_allow_html=True)
    p1_row = df[df["Name"] == player1][["Goals","Assists","Appearances","Passes","Tackles","Interceptions","Yellow cards","Red cards","Saves"]].iloc[0]
    p2_row = df[df["Name"] == player2][["Goals","Assists","Appearances","Passes","Tackles","Interceptions","Yellow cards","Red cards","Saves"]].iloc[0]
    comp = pd.DataFrame({"Stat": p1_row.index, player1: p1_row.values, player2: p2_row.values})
    st.dataframe(comp.set_index("Stat"), use_container_width=True)
