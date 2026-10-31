"""
DHV NIRF Ranking Analytics Dashboard
====================================
Interactive Dashboard covering NIRF Rankings (2017–2025) across all categories.

Evaluation Levels Implemented:
- Level 1: All 8 Official Sample Question Categories (Annexure A, 40 questions).
- Level 2: Dynamic Analysis Engine for unseen questions with ad-hoc aggregations and custom charts.
- Level 3: Natural Language Query Interface ("Ask NIRF Data") for conversational exploration.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_loader import load_master_data, load_manual_file
import src.analysis as analysis
import src.visualizations as viz
from src.query_engine import parse_query, execute_query
from src.preprocessing import validate_master_dataset

# Streamlit Page Configuration
st.set_page_config(
    page_title="NIRF Ranking Analytics (2017–2025)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for clean presentation
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F8FAFC; border-radius: 8px; padding: 15px; border-left: 5px solid #2563EB; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 16px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_cached_master_data():
    """Load and cache the master dataset for high performance."""
    return load_master_data()


# Load Master Data
df_master = get_cached_master_data()

# Sidebar Navigation
st.sidebar.title("🎓 NIRF Analytics")
st.sidebar.caption("Data Handling & Visualization (DHV) Project")

menu_choice = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Dashboard Overview",
        "🎯 Sample Questions (Level 1)",
        "⚡ Dynamic Analysis (Level 2)",
        "💬 Ask NIRF Data (Level 3)",
        "📁 Manual File Import",
        "📋 Data Quality & Coverage"
    ]
)

# Global Filters in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")

if not df_master.empty:
    all_categories = sorted(df_master["category"].unique().tolist())
    all_years = sorted(df_master["year"].unique().tolist(), reverse=True)
    all_states = sorted(df_master["state"].unique().tolist())

    selected_year = st.sidebar.selectbox("Select Year", all_years, index=0)
    selected_category = st.sidebar.selectbox("Select Category", all_categories, index=all_categories.index("Overall") if "Overall" in all_categories else 0)
else:
    selected_year = 2024
    selected_category = "Overall"
    all_categories = ["Overall"]
    all_years = [2024]
    all_states = []


# ==============================================================================
# 1. DASHBOARD OVERVIEW
# ==============================================================================
if menu_choice == "📊 Dashboard Overview":
    st.markdown('<div class="main-header">NIRF Ranking Analytics Dashboard (2017–2025)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comprehensive Data Handling and Visualization across all Indian Higher Educational Institutions</div>', unsafe_allow_html=True)

    if df_master.empty:
        st.warning("Master dataset not found. Please run the preprocessing pipeline or check `data/processed/nirf_master.csv`.")
    else:
        # KPI Metrics Cards
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Total Records", f"{len(df_master):,}")
        kpi2.metric("Institutions", f"{df_master['name'].nunique():,}")
        kpi3.metric("States & UTs", f"{df_master['state'].nunique():,}")
        kpi4.metric("Years Covered", f"{df_master['year'].min()}–{df_master['year'].max()}")
        kpi5.metric("Categories", f"{df_master['category'].nunique()}")

        st.markdown("---")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader(f"Top 10 Institutions in {selected_year} ({selected_category})")
            top10 = analysis.filter_data(df_master, year=selected_year, category=selected_category).sort_values("rank").head(10)
            if not top10.empty:
                st.dataframe(
                    top10[["rank", "name", "score", "city", "state", "tlr", "rpc"]].reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(f"No records available for {selected_category} in {selected_year}.")

        with col_right:
            st.subheader(f"Score Distribution in {selected_year} ({selected_category})")
            scores = analysis.get_score_distribution(df_master, year=selected_year, category=selected_category)
            if not scores.empty:
                fig_hist = viz.plot_score_histogram(scores, year=selected_year)
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Score data not available for this selection.")

        st.subheader("State-wise Representation in Top 100")
        state_df = analysis.get_states_top_institutions(df_master, year=selected_year, category=selected_category, top_n=100, limit=12)
        if not state_df.empty:
            fig_state = viz.plot_state_distribution(state_df, f"Top States by Institution Count in Top 100 ({selected_year})")
            st.plotly_chart(fig_state, use_container_width=True)


# ==============================================================================
# 2. SAMPLE QUESTIONS (LEVEL 1: 10 MARKS)
# ==============================================================================
elif menu_choice == "🎯 Sample Questions (Level 1)":
    st.markdown('<div class="main-header">Official Sample Questionnaire (Annexure A)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Select an analysis category and explore answers to all 40 questions from the official project brief.</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "1. Time-Series Trends",
        "2. Geospatial Analysis",
        "3. Univariate Analysis",
        "4. Bivariate & Correlation",
        "5. Multivariate Analysis",
        "6. Statistical Comparison",
        "7. Ranking Transitions",
        "8. Outlier & Gaps"
    ])

    # ------------------ TAB 1: Time-Series Trends ------------------
    with tabs[0]:
        st.subheader("1. Time-series and Trend Analysis")
        q1_choice = st.selectbox(
            "Select Question:",
            [
                "1.1 Institutional Rank Trajectory (2017–2025)",
                "1.2 Greatest Rank Improvements Over Time",
                "1.3 Largest Declines in Ranking",
                "1.4 Average Score Evolution Over Time",
                "1.5 Institutions Consistently in Top 10"
            ]
        )

        if "1.1" in q1_choice:
            # Institution selection
            available_institutions = sorted(df_master[df_master["category"] == selected_category]["name"].unique().tolist())
            selected_inst = st.selectbox("Select Institution:", available_institutions, index=0 if available_institutions else None)
            if selected_inst:
                trend_df = analysis.get_institution_rank_trend(df_master, selected_inst, category=selected_category)
                if not trend_df.empty:
                    fig = viz.plot_institution_rank_trend(trend_df, selected_inst)
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(trend_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("No historical trend data found for this institution.")

        elif "1.2" in q1_choice:
            col_sy, col_ey = st.columns(2)
            sy = col_sy.selectbox("Start Year", sorted(all_years), index=0, key="imp_sy")
            ey = col_ey.selectbox("End Year", sorted(all_years, reverse=True), index=0, key="imp_ey")
            imp_df = analysis.get_biggest_rank_improvements(df_master, category=selected_category, start_year=sy, end_year=ey)
            if not imp_df.empty:
                fig = viz.plot_biggest_rank_movers(imp_df, f"Top Rank Improvements ({sy} to {ey})")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(imp_df, use_container_width=True, hide_index=True)
            else:
                st.info("No comparative records found between the selected years.")

        elif "1.3" in q1_choice:
            col_sy, col_ey = st.columns(2)
            sy = col_sy.selectbox("Start Year", sorted(all_years), index=0, key="dec_sy")
            ey = col_ey.selectbox("End Year", sorted(all_years, reverse=True), index=0, key="dec_ey")
            dec_df = analysis.get_biggest_rank_declines(df_master, category=selected_category, start_year=sy, end_year=ey)
            if not dec_df.empty:
                fig = viz.plot_biggest_rank_movers(dec_df, f"Largest Rank Declines ({sy} to {ey})")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(dec_df, use_container_width=True, hide_index=True)
            else:
                st.info("No comparative records found.")

        elif "1.4" in q1_choice:
            trend_df = analysis.get_average_score_trend(df_master, category=selected_category)
            if not trend_df.empty:
                fig = viz.plot_score_trend(trend_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(trend_df, use_container_width=True, hide_index=True)

        elif "1.5" in q1_choice:
            min_yrs = st.slider("Minimum Years in Top 10:", min_value=2, max_value=9, value=5)
            consistent_df = analysis.get_consistent_top_institutions(df_master, category=selected_category, top_n=10, min_years=min_yrs)
            if not consistent_df.empty:
                fig = viz.plot_consistent_top_institutions(consistent_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(consistent_df, use_container_width=True, hide_index=True)
            else:
                st.info(f"No institutions appeared in Top 10 for at least {min_yrs} years in {selected_category}.")

    # ------------------ TAB 2: Geospatial Analysis ------------------
    with tabs[1]:
        st.subheader("2. Geospatial and Regional Analysis")
        q2_choice = st.selectbox(
            "Select Question:",
            [
                "2.1 States with Highest Top 100 Institutions",
                "2.2 Geographical Distribution Trend (2017–2025)",
                "2.3 States with Improved Representation Over Time",
                "2.4 Comparative State Analysis (e.g., Karnataka vs Tamil Nadu)",
                "2.5 Newly Appearing Institutions by State"
            ]
        )

        if "2.1" in q2_choice:
            state_df = analysis.get_states_top_institutions(df_master, year=selected_year, category=selected_category, top_n=100)
            if not state_df.empty:
                fig = viz.plot_state_distribution(state_df, f"States with Most Top 100 Institutions ({selected_year})")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(state_df, use_container_width=True, hide_index=True)

        elif "2.2" in q2_choice:
            geo_pivot = analysis.get_geo_distribution_trend(df_master, category=selected_category, top_n=100)
            if not geo_pivot.empty:
                st.markdown(f"**Top 100 Institutions Count per State (2017–2025) in {selected_category}:**")
                st.dataframe(geo_pivot, use_container_width=True, hide_index=True)

        elif "2.3" in q2_choice:
            growth_df = analysis.get_state_representation_growth(df_master, category=selected_category, start_year=2017, end_year=selected_year)
            if not growth_df.empty:
                fig = viz.plot_state_growth(growth_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(growth_df, use_container_width=True, hide_index=True)

        elif "2.4" in q2_choice:
            c1, c2 = st.columns(2)
            s1 = c1.selectbox("State 1:", all_states, index=all_states.index("Karnataka") if "Karnataka" in all_states else 0)
            s2 = c2.selectbox("State 2:", all_states, index=all_states.index("Tamil Nadu") if "Tamil Nadu" in all_states else 1)
            comp_summary, raw_comp = analysis.compare_two_states(df_master, state1=s1, state2=s2, category=selected_category, year=selected_year)
            st.dataframe(comp_summary, use_container_width=True, hide_index=True)
            if not raw_comp.empty:
                fig = viz.plot_two_states_comparison(raw_comp)
                st.plotly_chart(fig, use_container_width=True)

        elif "2.5" in q2_choice:
            new_df, raw_new = analysis.get_newly_appearing_institutions_by_state(df_master, category=selected_category, base_year=2017, recent_year=selected_year)
            if not new_df.empty:
                st.write(f"States producing newly appeared institutions in {selected_year} (compared to 2017 baseline):")
                fig = viz.plot_state_distribution(new_df.rename(columns={"new_institutions_count": "institution_count"}), f"Newly Appearing Institutions in {selected_year}")
                st.plotly_chart(fig, use_container_width=True)
                with st.expander("View Newly Appearing Institutions List"):
                    st.dataframe(raw_new[["name", "state", "rank", "score"]], use_container_width=True, hide_index=True)

    # ------------------ TAB 3: Univariate Analysis ------------------
    with tabs[2]:
        st.subheader("3. Univariate Analysis")
        q3_choice = st.selectbox(
            "Select Question:",
            [
                "3.1 Score Distribution Histogram & Box",
                "3.2 Rank Distribution",
                "3.3 Summary Statistics (Mean, Median, Min, Max)",
                "3.4 Score Quartiles Breakdown",
                "3.5 Score Spread Comparison Across Categories"
            ]
        )

        if "3.1" in q3_choice:
            scores = analysis.get_score_distribution(df_master, year=selected_year, category=selected_category)
            if not scores.empty:
                fig = viz.plot_score_histogram(scores, year=selected_year)
                st.plotly_chart(fig, use_container_width=True)

        elif "3.2" in q3_choice:
            ranks = analysis.get_rank_distribution(df_master, year=selected_year, category=selected_category)
            if not ranks.empty:
                fig = px.histogram(ranks, nbins=30, title=f"Distribution of Ranks ({selected_year} - {selected_category})", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

        elif "3.3" in q3_choice:
            stats = analysis.get_score_summary_stats(df_master, year=selected_year, category=selected_category)
            if stats:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Mean Score", f"{stats['mean']:.2f}")
                c2.metric("Median Score", f"{stats['median']:.2f}")
                c3.metric("Min Score", f"{stats['min']:.2f}")
                c4.metric("Max Score", f"{stats['max']:.2f}")
                st.json(stats)

        elif "3.4" in q3_choice:
            q_df = analysis.get_score_quartiles(df_master, year=selected_year, category=selected_category)
            if not q_df.empty:
                fig = viz.plot_quartile_donut(q_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(q_df, use_container_width=True, hide_index=True)

        elif "3.5" in q3_choice:
            spread_df = analysis.get_score_spread_by_category(df_master, year=selected_year)
            if not spread_df.empty:
                fig = viz.plot_category_score_spread(spread_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(spread_df, use_container_width=True, hide_index=True)

    # ------------------ TAB 4: Bivariate & Correlation ------------------
    with tabs[3]:
        st.subheader("4. Bivariate Analysis and Correlation")
        q4_choice = st.selectbox(
            "Select Question:",
            [
                "4.1 RPC vs Overall Score Correlation",
                "4.2 Perception vs Overall Score Correlation",
                "4.3 Parameter with Strongest Correlation to Score",
                "4.4 TLR vs RPC Cross-Institutional Relation",
                "4.5 Research Score Correlation Evolution (2017–2025)",
                "🌟 Select-Two-Variables Dynamic Explorer"
            ]
        )

        if "4.1" in q4_choice:
            r, data = analysis.get_rpc_vs_score_correlation(df_master, year=selected_year, category=selected_category)
            st.metric("Correlation Coefficient (r)", f"{r:.3f}")
            if not data.empty:
                fig = viz.plot_scatter_with_trendline(data, "rpc", "score", corr_val=r, title=f"RPC vs Overall Score in {selected_year} (r = {r})")
                st.plotly_chart(fig, use_container_width=True)

        elif "4.2" in q4_choice:
            r, data = analysis.get_perception_vs_score_correlation(df_master, year=selected_year, category=selected_category)
            st.metric("Perception vs Score Correlation (r)", f"{r:.3f}")
            if not data.empty:
                fig = viz.plot_scatter_with_trendline(data, "perception", "score", corr_val=r, title=f"Perception vs Overall Score ({selected_year})")
                st.plotly_chart(fig, use_container_width=True)

        elif "4.3" in q4_choice:
            corrs = analysis.get_all_parameters_correlation(df_master, year=selected_year, category=selected_category)
            if not corrs.empty:
                fig = viz.plot_parameter_correlation_bar(corrs)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(corrs, use_container_width=True, hide_index=True)

        elif "4.4" in q4_choice:
            r, data = analysis.get_tlr_vs_rpc_relation(df_master, year=selected_year, category=selected_category)
            st.metric("TLR vs RPC Correlation (r)", f"{r:.3f}")
            if not data.empty:
                fig = viz.plot_scatter_with_trendline(data, "tlr", "rpc", corr_val=r, title=f"TLR vs RPC Scatter ({selected_year})")
                st.plotly_chart(fig, use_container_width=True)

        elif "4.5" in q4_choice:
            trend_df = analysis.get_correlation_trend_over_time(df_master, param1="rpc", param2="score", category=selected_category)
            if not trend_df.empty:
                fig = viz.plot_correlation_trend(trend_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(trend_df, use_container_width=True, hide_index=True)

        elif "Select-Two-Variables" in q4_choice:
            st.markdown("##### 🌟 Dynamic 2-Variable Scatter & Correlation Explorer")
            c1, c2 = st.columns(2)
            num_cols = ["score", "tlr", "rpc", "go", "oi", "perception", "rank"]
            v1 = c1.selectbox("Variable X", num_cols, index=1)
            v2 = c2.selectbox("Variable Y", num_cols, index=0)
            res = analysis.get_two_variable_correlation(df_master, v1, v2, year=selected_year, category=selected_category)
            st.metric("Pearson Correlation (r)", f"{res['r']:.3f}", f"Line: Y = {res['slope']}*X + {res['intercept']}")
            if not res["data"].empty:
                fig = viz.plot_scatter_with_trendline(res["data"], v1, v2, corr_val=res["r"])
                st.plotly_chart(fig, use_container_width=True)

    # ------------------ TAB 5: Multivariate Analysis ------------------
    with tabs[4]:
        st.subheader("5. Multivariate Analysis")
        q5_choice = st.selectbox(
            "Select Question:",
            [
                "5.1 Top 5 Radar/Spider Comparison Across 5 Parameters",
                "5.2 High Research but Low Teaching Institutions",
                "5.3 High Teaching but Low Perception Institutions",
                "5.4 Score Improved Despite Declining Parameter",
                "5.5 Largest Strongest vs Weakest Parameter Gap"
            ]
        )

        if "5.1" in q5_choice:
            top5 = analysis.get_top_n_multivariate_profile(df_master, year=selected_year, category=selected_category, top_n=5)
            if not top5.empty:
                fig = viz.plot_radar_comparison(top5)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(top5, use_container_width=True, hide_index=True)

        elif "5.2" in q5_choice:
            high_r_low_t = analysis.get_high_research_low_teaching(df_master, year=selected_year, category=selected_category)
            if not high_r_low_t.empty:
                st.write(f"Institutions with High RPC (>= 75th percentile) and Low TLR (<= 50th percentile) in {selected_year}:")
                st.dataframe(high_r_low_t, use_container_width=True, hide_index=True)
            else:
                st.info("No institutions met this threshold in the selected category and year.")

        elif "5.3" in q5_choice:
            high_t_low_p = analysis.get_high_teaching_low_perception(df_master, year=selected_year, category=selected_category)
            if not high_t_low_p.empty:
                st.write(f"Institutions with High TLR (>= 75th percentile) and Low Perception (<= 50th percentile) in {selected_year}:")
                st.dataframe(high_t_low_p, use_container_width=True, hide_index=True)
            else:
                st.info("No institutions met this threshold.")

        elif "5.4" in q5_choice:
            res_df = analysis.get_improved_score_with_declining_parameters(df_master, category=selected_category, start_year=2017, end_year=selected_year)
            if not res_df.empty:
                st.write(f"Institutions whose overall score increased from 2017 to {selected_year} despite drops in specific parameters:")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
            else:
                st.info("No matching institutions found.")

        elif "5.5" in q5_choice:
            gap_df = analysis.get_strongest_weakest_parameter_gap(df_master, year=selected_year, category=selected_category)
            if not gap_df.empty:
                fig = viz.plot_gap_bar(gap_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(gap_df, use_container_width=True, hide_index=True)

    # ------------------ TAB 6: Statistical Comparison ------------------
    with tabs[5]:
        st.subheader("6. Distribution and Statistical Comparison")
        q6_choice = st.selectbox(
            "Select Question:",
            [
                "6.1 Top 10 vs Remaining Institutions Score Distribution",
                "6.2 Score Dispersion Across Years",
                "6.3 Parameter Variability (Coefficient of Variation)",
                "6.4 Median and IQR Evolution Over Time",
                "6.5 State-wise Score Distribution"
            ]
        )

        if "6.1" in q6_choice:
            summary, t10, rest = analysis.compare_top10_vs_rest(df_master, year=selected_year, category=selected_category)
            st.dataframe(summary, use_container_width=True, hide_index=True)
            fig = viz.plot_top10_vs_rest_box(t10, rest)
            st.plotly_chart(fig, use_container_width=True)

        elif "6.2" in q6_choice:
            disp_df = analysis.compare_score_dispersion_across_years(df_master, category=selected_category)
            if not disp_df.empty:
                fig = viz.plot_dispersion_trend(disp_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(disp_df, use_container_width=True, hide_index=True)

        elif "6.3" in q6_choice:
            var_df = analysis.get_parameter_variability(df_master, year=selected_year, category=selected_category)
            if not var_df.empty:
                st.write(f"Parameter variability ranked by Coefficient of Variation (CV %) in {selected_year}:")
                fig = px.bar(var_df, x="parameter", y="coefficient_of_variation_pct", text="coefficient_of_variation_pct",
                             title="Parameter Variability (Coefficient of Variation %)", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(var_df, use_container_width=True, hide_index=True)

        elif "6.4" in q6_choice:
            trend_df = analysis.get_median_iqr_trend(df_master, category=selected_category)
            if not trend_df.empty:
                fig = px.line(trend_df, x="year", y=["median", "iqr"], markers=True, title="Median Score and Interquartile Range (IQR) Over Time", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(trend_df, use_container_width=True, hide_index=True)

        elif "6.5" in q6_choice:
            state_scores = analysis.get_state_score_distribution(df_master, year=selected_year, category=selected_category)
            if not state_scores.empty:
                fig = viz.plot_state_score_box(state_scores)
                st.plotly_chart(fig, use_container_width=True)

    # ------------------ TAB 7: Ranking Transitions ------------------
    with tabs[6]:
        st.subheader("7. Ranking Transitions and Institutional Mobility")
        q7_choice = st.selectbox(
            "Select Question:",
            [
                "7.1 51–100 Band into Top 50 Transitions",
                "7.2 Top 10 Entries and Exits",
                "7.3 Percentage Retained in Same Rank Band",
                "7.4 Largest Upward and Downward Rank Movements",
                "7.5 Up, Down, Retained Mobility Breakdown"
            ]
        )

        c1, c2 = st.columns(2)
        y1 = c1.selectbox("Base Year", sorted(all_years), index=sorted(all_years).index(2023) if 2023 in all_years else 0, key="t_y1")
        y2 = c2.selectbox("Comparison Year", sorted(all_years), index=sorted(all_years).index(2024) if 2024 in all_years else 1, key="t_y2")

        if "7.1" in q7_choice:
            trans_df = analysis.get_band_to_top50_transitions(df_master, category=selected_category, year1=y1, year2=y2)
            if not trans_df.empty:
                fig = viz.plot_band_transitions_scatter(trans_df, y1, y2)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(trans_df, use_container_width=True, hide_index=True)
            else:
                st.info(f"No institutions moved from 51–100 in {y1} to Top 50 in {y2} in {selected_category}.")

        elif "7.2" in q7_choice:
            t10_info = analysis.get_top10_entries_and_exits(df_master, category=selected_category, year1=y1, year2=y2)
            c_in, c_out = st.columns(2)
            c_in.success(f"**New Entrants in Top 10 ({y2}):**\n\n" + ("\n".join(f"- {e}" for e in t10_info["entries"]) if t10_info["entries"] else "None"))
            c_out.error(f"**Exited Top 10 ({y1} -> {y2}):**\n\n" + ("\n".join(f"- {e}" for e in t10_info["exits"]) if t10_info["exits"] else "None"))

        elif "7.3" in q7_choice:
            band_df, overall_pct = analysis.get_percentage_retained_in_band(df_master, category=selected_category, year1=y1, year2=y2)
            st.metric("Overall Rank Band Retention", f"{overall_pct}%")
            st.dataframe(band_df, use_container_width=True, hide_index=True)

        elif "7.4" in q7_choice:
            up, down = analysis.get_largest_upward_downward_shifts(df_master, category=selected_category, year1=y1, year2=y2)
            col_u, col_d = st.columns(2)
            with col_u:
                st.markdown("**Largest Upward Climbs:**")
                st.dataframe(up[["name", "rank_prev", "rank_curr", "rank_shift"]], use_container_width=True, hide_index=True)
            with col_d:
                st.markdown("**Largest Downward Drops:**")
                st.dataframe(down[["name", "rank_prev", "rank_curr", "rank_shift"]], use_container_width=True, hide_index=True)

        elif "7.5" in q7_choice:
            mob = analysis.get_mobility_summary(df_master, category=selected_category, year1=y1, year2=y2)
            fig = viz.plot_mobility_donut(mob)
            st.plotly_chart(fig, use_container_width=True)
            st.json(mob)

    # ------------------ TAB 8: Outliers and Performance Gaps ------------------
    with tabs[7]:
        st.subheader("8. Outlier Detection and Performance Gaps")
        q8_choice = st.selectbox(
            "Select Question:",
            [
                "8.1 High Research Scores Relative to Overall Score",
                "8.2 Research vs Teaching Gap (RPC - TLR)",
                "8.3 Unusually Large Year-to-Year Score Changes (Z-score)",
                "8.4 Strong Parameter Score but Poor Overall Rank",
                "8.5 Institutional Ranking Volatility (Std Dev of Ranks)"
            ]
        )

        if "8.1" in q8_choice:
            out_df = analysis.get_research_score_outliers(df_master, year=selected_year, category=selected_category)
            if not out_df.empty:
                fig = viz.plot_residual_outliers(out_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(out_df, use_container_width=True, hide_index=True)
            else:
                st.info("No residual outliers detected at this threshold.")

        elif "8.2" in q8_choice:
            gap_df = analysis.get_research_teaching_gap_outliers(df_master, year=selected_year, category=selected_category)
            if not gap_df.empty:
                st.write(f"Top institutions performing substantially better in Research than Teaching ({selected_year}):")
                st.dataframe(gap_df, use_container_width=True, hide_index=True)

        elif "8.3" in q8_choice:
            z_df = analysis.get_score_change_outliers(df_master, category=selected_category, year1=2023, year2=selected_year)
            if not z_df.empty:
                st.write(f"Score change outliers (Z-score >= 2.0) from 2023 to {selected_year}:")
                st.dataframe(z_df[["name", "s1", "s2", "score_change", "z_score"]], use_container_width=True, hide_index=True)
            else:
                st.info("No score change outliers detected.")

        elif "8.4" in q8_choice:
            param_sel = st.selectbox("Select Parameter:", ["rpc", "tlr", "go", "oi", "perception"])
            poor_rank = analysis.get_strong_param_poor_rank(df_master, year=selected_year, category=selected_category, param=param_sel)
            if not poor_rank.empty:
                st.write(f"Institutions with Top 25% {param_sel.upper()} score but Rank > 50 in {selected_year}:")
                st.dataframe(poor_rank, use_container_width=True, hide_index=True)
            else:
                st.info("No matching institutions found.")

        elif "8.5" in q8_choice:
            vol_df = analysis.get_rank_volatility(df_master, category=selected_category, min_years=4)
            if not vol_df.empty:
                fig = viz.plot_volatility_bar(vol_df)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(vol_df, use_container_width=True, hide_index=True)


# ==============================================================================
# 3. DYNAMIC ANALYSIS (LEVEL 2: 5 MARKS)
# ==============================================================================
elif menu_choice == "⚡ Dynamic Analysis (Level 2)":
    st.markdown('<div class="main-header">⚡ Dynamic Analysis Engine (Level 2)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Dynamically explore combinations of variables, categories, filters, and custom chart types for unseen questions.</div>', unsafe_allow_html=True)

    with st.expander("🛠️ Configure Dynamic Filters & Aggregations", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        dyn_year = f_col1.multiselect("Filter Years:", all_years, default=[all_years[0]])
        dyn_cat = f_col2.multiselect("Filter Categories:", all_categories, default=["Overall"])
        rank_range = f_col3.slider("Rank Range:", min_value=1, max_value=200, value=(1, 100))

        v_col1, v_col2, v_col3, v_col4 = st.columns(4)
        num_fields = ["score", "tlr", "rpc", "go", "oi", "perception", "rank"]
        x_axis = v_col1.selectbox("X-Axis Variable", num_fields, index=1)
        y_axis = v_col2.selectbox("Y-Axis Variable", num_fields, index=0)
        group_by = v_col3.selectbox("Color / Group By", ["category", "state", "year", "None"], index=0)
        chart_type = v_col4.selectbox("Chart Type", ["Scatter Plot with Trendline", "Box Plot", "Grouped Bar", "Histogram"])

    # Filter data dynamically
    dyn_filtered = df_master.copy()
    if dyn_year:
        dyn_filtered = dyn_filtered[dyn_filtered["year"].isin(dyn_year)]
    if dyn_cat:
        dyn_filtered = dyn_filtered[dyn_filtered["category"].isin(dyn_cat)]
    dyn_filtered = dyn_filtered[(dyn_filtered["rank"] >= rank_range[0]) & (dyn_filtered["rank"] <= rank_range[1])]

    if dyn_filtered.empty:
        st.warning("No records match the selected dynamic filters. Try broadening your criteria.")
    else:
        st.markdown(f"**Filtered Records Matching Criteria:** `{len(dyn_filtered)}` records.")

        # Chart Generation Logic
        color_field = None if group_by == "None" else group_by

        if chart_type == "Scatter Plot with Trendline":
            valid_scatter = dyn_filtered.dropna(subset=[x_axis, y_axis])
            if len(valid_scatter) > 1:
                r_val = valid_scatter[x_axis].corr(valid_scatter[y_axis])
                fig = px.scatter(
                    valid_scatter,
                    x=x_axis,
                    y=y_axis,
                    color=color_field,
                    trendline="ols",
                    hover_data=["name", "rank", "score", "category", "year"],
                    title=f"Dynamic Scatter: {x_axis.upper()} vs {y_axis.upper()} (Pearson r = {r_val:.3f})",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Not enough valid data points for scatter plot.")

        elif chart_type == "Box Plot":
            fig = px.box(
                dyn_filtered,
                x=color_field if color_field else "category",
                y=y_axis,
                color=color_field,
                points="outliers",
                title=f"Box Plot of {y_axis.upper()}",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Grouped Bar":
            agg_df = dyn_filtered.groupby([color_field if color_field else "category"])[y_axis].mean().reset_index()
            fig = px.bar(
                agg_df,
                x=color_field if color_field else "category",
                y=y_axis,
                text=agg_df[y_axis].round(2),
                title=f"Average {y_axis.upper()} Grouped by {color_field if color_field else 'Category'}",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Histogram":
            fig = px.histogram(
                dyn_filtered,
                x=x_axis,
                color=color_field,
                nbins=25,
                marginal="box",
                title=f"Distribution Histogram of {x_axis.upper()}",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Download button for filtered dataset
        csv_data = dyn_filtered.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Filtered Data as CSV", data=csv_data, file_name="nirf_dynamic_export.csv", mime="text/csv")


# ==============================================================================
# 4. ASK NIRF DATA (LEVEL 3: 5 MARKS)
# ==============================================================================
elif menu_choice == "💬 Ask NIRF Data (Level 3)":
    st.markdown('<div class="main-header">💬 Ask NIRF Data: Natural-Language Query Interface</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask analytical questions in plain English. The local rule-based AI engine parses entities and generates charts on the fly.</div>', unsafe_allow_html=True)

    # Example questions buttons
    st.markdown("**Sample Questions You Can Ask:**")
    sample_queries = [
        "Which states have the most Engineering institutions in the top 100 in 2025?",
        "How has the overall NIRF ranking of Indian Institute of Technology Madras changed from 2017 to 2025?",
        "What is the correlation between TLR and RPC in 2024?",
        "Which institutions showed the greatest improvement in rank from 2017 to 2024 in Overall?",
        "Compare Karnataka with Tamil Nadu in 2024 in Overall",
        "Which institutions entered or exited the top 10 between 2023 and 2024?"
    ]

    selected_sample = None
    cols = st.columns(2)
    for i, sq in enumerate(sample_queries):
        if cols[i % 2].button(f"💡 {sq}", key=f"sq_{i}"):
            selected_sample = sq

    user_query = st.text_input("Enter your natural-language question:", value=selected_sample or "")

    if user_query:
        # Known institutions for accurate named entity recognition
        known_insts = df_master["name"].unique()
        plan = parse_query(user_query, known_institutions=known_insts)

        with st.expander("🔍 Inspect Interpreted Query Plan (Rule-based Parser)", expanded=False):
            st.json(plan)

        with st.spinner("Analyzing NIRF dataset and generating visualization..."):
            exec_res = execute_query(plan, df_master)

        st.markdown("### 📊 Findings")
        st.markdown(exec_res["summary_text"])

        if exec_res["figure"] is not None:
            st.plotly_chart(exec_res["figure"], use_container_width=True)

        if not exec_res["data"].empty:
            with st.expander("View Underlying Data Table"):
                st.dataframe(exec_res["data"], use_container_width=True, hide_index=True)


# ==============================================================================
# 5. MANUAL FILE IMPORT
# ==============================================================================
elif menu_choice == "📁 Manual File Import":
    st.markdown('<div class="main-header">📁 Manual Data Import</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload supplementary CSV or Excel files (e.g. newly published rankings, un-scraped categories, or custom spreadsheets).</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        imported_df, err = load_manual_file(uploaded_file, uploaded_file.name)
        if err:
            st.error(f"Error loading file: {err}")
        else:
            st.success(f"Successfully loaded file: `{uploaded_file.name}` with `{len(imported_df)}` rows!")
            st.dataframe(imported_df.head(10), use_container_width=True)

            if st.button("Merge into Current Session Dataset"):
                # Preprocess imported df
                from src.preprocessing import preprocess_nirf_dataframe
                cleaned_imported = preprocess_nirf_dataframe(imported_df)
                st.session_state["custom_data"] = cleaned_imported
                st.success(f"Merged `{len(cleaned_imported)}` records into active session!")


# ==============================================================================
# 6. DATA QUALITY & COVERAGE
# ==============================================================================
elif menu_choice == "📋 Data Quality & Coverage":
    st.markdown('<div class="main-header">📋 Data Coverage & Quality Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Audit metrics verifying complete 2017–2025 NIRF ranking integrity.</div>', unsafe_allow_html=True)

    if not df_master.empty:
        # Run validation
        val_res = validate_master_dataset(df_master)

        c1, c2, c3 = st.columns(3)
        c1.metric("Validation Status", "PASSED" if val_res["valid"] else "WARNINGS")
        c2.metric("Total Records", f"{val_res['total_records']:,}")
        c3.metric("Duplicate Records Found", f"{val_res['duplicate_records']}")

        st.markdown("---")

        st.subheader("Records Collected per Year")
        year_counts = df_master["year"].value_counts().sort_index().reset_index()
        year_counts.columns = ["Year", "Record Count"]
        fig_yr = px.bar(year_counts, x="Year", y="Record Count", text="Record Count", color="Record Count", color_continuous_scale="Blues", template="plotly_white")
        st.plotly_chart(fig_yr, use_container_width=True)

        st.subheader("Records Collected per Category")
        cat_counts = df_master["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Record Count"]
        fig_cat = px.bar(cat_counts, x="Category", y="Record Count", text="Record Count", color="Record Count", color_continuous_scale="Teal", template="plotly_white")
        st.plotly_chart(fig_cat, use_container_width=True)

        st.subheader("Missing Value Summary")
        missing_df = pd.DataFrame({
            "Column": df_master.columns,
            "Missing Count": df_master.isnull().sum().values,
            "Missing %": (df_master.isnull().sum().values / len(df_master) * 100).round(2)
        })
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
