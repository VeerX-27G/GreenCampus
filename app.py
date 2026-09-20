import streamlit as st
import plotly.express as px
from data.mock_energy import generate_mock_data
from utils.scoring import calculate_leaderboard

st.set_page_config(page_title="GreenCampus Challenge", page_icon="🌱", layout="wide")

# --- Sidebar ---
st.sidebar.title("🌱 GreenCampus Challenge")
st.markdown("Dorms compete by reducing their energy usage — the leaderboard ranks who's improving the most.")
st.sidebar.markdown("Compete with other dorms to cut energy usage.")

st.sidebar.divider()

date_range = st.sidebar.slider(
    "Days to display",
    min_value=7,
    max_value=30,
    value=30,
    help="Controls how much history is shown in the charts and used for leaderboard comparison."
)

recent_window = st.sidebar.slider(
    "Recent period (days) for ranking",
    min_value=3,
    max_value=14,
    value=7,
    help="Leaderboard compares this recent window against everything before it."
)

st.sidebar.divider()
st.sidebar.caption("Built for [UR Hacks] 🚀")

st.title("GreenCampus Challenge 🌱")
st.caption("Tracking dorm energy usage and rewarding reduction")

@st.cache_data
def load_data():
    return generate_mock_data()

full_df = load_data()
df = full_df.sort_values("date").groupby("dorm", group_keys=False).tail(date_range)

st.subheader("Daily Energy Usage by Dorm")

fig = px.line(
    df,
    x="date",
    y="kwh",
    color="dorm",
    labels={"kwh": "Energy Usage (kWh)", "date": "Date", "dorm": "Dorm"},
)
st.plotly_chart(fig, width="stretch")

st.subheader("🏆 Leaderboard — Energy Reduction Ranking")

leaderboard = calculate_leaderboard(df, recent_days=recent_window)

# --- KPI summary row ---
col1, col2, col3 = st.columns(3)

best_dorm = leaderboard.iloc[0]
total_avg_change = leaderboard["pct_change"].mean()
improving_count = (leaderboard["pct_change"] < 0).sum()

col1.metric("🥇 Top Performer", best_dorm["dorm"], f"{best_dorm['pct_change']}%")
col2.metric("📉 Campus Avg Change", f"{total_avg_change:.1f}%")
col3.metric("✅ Dorms Improving", f"{improving_count} / {len(leaderboard)}")

st.divider()
st.subheader("🔍 Dorm Detail View")

selected_dorm = st.selectbox("Select a dorm to inspect:", sorted(df["dorm"].unique()))

dorm_df = df[df["dorm"] == selected_dorm].sort_values("date")
dorm_rank_row = leaderboard[leaderboard["dorm"] == selected_dorm].iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Current Rank", f"#{dorm_rank_row['rank']}")
col2.metric("Change (7-day)", f"{dorm_rank_row['pct_change']}%")
col3.metric("Recent Avg Usage", f"{dorm_rank_row['recent_avg_kwh']} kWh")

detail_fig = px.line(
    dorm_df,
    x="date",
    y="kwh",
    title=f"{selected_dorm} — Daily Usage Trend",
    labels={"kwh": "Energy Usage (kWh)", "date": "Date"},
)
detail_fig.add_hline(
    y=dorm_rank_row["earlier_avg_kwh"],
    line_dash="dash",
    line_color="gray",
    annotation_text="Earlier avg",
)
st.plotly_chart(detail_fig, width="stretch")

# --- Simple tip based on performance ---
if dorm_rank_row["pct_change"] < 0:
    st.success(f"🎉 {selected_dorm} is reducing usage — keep it up! Consider unplugging idle devices to push the trend further.")
else:
    st.warning(f"⚠️ {selected_dorm}'s usage is trending up. Try turning off lights when rooms are empty and using natural light during the day.")

# --- Medal emojis for top 3 ---
def add_medal(rank):
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    return medals.get(rank, "")

leaderboard_display = leaderboard.copy()
leaderboard_display["rank"] = leaderboard_display["rank"].apply(
    lambda r: f"{add_medal(r)} {r}"
)

st.dataframe(
    leaderboard_display,
    column_config={
        "pct_change": st.column_config.NumberColumn("Change (%)", format="%.1f%%"),
    },
    hide_index=True,
    width="stretch",
)

# --- Bar chart of % change, ranked ---
st.subheader("Change in Usage by Dorm")

bar_fig = px.bar(
    leaderboard.sort_values("pct_change"),
    x="dorm",
    y="pct_change",
    color="pct_change",
    color_continuous_scale=["green", "yellow", "red"],  # green = big reduction, red = increase
    labels={"pct_change": "Change (%)", "dorm": "Dorm"},
)
bar_fig.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(bar_fig, width="stretch")