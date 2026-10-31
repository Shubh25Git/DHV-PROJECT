"""
Visualizations Module - Plotly Chart Generators
================================================
This module generates clean, interactive Plotly visualizations for the NIRF dashboard.

Design principles:
- Clear, readable typography and informative hover tooltips.
- Proper inverted y-axes for rank charts (Rank 1 at the top).
- Consistent color palettes and responsive layouts.
- Beginner-friendly, well-commented functions.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Standard color theme
THEME_COLOR = "#1f77b4"
COLOR_PALETTE = ["#2b5c8f", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666"]


# ==============================================================================
# Group 1: Time-Series and Trend Visualizations
# ==============================================================================

def plot_institution_rank_trend(df_trend, institution_name):
    """Line chart showing rank trajectory from 2017 to 2025 (y-axis inverted)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_trend["year"],
        y=df_trend["rank"],
        mode="lines+markers+text",
        text=df_trend["rank"].astype(int).astype(str),
        textposition="top center",
        name="Rank",
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=9, color="#0b3954")
    ))
    fig.update_layout(
        title=f"NIRF Rank Trajectory: {institution_name} (2017-2025)",
        xaxis_title="Ranking Year",
        yaxis_title="Rank (Lower number is better)",
        yaxis=dict(autorange="reversed"),  # Invert axis so rank 1 is on top
        template="plotly_white",
        hovermode="x unified"
    )
    return fig


