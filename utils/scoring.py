import pandas as pd


def calculate_leaderboard(df, recent_days=7):
    """
    Compare each dorm's average usage in the most recent period
    vs. the earlier period, and rank by % reduction.
    """
    results = []

    for dorm in df["dorm"].unique():
        dorm_df = df[df["dorm"] == dorm].sort_values("date")

        earlier = dorm_df.iloc[:-recent_days]  # everything except last N days
        recent = dorm_df.iloc[-recent_days:]  # last N days

        earlier_avg = earlier["kwh"].mean()
        recent_avg = recent["kwh"].mean()

        pct_change = ((recent_avg - earlier_avg) / earlier_avg) * 100

        results.append({
            "dorm": dorm,
            "earlier_avg_kwh": round(earlier_avg, 1),
            "recent_avg_kwh": round(recent_avg, 1),
            "pct_change": round(pct_change, 1),
        })

    leaderboard = pd.DataFrame(results)
    leaderboard = leaderboard.sort_values("pct_change")  # most negative = biggest reduction = best
    leaderboard["rank"] = range(1, len(leaderboard) + 1)

    return leaderboard[["rank", "dorm", "earlier_avg_kwh", "recent_avg_kwh", "pct_change"]]