def plot_biggest_rank_movers(df_movers, title="Biggest Rank Improvements"):
    """Horizontal bar chart showing institutional rank shifts."""
    col = "rank_improvement" if "rank_improvement" in df_movers.columns else "rank_decline"
    color = "#2ca02c" if "improvement" in col else "#d62728"
    
    fig = px.bar(
        df_movers,
        x=col,
        y="name",
        orientation="h",
        text=col,
        title=title,
        labels={"name": "Institution", col: "Rank Shift (Positions)"},
        color_discrete_sequence=[color]
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig


def plot_score_trend(df_trend):
    """Line chart with range area showing mean, min, max score over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_trend["year"],
        y=df_trend["mean_score"],
        mode="lines+markers",
        name="Average Score",
        line=dict(color="#1f77b4", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df_trend["year"],
        y=df_trend["median_score"],
        mode="lines+markers",
        name="Median Score",
        line=dict(color="#ff7f0e", width=2, dash="dash")
    ))
    fig.update_layout(
        title="Institutional Score Trends Over Time",
        xaxis_title="Year",
        yaxis_title="Score (0-100)",
        template="plotly_white"
    )
    return fig


def plot_consistent_top_institutions(df_consistent):
    """Bar chart showing number of years institutions spent in Top 10."""
    fig = px.bar(
        df_consistent,
        x="frequency",
        y="name",
        orientation="h",
        text="frequency",
        title="Institutions Consistently in Top 10",
        labels={"frequency": "Years in Top 10", "name": "Institution"},
        color="frequency",
        color_continuous_scale="Blues"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig


# ==============================================================================
# Group 2: Geospatial and Regional Visualizations
# ==============================================================================

def plot_state_distribution(df_states, title="Top States by Ranked Institutions"):
    """Bar chart of top states by institution count."""
    fig = px.bar(
        df_states,
        x="state",
        y="institution_count",
        text="institution_count",
        title=title,
        labels={"state": "State / UT", "institution_count": "Institutions Count"},
        color="institution_count",
        color_continuous_scale="Teal"
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_state_growth(df_growth):
    """Diverging bar chart showing change in state representation."""
    fig = px.bar(
        df_growth,
        x="growth",
        y="state",
        orientation="h",
        text="growth",
        title="State Representation Growth in Top 100",
        labels={"growth": "Change in Institutions Count", "state": "State"},
        color="growth",
        color_continuous_scale="RdYlGn"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig


def plot_two_states_comparison(df_comparison):
    """Box plot or grouped bar comparing two selected states."""
    fig = px.box(
        df_comparison,
        x="state",
        y="score",
        points="all",
        color="state",
        hover_data=["name", "rank"],
        title="Score Comparison Between Selected States",
        labels={"score": "Score", "state": "State"}
    )
    fig.update_layout(template="plotly_white")
    return fig

def plot_geo_distribution_heatmap(pivot_df, category="Overall", top_n=100):
    """
    Q2.2: Heatmap showing geographical distribution of top-ranked institutions across years (2017-2025).
    X-axis: Years (2017-2025)
    Y-axis: States, ordered by total representation (highest at top)
    Color: Number of institutions in top N
    """
    if pivot_df.empty or "state" not in pivot_df.columns:
        return go.Figure()

    year_cols = [c for c in pivot_df.columns if c != "state"]
    if not year_cols:
        return go.Figure()

    # Sort year cols
    year_cols = sorted(year_cols, key=lambda y: int(y) if str(y).isdigit() else str(y))
    x_years = [str(y) for y in year_cols]
    states = pivot_df["state"].tolist()
    z_matrix = pivot_df[year_cols].values.tolist()

    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=x_years,
        y=states,
        colorscale="YlGnBu",
        text=z_matrix,
        texttemplate="%{text}",
        textfont=dict(size=10),
        hoverongaps=False,
        hovertemplate="<b>State:</b> %{y}<br><b>Year:</b> %{x}<br><b>Top " + str(top_n) + " Count:</b> %{z} institutions<extra></extra>",
        colorbar=dict(
            title=dict(text=f"Top {top_n}<br>Count", side="top"),
            thickness=14,
            len=0.9
        )
    ))

    fig.update_layout(
        title=f"Geographical Distribution of Top {top_n} Institutions (2017-2025) - {category}",
        xaxis_title="Ranking Year",
        yaxis_title="State / UT",
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        margin=dict(l=150, r=40, t=60, b=50),
        height=max(450, len(states) * 22 + 140)
    )
    return fig



# ==============================================================================
# Group 3: Univariate Visualizations
# ==============================================================================

def plot_score_histogram(scores_series, year=2024):
    """Histogram with distribution curve for institutional scores."""
    fig = px.histogram(
        x=scores_series,
        nbins=25,
        marginal="box",
        title=f"Distribution of NIRF Scores ({year})",
        labels={"x": "Overall Score"},
        color_discrete_sequence=["#2b5c8f"]
    )
    fig.update_layout(template="plotly_white", yaxis_title="Number of Institutions")
    return fig


def plot_quartile_donut(df_quartiles):
    """Donut chart for score quartiles."""
    fig = px.pie(
        df_quartiles,
        names="quartile",
        values="count",
        hole=0.45,
        title="Institution Distribution Across Score Quartiles",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_category_score_spread(df_spread):
    """Bar chart with error bars showing mean and standard deviation across categories."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_spread["category"],
        y=df_spread["mean"],
        error_y=dict(type="data", array=df_spread["std_dev"], visible=True),
        marker_color="#3366cc",
        text=df_spread["mean"].round(1),
        textposition="auto"
    ))
    fig.update_layout(
        title="Score Spread Across NIRF Ranking Categories (Mean ± Std Dev)",
        xaxis_title="Category",
        yaxis_title="Score",
        template="plotly_white"
    )
    return fig


def plot_rank_distribution(df_ranked, year=2024, category="Overall"):
    """
    Q3.2: Bar chart showing distribution of overall ranks grouped into meaningful rank bands.
    Bands: Rank 1–10 (Top 10), Rank 11–25, Rank 26–50, Rank 51–100, Rank 101–150, Rank 151+.
    Avoids misleading flat histograms by showing tier concentration and counts.
    """
    if isinstance(df_ranked, pd.Series):
        ranks = df_ranked.dropna().astype(float)
    elif "rank" in df_ranked.columns:
        ranks = df_ranked["rank"].dropna().astype(float)
    else:
        return go.Figure()

    if ranks.empty:
        return go.Figure()

    bins = [0, 10, 25, 50, 100, 150, 1000]
    labels = ["Rank 1–10 (Top 10)", "Rank 11–25", "Rank 26–50", "Rank 51–100", "Rank 101–150", "Rank 151+"]

    band_series = pd.cut(ranks, bins=bins, labels=labels, right=True)
    counts = band_series.value_counts(sort=False).reindex(labels, fill_value=0)

    max_rank = ranks.max()
    cutoff_idx = 3
    for idx, l in enumerate(labels):
        if counts[l] > 0 or (idx > 0 and bins[idx] <= max_rank):
            cutoff_idx = max(cutoff_idx, idx)
    kept_labels = labels[:cutoff_idx + 1]
    kept_counts = [int(counts[l]) for l in kept_labels]

    fig = go.Figure()
    colors = ["#4338ca", "#6366f1", "#818cf8", "#06b6d4", "#0ea5e9", "#3b82f6"]
    fig.add_trace(go.Bar(
        x=kept_labels,
        y=kept_counts,
        text=[f"{c} Inst." if c > 0 else "0" for c in kept_counts],
        textposition="outside",
        marker=dict(
            color=colors[:len(kept_labels)],
            line=dict(color="rgba(255,255,255,0.15)", width=1)
        ),
        hovertemplate="<b>%{x}</b><br>Count: %{y} institutions<extra></extra>"
    ))

    title_str = f"Rank Distribution Across Tiers — {category} ({year})" if year else f"Rank Distribution Across Tiers — {category}"
    fig.update_layout(
        title=title_str,
        xaxis_title="Rank Band / Tier",
        yaxis_title="Number of Institutions",
        template="plotly_white",
        yaxis=dict(rangemode="tozero")
    )
    return fig

# ==============================================================================
# Group 4: Bivariate and Correlation Visualizations
# ==============================================================================

def plot_scatter_with_trendline(df_data, x_col, y_col, corr_val=None, title=None):
    """Scatter plot with linear trendline and hover details."""
    fig = px.scatter(
        df_data,
        x=x_col,
        y=y_col,
        trendline="ols",
        hover_data=["name", "rank", "score"],
        title=title or f"{x_col.upper()} vs {y_col.upper()} (Pearson r = {corr_val})",
        labels={x_col: x_col.upper(), y_col: y_col.upper()},
        color_discrete_sequence=["#1f77b4"]
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_parameter_correlation_bar(df_corrs):
    """Bar chart showing correlation of each parameter with overall score."""
    fig = px.bar(
        df_corrs,
        x="parameter",
        y="correlation_with_score",
        text="correlation_with_score",
        title="NIRF Parameter Correlation with Overall Score",
        labels={"parameter": "Ranking Parameter", "correlation_with_score": "Correlation (r)"},
        color="correlation_with_score",
        color_continuous_scale="Blues"
    )
    fig.update_layout(template="plotly_white", yaxis=dict(range=[0, 1]))
    return fig


def plot_correlation_trend(df_trend):
    """Line chart showing correlation evolution over years."""
    fig = px.line(
        df_trend,
        x="year",
        y="correlation",
        markers=True,
        title="Correlation Evolution Across Years (2017-2025)",
        labels={"year": "Year", "correlation": "Correlation Coefficient (r)"}
    )
    fig.update_layout(template="plotly_white")
    return fig


# ==============================================================================
# Group 5: Multivariate Visualizations
# ==============================================================================

def plot_radar_comparison(df_top5):
    """Radar (Spider) chart comparing top institutions across all 5 parameters."""
    categories = ["TLR", "RPC", "GO", "OI", "PERCEPTION"]
    fig = go.Figure()
    
    for _, row in df_top5.iterrows():
        values = [row["tlr"], row["rpc"], row["go"], row["oi"], row["perception"]]
        # Close the loop on radar chart
        values.append(values[0])
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=f"#{int(row['rank'])}: {row['name'][:25]}"
        ))
        
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Multivariate Parameter Profiles of Top Institutions",
        template="plotly_white"
    )
    return fig


def plot_gap_bar(df_gaps):
    """Horizontal bar chart showing parameter gap magnitude."""
    fig = px.bar(
        df_gaps,
        x="gap",
        y="name",
        orientation="h",
        text="gap",
        title="Largest Gap Between Strongest and Weakest Parameter",
        labels={"gap": "Score Difference (Max - Min)", "name": "Institution"},
        color="gap",
        color_continuous_scale="Purples"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig


def plot_high_teaching_low_perception(df_all, tlr_threshold, pr_threshold, year=2024, category="Overall"):
    """
    Q5.3: Scatter plot of Teaching (TLR) vs Perception (PR).
    Displays 75th-percentile TLR threshold and 50th-percentile PR threshold lines,
    highlighting institutions meeting both conditions (TLR >= 75th percentile and PR <= 50th percentile).
    """
    if df_all.empty:
        return go.Figure()

    df = df_all.dropna(subset=["tlr", "perception"]).copy()
    if df.empty:
        return go.Figure()

    is_outlier = (df["tlr"] >= tlr_threshold) & (df["perception"] <= pr_threshold)
    df["is_outlier"] = is_outlier

    outliers = df[df["is_outlier"]]
    regular = df[~df["is_outlier"]]

    fig = go.Figure()

    # Regular institutions
    if not regular.empty:
        fig.add_trace(go.Scatter(
            x=regular["tlr"],
            y=regular["perception"],
            mode="markers",
            name="Other Institutions",
            text=regular["name"],
            customdata=np.stack((regular["rank"], regular["score"]), axis=-1),
            hovertemplate="<b>%{text}</b><br>Rank: #%{customdata[0]}<br>Score: %{customdata[1]:.2f}<br>TLR: %{x:.2f}<br>Perception: %{y:.2f}<extra></extra>",
            marker=dict(size=7, color="#64748b", opacity=0.6)
        ))

    # Outlier institutions (High TLR, Low PR)
    if not outliers.empty:
        fig.add_trace(go.Scatter(
            x=outliers["tlr"],
            y=outliers["perception"],
            mode="markers+text",
            name=f"High TLR / Low PR ({len(outliers)})",
            text=outliers["name"].apply(lambda n: n[:24] + "..." if len(n) > 26 else n),
            textposition="top right",
            customdata=np.stack((outliers["rank"], outliers["score"]), axis=-1),
            hovertemplate="<b>%{text}</b><br>Rank: #%{customdata[0]}<br>Score: %{customdata[1]:.2f}<br>TLR: %{x:.2f}<br>Perception: %{y:.2f}<extra></extra>",
            marker=dict(size=11, color="#f59e0b", symbol="diamond", line=dict(color="#ffffff", width=1.5))
        ))

    # Add threshold reference lines
    fig.add_vline(
        x=tlr_threshold,
        line_width=1.5,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text=f"TLR 75th %ile ({tlr_threshold:.1f})",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#ef4444")
    )
    fig.add_hline(
        y=pr_threshold,
        line_width=1.5,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text=f"PR 50th %ile ({pr_threshold:.1f})",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#ef4444")
    )

    fig.update_layout(
        title=f"High Teaching (TLR) vs Low Perception (PR) - {category} ({year})",
        xaxis_title=f"Teaching, Learning & Resources (TLR) [Threshold: {tlr_threshold:.1f}]",
        yaxis_title=f"Peer Perception (PR) [Threshold: {pr_threshold:.1f}]",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_improved_score_with_declining_parameters(df_improved, category="Overall", start_year=2017, end_year=2024, top_n=15):
    """
    Q5.4: Diverging horizontal bar chart comparing overall score improvement against parameter declines.
    Positive bars (green): Overall score improvement
    Negative bars (red): Maximum parameter decline
    """
    if df_improved.empty:
        return go.Figure()

    df = df_improved.head(top_n).copy()
    if df.empty:
        return go.Figure()

    # Sort ascending so top improvement is on top of horizontal chart
    df = df.sort_values(by="score_improvement", ascending=True)

    y_labels = [n[:30] + "..." if len(n) > 32 else n for n in df["name"]]
    
    # Extract worst decline if available, else default
    if "worst_decline" in df.columns:
        worst_drops = df["worst_decline"].fillna(0.0).tolist()
    else:
        worst_drops = [-1.0] * len(df)

    gains = df["score_improvement"].tolist()
    declined_info = df["declined_parameters"].tolist() if "declined_parameters" in df.columns else [""] * len(df)
    names = df["name"].tolist()
    start_scores = df["start_score"].tolist() if "start_score" in df.columns else [0.0] * len(df)
    end_scores = df["end_score"].tolist() if "end_score" in df.columns else [0.0] * len(df)

    fig = go.Figure()

    # Trace 1: Overall Score Improvement
    fig.add_trace(go.Bar(
        y=y_labels,
        x=gains,
        orientation="h",
        name="Overall Score Improvement",
        marker=dict(color="#10b981", line=dict(color="rgba(255,255,255,0.2)", width=1)),
        text=[f"+{val:.2f}" for val in gains],
        textposition="outside",
        customdata=np.stack((names, start_scores, end_scores, declined_info), axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>Overall Score: %{customdata[1]:.2f} -> %{customdata[2]:.2f} (Gain: +%{x:.2f})<br>Declined Params: %{customdata[3]}<extra></extra>"
    ))

    # Trace 2: Worst Parameter Decline
    fig.add_trace(go.Bar(
        y=y_labels,
        x=worst_drops,
        orientation="h",
        name="Max Parameter Decline",
        marker=dict(color="#ef4444", line=dict(color="rgba(255,255,255,0.2)", width=1)),
        text=[f"{val:.2f}" for val in worst_drops],
        textposition="outside",
        customdata=np.stack((names, start_scores, end_scores, declined_info), axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>Max Parameter Drop: %{x:.2f}<br>Declined Params: %{customdata[3]}<extra></extra>"
    ))

    fig.add_vline(
        x=0,
        line_width=2,
        line_color="#94a3b8",
        line_dash="solid",
        annotation_text="Zero Change",
        annotation_position="top",
        annotation_font=dict(size=10, color="#94a3b8")
    )

    fig.update_layout(
        barmode="relative",
        title=f"Overall Score Improvement vs Parameter Decline ({start_year} -> {end_year}) - {category}",
        xaxis_title="Score Change [Positive = Overall Gain, Negative = Parameter Drop]",
        yaxis_title="Institution",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=180, r=40, t=60, b=50),
        height=max(420, len(df) * 28 + 120)
    )
    return fig




# ==============================================================================
# Group 6: Distribution and Statistical Comparison
# ==============================================================================

def plot_top10_vs_rest_box(top10_scores, rest_scores):
    """Side-by-side boxplot comparing Top 10 scores vs the rest."""
    df_box = pd.concat([
        pd.DataFrame({"Group": "Top 10", "Score": top10_scores}),
        pd.DataFrame({"Group": "Rank 11+", "Score": rest_scores})
    ])
    fig = px.box(
        df_box,
        x="Group",
        y="Score",
        points="all",
        color="Group",
        title="Score Distribution: Top 10 vs Rest of Ranked Institutions",
        color_discrete_map={"Top 10": "#2ca02c", "Rank 11+": "#1f77b4"}
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_dispersion_trend(df_dispersion):
    """Line chart showing score variance and standard deviation over years."""
    fig = px.line(
        df_dispersion,
        x="year",
        y="std_dev",
        markers=True,
        title="Dispersion of NIRF Scores Across Years (Standard Deviation)",
        labels={"year": "Year", "std_dev": "Standard Deviation of Scores"}
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_state_score_box(df_state_scores):
    """Boxplot of scores distributed across states."""
    fig = px.box(
        df_state_scores,
        x="state",
        y="score",
        points="outliers",
        color="state",
        title="State-wise Score Distribution",
        labels={"state": "State", "score": "Score"}
    )
    fig.update_layout(template="plotly_white", showlegend=False)
    return fig


# ==============================================================================
# Group 7: Ranking Transitions Visualizations
# ==============================================================================

def plot_mobility_donut(summary_dict):
    """Donut chart for ranking movement summary (up, down, retained)."""
    labels = ["Moved Up", "Moved Down", "Retained Position"]
    values = [summary_dict["moved_up"], summary_dict["moved_down"], summary_dict["retained_position"]]
    fig = px.pie(
        names=labels,
        values=values,
        hole=0.45,
        title=f"Institutional Rank Mobility (Total Compared: {summary_dict['total_compared']})",
        color=labels,
        color_discrete_map={"Moved Up": "#2ca02c", "Moved Down": "#d62728", "Retained Position": "#1f77b4"}
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_band_transitions_scatter(df_transitions, year1, year2):
    """Scatter showing rank in year 1 vs year 2 for transitioning institutions."""
    fig = px.scatter(
        df_transitions,
        x="rank_year1",
        y="rank_year2",
        text="name",
        title=f"Institutions Moving from 51-100 Band ({year1}) to Top 50 ({year2})",
        labels={"rank_year1": f"Rank in {year1}", "rank_year2": f"Rank in {year2}"},
        color="rank_year2",
        color_continuous_scale="Greens"
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        xaxis=dict(autorange="reversed"),
        yaxis=dict(autorange="reversed"),
        template="plotly_white"
    )
    return fig


# ==============================================================================
# Group 8: Outlier Detection Visualizations
# ==============================================================================

def plot_residual_outliers(df_outliers):
    """Scatter of residual outliers with regression line."""
    fig = px.scatter(
        df_outliers,
        x="score",
        y="rpc",
        text="name",
        hover_data=["rank", "residual"],
        title="Research Score Outliers Relative to Overall Score",
        labels={"score": "Overall Score", "rpc": "Research Score (RPC)"},
        color="residual",
        color_continuous_scale="Reds"
    )
    fig.update_traces(textposition="top right")
    fig.update_layout(template="plotly_white")
    return fig


def plot_volatility_bar(df_volatility):
    """Bar chart of ranking volatility (standard deviation of rank)."""
    fig = px.bar(
        df_volatility,
        x="rank_std_dev",
        y="name",
        orientation="h",
        text="rank_std_dev",
        title="Highest Ranking Volatility (Standard Deviation of Ranks)",
        labels={"rank_std_dev": "Rank Std Dev", "name": "Institution"},
        color="rank_std_dev",
        color_continuous_scale="Oranges"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig


def plot_research_teaching_gap(df_gap, year=2024, category="Overall", top_n=15):
    """
    Q8.2: Horizontal bar chart showing gap between Research (RPC) and Teaching (TLR).
    Gap = RPC - TLR.
    Clearly distinguishes positive gaps (RPC > TLR) and negative gaps (TLR > RPC)
    with a zero reference line.
    """
    if df_gap.empty:
        return go.Figure()

    df = df_gap.head(top_n).copy()
    # Sort ascending so the largest positive gap appears at the top of horizontal chart
    df = df.sort_values(by="research_teaching_gap", ascending=True)

    colors = ["#10b981" if g >= 0 else "#ef4444" for g in df["research_teaching_gap"]]
    texts = [f"{g:+.2f}" for g in df["research_teaching_gap"]]
    y_labels = [n[:32] + "..." if len(n) > 34 else n for n in df["name"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["research_teaching_gap"],
        y=y_labels,
        orientation="h",
        text=texts,
        textposition="outside",
        marker=dict(color=colors),
        customdata=np.stack((df["name"], df["rpc"], df["tlr"], df["rank"]), axis=-1),
        hovertemplate="<b>%{customdata[0]}</b> (Rank #%{customdata[3]})<br>Gap (RPC - TLR): %{x:+.2f}<br>Research (RPC): %{customdata[1]:.2f}<br>Teaching (TLR): %{customdata[2]:.2f}<extra></extra>"
    ))

    fig.add_vline(
        x=0,
        line_width=2,
        line_color="#94a3b8",
        line_dash="solid",
        annotation_text="Zero Gap (RPC = TLR)",
        annotation_position="top",
        annotation_font=dict(size=10, color="#94a3b8")
    )

    fig.update_layout(
        title=f"Research vs Teaching Score Gap (RPC - TLR) - {category} ({year})",
        xaxis_title="Gap: Research Score (RPC) - Teaching Score (TLR) [Positive = Research Leads]",
        yaxis_title="Institution",
        template="plotly_white",
        margin=dict(l=180, r=40, t=50, b=50),
        height=max(420, len(df) * 26 + 120)
    )
    return fig


def plot_strong_param_poor_rank(df_all, param="rpc", param_threshold=75.0, rank_cutoff=50, year=2024, category="Overall"):
    """
    Q8.4: Scatter plot showing parameter score against overall rank.
    Uses reversed rank axis (Rank 1 at the top/left).
    Draws reference lines for parameter 75th percentile and Rank 50 cutoff,
    highlighting institutions with strong parameter (>= threshold) but poor rank (> 50).
    """
    if df_all.empty or param not in df_all.columns:
        return go.Figure()

    df = df_all.dropna(subset=[param, "rank"]).copy()
    if df.empty:
        return go.Figure()

    is_outlier = (df[param] >= param_threshold) & (df["rank"] > rank_cutoff)
    df["is_outlier"] = is_outlier

    outliers = df[df["is_outlier"]]
    regular = df[~df["is_outlier"]]

    param_label = param.upper()
    fig = go.Figure()

    if not regular.empty:
        fig.add_trace(go.Scatter(
            x=regular[param],
            y=regular["rank"],
            mode="markers",
            name="Other Institutions",
            text=regular["name"],
            customdata=regular["score"],
            hovertemplate="<b>%{text}</b><br>Rank: #%{y}<br>" + param_label + ": %{x:.2f}<br>Overall Score: %{customdata:.2f}<extra></extra>",
            marker=dict(size=7, color="#64748b", opacity=0.6)
        ))

    if not outliers.empty:
        fig.add_trace(go.Scatter(
            x=outliers[param],
            y=outliers["rank"],
            mode="markers+text",
            name=f"Strong {param_label} & Poor Rank ({len(outliers)})",
            text=outliers["name"].apply(lambda n: n[:24] + "..." if len(n) > 26 else n),
            textposition="top right",
            customdata=outliers["score"],
            hovertemplate="<b>%{text}</b><br>Rank: #%{y}<br>" + param_label + ": %{x:.2f}<br>Overall Score: %{customdata:.2f}<extra></extra>",
            marker=dict(size=11, color="#ec4899", symbol="diamond", line=dict(color="#ffffff", width=1.5))
        ))

    # Reference lines
    fig.add_vline(
        x=param_threshold,
        line_width=1.5,
        line_dash="dash",
        line_color="#ec4899",
        annotation_text=f"{param_label} 75th %ile ({param_threshold:.1f})",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#ec4899")
    )
    fig.add_hline(
        y=rank_cutoff,
        line_width=1.5,
        line_dash="dash",
        line_color="#ec4899",
        annotation_text=f"Rank {rank_cutoff} Boundary",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#ec4899")
    )

    fig.update_layout(
        title=f"Strong {param_label} Score vs Overall Rank - {category} ({year})",
        xaxis_title=f"{param_label} Score (75th percentile threshold: {param_threshold:.1f})",
        yaxis_title="NIRF Rank (Lower rank number is better)",
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_multi_institution_comparison(df_comparison, title=None):
    """
    Comparison visualization containing every requested institution.
    Uses grouped bar charts for scores (0-100) and a separate rank chart with inverted y-axis (rank 1 at top),
    ensuring ranks and scores are never combined on the same axis.
    """
    metrics = ["Overall Score", "TLR", "RPC", "GO", "OI", "Perception"]
    col_map = {
        "Overall Score": "score",
        "TLR": "tlr",
        "RPC": "rpc",
        "GO": "go",
        "OI": "oi",
        "Perception": "perception",
    }

    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.68, 0.32],
        subplot_titles=["Scores & NIRF Parameters (0-100)", "NIRF Rank (Lower Rank Number is Better)"]
    )
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

    for i, (_, row) in enumerate(df_comparison.iterrows()):
        inst_name = str(row.get("name", f"Institution {i+1}"))
        short_name = inst_name.replace("Indian Institute of Technology", "IIT").replace("National Institute of Technology", "NIT")
        rank_val = row.get("rank")
        rank_str = f"Rank #{int(rank_val)}" if pd.notna(rank_val) and rank_val == int(rank_val) else (f"Rank #{rank_val}" if pd.notna(rank_val) else "Unranked")

        y_vals = []
        text_vals = []
        for m in metrics:
            col = col_map[m]
            val = row.get(col, np.nan)
            if pd.notna(val) and val is not None:
                fval = float(val)
                y_vals.append(round(fval, 2))
                text_vals.append(f"{fval:.1f}")
            else:
                y_vals.append(0)
                text_vals.append("-")

        # Trace for Subplot 1 (Scores & Parameters)
        fig.add_trace(go.Bar(
            x=metrics,
            y=y_vals,
            name=f"{short_name} ({rank_str})",
            text=text_vals,
            textposition="auto",
            marker_color=colors[i % len(colors)]
        ), row=1, col=1)

        # Trace for Subplot 2 (Rank bar chart)
        if pd.notna(rank_val):
            fig.add_trace(go.Bar(
                x=[short_name],
                y=[float(rank_val)],
                name=f"{short_name} Rank",
                text=[rank_str],
                textposition="auto",
                marker_color=colors[i % len(colors)],
                showlegend=False
            ), row=1, col=2)

    chart_title = title or "Multi-Institution Comparison: Scores & Rankings"
    fig.update_layout(
        title=chart_title,
        barmode="group",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )
    fig.update_yaxes(range=[0, 105], title_text="Score / 100", row=1, col=1)
    fig.update_yaxes(autorange="reversed", title_text="Rank (Lower is Better)", row=1, col=2)
    return fig


# Alias for backward compatibility
plot_two_institutions_comparison = plot_multi_institution_comparison


def plot_parameter_comparison(inst_name, cat, year, param_names, param_values):
    """
    Bar chart comparing parameter scores of a single institution.
    """
    fig = go.Figure()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    fig.add_trace(go.Bar(
        x=param_names,
        y=param_values,
        text=[f"{v:.2f}" for v in param_values],
        textposition="auto",
        marker_color=colors[:len(param_names)]
    ))

    short_name = inst_name.replace("Indian Institute of Technology", "IIT").replace("National Institute of Technology", "NIT")
    fig.update_layout(
        title=f"Parameter Comparison: {short_name} ({cat} - {year})",
        yaxis=dict(range=[0, 105], title="Score / 100"),
        xaxis_title="Parameter",
        template="plotly_white"
    )
    return fig

