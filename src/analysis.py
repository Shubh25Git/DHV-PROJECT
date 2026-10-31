"""
Analysis Module - Core Statistical and Analytical Functions
============================================================
This module implements all analytical logic for the DHV NIRF Ranking project,
directly covering all 8 analytical groups and 40 sample questions specified in Annexure A.

Coding style:
- Beginner-friendly Python.
- Straightforward Pandas operations (filter, group, sort, aggregate).
- Clear, descriptive variable names.
- Explicit comments explaining the analytical purpose of each step.
- Resilient to missing parameters or edge cases.
"""

import os
import sys
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==============================================================================
# Helper / General Utility Functions
# ==============================================================================

def filter_data(df, year=None, category=None):
    """
    Helper function to filter the master DataFrame by year and category.
    If year or category is None or 'All', that filter is omitted.
    """
    filtered = df.copy()
    if year is not None and str(year).lower() != "all":
        filtered = filtered[filtered["year"] == int(year)]
    if category is not None and str(category).lower() != "all":
        filtered = filtered[filtered["category"].str.lower() == str(category).lower()]
    return filtered


# ==============================================================================
# 1. TIME-SERIES AND TREND ANALYSIS
# ==============================================================================

def get_institution_rank_trend(df, institution_name, category="Overall"):
    """
    Q1.1: How has the overall NIRF ranking of a selected institution changed from 2017 to 2025?
    
    Inputs:
    - df: master DataFrame
    - institution_name: string, name of institution (case-insensitive search)
    - category: string, ranking category (e.g. 'Overall')
    
    Returns:
    - DataFrame containing year, name, rank, score sorted chronologically by year.
    """
    # Filter by category
    subset = filter_data(df, category=category)
    # Search for institution name case-insensitively
    mask = subset["name"].str.contains(institution_name, case=False, na=False)
    result = subset[mask][["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]]
    return result.sort_values("year").reset_index(drop=True)


def get_biggest_rank_improvements(df, category="Overall", start_year=2017, end_year=2025, limit=10):
    """
    Q1.2: Which institutions have shown the greatest improvement in rank over the nine years?
    Rank improvement = (Rank in start_year) - (Rank in end_year).
    A positive number means the rank improved (e.g. 50 -> 10 = +40 improvement).
    """
    subset = filter_data(df, category=category)
    start_df = subset[subset["year"] == start_year][["name", "rank", "score"]].rename(
        columns={"rank": "start_rank", "score": "start_score"}
    )
    end_df = subset[subset["year"] == end_year][["name", "rank", "score"]].rename(
        columns={"rank": "end_rank", "score": "end_score"}
    )
    
    # Merge both years on institution name
    merged = pd.merge(start_df, end_df, on="name", how="inner")
    # Positive rank_diff means improved rank
    merged["rank_improvement"] = merged["start_rank"] - merged["end_rank"]
    
    # Sort descending so biggest improvement comes first
    result = merged.sort_values(by="rank_improvement", ascending=False).head(limit)
    return result.reset_index(drop=True)


def get_biggest_rank_declines(df, category="Overall", start_year=2017, end_year=2025, limit=10):
    """
    Q1.3: Which institutions have experienced the largest decline in ranking?
    Rank decline = (Rank in end_year) - (Rank in start_year).
    A positive number means the rank worsened (e.g. 10 -> 50 = +40 decline).
    """
    subset = filter_data(df, category=category)
    start_df = subset[subset["year"] == start_year][["name", "rank", "score"]].rename(
        columns={"rank": "start_rank", "score": "start_score"}
    )
    end_df = subset[subset["year"] == end_year][["name", "rank", "score"]].rename(
        columns={"rank": "end_rank", "score": "end_score"}
    )
    
    merged = pd.merge(start_df, end_df, on="name", how="inner")
    merged["rank_decline"] = merged["end_rank"] - merged["start_rank"]
    
    # Sort descending so biggest drop in rank comes first
    result = merged.sort_values(by="rank_decline", ascending=False).head(limit)
    return result.reset_index(drop=True)


def get_average_score_trend(df, category="Overall"):
    """
    Q1.4: How has the average score of institutions changed over time?
    Calculates mean, median, min, max score for each year in the category.
    """
    subset = filter_data(df, category=category)
    # Group by year and calculate score statistics
    trend = subset.groupby("year")["score"].agg(
        mean_score="mean",
        median_score="median",
        min_score="min",
        max_score="max",
        count="count"
    ).reset_index()
    return trend.round(2)


def get_consistent_top_institutions(df, category="Overall", top_n=10, min_years=5):
    """
    Q1.5: Which institutions have remained consistently in the top 10 across multiple years?
    """
    subset = filter_data(df, category=category)
    # Filter only records where rank is in the top N
    top_records = subset[subset["rank"] <= top_n]
    # Count how many distinct years each institution appeared in the top N
    counts = top_records.groupby("name")["year"].agg(
        years_in_top=lambda s: sorted(list(s.unique())),
        frequency="count"
    ).reset_index()
    # Filter for institutions meeting min_years threshold
    consistent = counts[counts["frequency"] >= min_years].sort_values(by="frequency", ascending=False)
    return consistent.reset_index(drop=True)


# ==============================================================================
# 2. GEOSPATIAL AND REGIONAL ANALYSIS
# ==============================================================================

def get_states_top_institutions(df, year=2024, category="Overall", top_n=100, limit=10):
    """
    Q2.1: Which states have the highest number of institutions in the top 100?
    """
    subset = filter_data(df, year=year, category=category)
    top_institutions = subset[subset["rank"] <= top_n]
    # Count institutions per state
    state_counts = top_institutions.groupby("state")["name"].count().reset_index()
    state_counts.columns = ["state", "institution_count"]
    # Sort descending
    result = state_counts.sort_values(by="institution_count", ascending=False).head(limit)
    return result.reset_index(drop=True)


def get_geo_distribution_trend(df, category="Overall", top_n=100):
    """
    Q2.2: How is the geographical distribution of top-ranked institutions changing from 2017 to 2025?
    Produces a pivot table with states as rows and years as columns showing institution counts.
    """
    subset = filter_data(df, category=category)
    top_institutions = subset[subset["rank"] <= top_n]
    pivot = pd.pivot_table(
        top_institutions,
        index="state",
        columns="year",
        values="name",
        aggfunc="count",
        fill_value=0
    ).reset_index()
    # Add a total column for sorting
    year_cols = [c for c in pivot.columns if c != "state"]
    pivot["total_across_years"] = pivot[year_cols].sum(axis=1)
    pivot = pivot.sort_values(by="total_across_years", ascending=False).drop(columns=["total_across_years"])
    return pivot.reset_index(drop=True)


def get_state_representation_growth(df, category="Overall", start_year=2017, end_year=2025, top_n=100):
    """
    Q2.3: Which states have improved their representation in the top 100 over time?
    Growth = (Count in end_year) - (Count in start_year).
    """
    subset = filter_data(df, category=category)
    top_institutions = subset[subset["rank"] <= top_n]
    
    start_counts = top_institutions[top_institutions["year"] == start_year].groupby("state")["name"].count().reset_index(name="start_count")
    end_counts = top_institutions[top_institutions["year"] == end_year].groupby("state")["name"].count().reset_index(name="end_count")
    
    merged = pd.merge(start_counts, end_counts, on="state", how="outer").fillna(0)
    merged["growth"] = merged["end_count"] - merged["start_count"]
    result = merged.sort_values(by="growth", ascending=False)
    return result.reset_index(drop=True)


def compare_two_states(df, state1="Karnataka", state2="Tamil Nadu", category="Overall", year=2024):
    """
    Q2.4: How do the rankings of institutions in Karnataka compare with those in Tamil Nadu?
    Compares average score, average rank, top institution, and count of institutions.
    """
    subset = filter_data(df, year=year, category=category)
    s1_data = subset[subset["state"].str.lower() == state1.lower()]
    s2_data = subset[subset["state"].str.lower() == state2.lower()]
    
    summary = []
    for state_name, data in [(state1, s1_data), (state2, s2_data)]:
        best_inst = data.sort_values("rank").iloc[0]["name"] if not data.empty else "None"
        best_rank = data["rank"].min() if not data.empty else np.nan
        summary.append({
            "state": state_name,
            "total_institutions": len(data),
            "average_score": round(data["score"].mean(), 2) if not data.empty else np.nan,
            "average_rank": round(data["rank"].mean(), 2) if not data.empty else np.nan,
            "top_institution": best_inst,
            "top_rank": best_rank
        })
    return pd.DataFrame(summary), pd.concat([s1_data, s2_data], ignore_index=True)


def compare_two_institutions(df, inst1, inst2, category="Overall", year=2024):
    """
    Compares two institutions on score, rank, and NIRF parameters for a specific category and year.
    Returns:
    - DataFrame containing the records for both institutions.
    """
    subset = filter_data(df, year=year, category=category)
    m1 = subset["name"].str.contains(inst1, case=False, na=False) if inst1 else pd.Series(False, index=subset.index)
    m2 = subset["name"].str.contains(inst2, case=False, na=False) if inst2 else pd.Series(False, index=subset.index)
    
    comp_df = pd.concat([subset[m1], subset[m2]], ignore_index=True)
    return comp_df.drop_duplicates(subset=["name", "year", "category"]).reset_index(drop=True)



def get_newly_appearing_institutions_by_state(df, category="Overall", base_year=2017, recent_year=2024):
    """
    Q2.5: Which states have produced the largest number of newly appearing institutions in the rankings?
    Newly appearing = institutions present in recent_year that were not ranked in base_year.
    """
    subset = filter_data(df, category=category)
    base_insts = set(subset[subset["year"] == base_year]["name"].unique())
    recent_df = subset[subset["year"] == recent_year]
    
    # Filter for institutions not present in base year
    new_institutions = recent_df[~recent_df["name"].isin(base_insts)]
    state_new_counts = new_institutions.groupby("state")["name"].count().reset_index(name="new_institutions_count")
    result = state_new_counts.sort_values(by="new_institutions_count", ascending=False)
    return result.reset_index(drop=True), new_institutions


# ==============================================================================
# 3. UNIVARIATE ANALYSIS
# ==============================================================================

def get_score_distribution(df, year=2024, category="Overall"):
    """
    Q3.1: What is the distribution of NIRF scores for a selected year?
    Returns clean score series with summary stats.
    """
    subset = filter_data(df, year=year, category=category)
    scores = subset["score"].dropna()
    return scores


def get_rank_distribution(df, year=2024, category="Overall"):
    """
    Q3.2: What is the distribution of overall ranks across all institutions?
    """
    subset = filter_data(df, year=year, category=category)
    ranks = subset["rank"].dropna()
    return ranks


def get_score_summary_stats(df, year=2024, category="Overall"):
    """
    Q3.3: What is the average, median, minimum, and maximum score in a given year?
    """
    subset = filter_data(df, year=year, category=category)
    scores = subset["score"].dropna()
    if scores.empty:
        return {}
    return {
        "year": year,
        "category": category,
        "count": len(scores),
        "mean": round(float(scores.mean()), 2),
        "median": round(float(scores.median()), 2),
        "min": round(float(scores.min()), 2),
        "max": round(float(scores.max()), 2),
        "std_dev": round(float(scores.std()), 2)
    }


def get_score_quartiles(df, year=2024, category="Overall"):
    """
    Q3.4: What percentage of ranked institutions fall into each score quartile?
    Divides scores into 4 quartiles: Q1 (0-25%), Q2 (25-50%), Q3 (50-75%), Q4 (75-100%).
    """
    subset = filter_data(df, year=year, category=category)
    scores = subset["score"].dropna()
    if scores.empty:
        return pd.DataFrame()

    q1 = scores.quantile(0.25)
    q2 = scores.quantile(0.50)
    q3 = scores.quantile(0.75)

    def assign_quartile(val):
        if val <= q1:
            return f"Q1 (<= {q1:.1f})"
        elif val <= q2:
            return f"Q2 ({q1:.1f} - {q2:.1f})"
        elif val <= q3:
            return f"Q3 ({q2:.1f} - {q3:.1f})"
        else:
            return f"Q4 (> {q3:.1f})"

    quartile_series = scores.apply(assign_quartile)
    counts = quartile_series.value_counts().reset_index()
    counts.columns = ["quartile", "count"]
    counts["percentage"] = round((counts["count"] / len(scores)) * 100, 2)
    return counts


def get_score_spread_by_category(df, year=2024):
    """
    Q3.5: How does the spread of scores differ across NIRF categories?
    Computes IQR, standard deviation, min, max across all categories for a year.
    """
    subset = df[df["year"] == int(year)]
    stats = subset.groupby("category")["score"].agg(
        institutions="count",
        mean="mean",
        std_dev="std",
        q25=lambda x: x.quantile(0.25),
        median="median",
        q75=lambda x: x.quantile(0.75),
        min="min",
        max="max"
    ).reset_index()
    stats["iqr"] = stats["q75"] - stats["q25"]
    return stats.round(2).sort_values(by="mean", ascending=False).reset_index(drop=True)


# ==============================================================================
# 4. BIVARIATE ANALYSIS AND CORRELATION
# ==============================================================================

def get_rpc_vs_score_correlation(df, year=2024, category="Overall"):
    """
    Q4.1: How strongly are Research and Professional Practice (RPC) scores associated with overall scores?
    Returns Pearson correlation coefficient (r) and (rpc, score) data points.
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["rpc", "score"])
    if len(subset) < 2:
        return 0.0, pd.DataFrame()
    corr = float(subset["rpc"].corr(subset["score"]))
    return round(corr, 3), subset[["name", "rpc", "score", "rank"]]


def get_perception_vs_score_correlation(df, year=2024, category="Overall"):
    """
    Q4.2: How does Perception (PR) relate to overall scores?
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["perception", "score"])
    if len(subset) < 2:
        return 0.0, pd.DataFrame()
    corr = float(subset["perception"].corr(subset["score"]))
    return round(corr, 3), subset[["name", "perception", "score", "rank"]]


def get_all_parameters_correlation(df, year=2024, category="Overall"):
    """
    Q4.3: Which NIRF parameter has the strongest correlation with the overall score?
    Evaluates correlation of score with [tlr, rpc, go, oi, perception].
    """
    params = ["tlr", "rpc", "go", "oi", "perception"]
    subset = filter_data(df, year=year, category=category)
    correlations = []
    
    for p in params:
        if p in subset.columns:
            valid_pairs = subset.dropna(subset=[p, "score"])
            if len(valid_pairs) > 1:
                r = valid_pairs[p].corr(valid_pairs["score"])
                correlations.append({"parameter": p.upper(), "correlation_with_score": round(float(r), 3)})
    
    corr_df = pd.DataFrame(correlations).sort_values(by="correlation_with_score", ascending=False)
    return corr_df.reset_index(drop=True)


def get_tlr_vs_rpc_relation(df, year=2024, category="Overall"):
    """
    Q4.4: How are TLR and RPC scores related across institutions?
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["tlr", "rpc"])
    corr = float(subset["tlr"].corr(subset["rpc"])) if len(subset) > 1 else 0.0
    return round(corr, 3), subset[["name", "tlr", "rpc", "score", "rank"]]


def get_correlation_trend_over_time(df, param1="rpc", param2="score", category="Overall"):
    """
    Q4.5: Has the correlation between research scores and overall scores changed from 2017 to 2025?
    Calculates Pearson r between param1 and param2 for each year.
    """
    subset = filter_data(df, category=category)
    trends = []
    for yr in sorted(subset["year"].unique()):
        year_data = subset[subset["year"] == yr].dropna(subset=[param1, param2])
        if len(year_data) > 2:
            r = year_data[param1].corr(year_data[param2])
            trends.append({"year": int(yr), "correlation": round(float(r), 3)})
    return pd.DataFrame(trends)


def get_two_variable_correlation(df, var1, var2, year=2024, category="Overall"):
    """
    Dynamic 2-Variable Feature:
    Allows user to select ANY two numerical variables and immediately get scatter data,
    correlation coefficient r, and linear regression trend line slope & intercept.
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=[var1, var2])
    if len(subset) < 2:
        return {"r": 0.0, "slope": 0.0, "intercept": 0.0, "data": pd.DataFrame()}
    
    corr = float(subset[var1].corr(subset[var2]))
    # Compute simple linear regression line: y = m*x + c
    x = subset[var1].values
    y = subset[var2].values
    m, c = np.polyfit(x, y, 1) if len(x) > 1 else (0.0, 0.0)
    
    return {
        "r": round(corr, 3),
        "slope": round(float(m), 3),
        "intercept": round(float(c), 3),
        "data": subset[["name", var1, var2, "score", "rank"]]
    }


# ==============================================================================
# 5. MULTIVARIATE ANALYSIS
# ==============================================================================

def get_top_n_multivariate_profile(df, year=2024, category="Overall", top_n=5):
    """
    Q5.1: How do the top five institutions compare across all five NIRF parameters?
    Returns parameter values for top N institutions (ideal for radar charts or parallel coordinates).
    """
    subset = filter_data(df, year=year, category=category).sort_values("rank").head(top_n)
    cols = ["name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
    return subset[cols].reset_index(drop=True)


def get_high_research_low_teaching(df, year=2024, category="Overall", percentile_high=75, percentile_low=50):
    """
    Q5.2: Which institutions have high research scores but relatively low teaching scores?
    High research = RPC >= 75th percentile.
    Low teaching = TLR <= 50th percentile.
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["rpc", "tlr"])
    if subset.empty:
        return pd.DataFrame()
    
    rpc_cutoff = subset["rpc"].quantile(percentile_high / 100.0)
    tlr_cutoff = subset["tlr"].quantile(percentile_low / 100.0)
    
    matches = subset[(subset["rpc"] >= rpc_cutoff) & (subset["tlr"] <= tlr_cutoff)]
    matches = matches[["name", "rank", "score", "rpc", "tlr"]].sort_values(by="rpc", ascending=False)
    return matches.reset_index(drop=True)


def get_high_teaching_low_perception(df, year=2024, category="Overall", percentile_high=75, percentile_low=50):
    """
    Q5.3: Which institutions have high teaching scores but relatively low perception scores?
    High teaching = TLR >= 75th percentile.
    Low perception = PERCEPTION <= 50th percentile.
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["tlr", "perception"])
    if subset.empty:
        return pd.DataFrame()
    
    tlr_cutoff = subset["tlr"].quantile(percentile_high / 100.0)
    pr_cutoff = subset["perception"].quantile(percentile_low / 100.0)
    
    matches = subset[(subset["tlr"] >= tlr_cutoff) & (subset["perception"] <= pr_cutoff)]
    matches = matches[["name", "rank", "score", "tlr", "perception"]].sort_values(by="tlr", ascending=False)
    return matches.reset_index(drop=True)


def get_improved_score_with_declining_parameters(df, category="Overall", start_year=2017, end_year=2024):
    """
    Q5.4: Which institutions have improved their overall scores despite declining scores in one or more parameters?
    """
    subset = filter_data(df, category=category)
    s_df = subset[subset["year"] == start_year].set_index("name")
    e_df = subset[subset["year"] == end_year].set_index("name")
    
    common = s_df.index.intersection(e_df.index)
    results = []
    
    for name in common:
        s_score = s_df.loc[name, "score"]
        e_score = e_df.loc[name, "score"]
        if pd.isna(s_score) or pd.isna(e_score):
            continue
        score_diff = e_score - s_score
        if score_diff > 0:
            declined_params = []
            param_changes = {}
            worst_decline = 0.0
            for p in ["tlr", "rpc", "go", "oi", "perception"]:
                if pd.notna(e_df.loc[name, p]) and pd.notna(s_df.loc[name, p]):
                    diff = round(float(e_df.loc[name, p] - s_df.loc[name, p]), 2)
                    param_changes[f"{p}_change"] = diff
                    if diff < 0:
                        declined_params.append(p.upper())
                        if diff < worst_decline:
                            worst_decline = diff
                else:
                    param_changes[f"{p}_change"] = None
            if declined_params:
                results.append({
                    "name": name,
                    "score_improvement": round(float(score_diff), 2),
                    "start_score": round(float(s_score), 2),
                    "end_score": round(float(e_score), 2),
                    "declined_parameters": ", ".join(declined_params),
                    "num_declined": len(declined_params),
                    "worst_decline": worst_decline,
                    **param_changes
                })
    
    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values(by="score_improvement", ascending=False).reset_index(drop=True)
    return res_df


def get_strongest_weakest_parameter_gap(df, year=2024, category="Overall", limit=10):
    """
    Q5.5: Which institutions have the largest difference between their strongest and weakest parameters?
    Gap = Max(TLR, RPC, GO, OI, PR) - Min(TLR, RPC, GO, OI, PR).
    """
    params = ["tlr", "rpc", "go", "oi", "perception"]
    subset = filter_data(df, year=year, category=category).dropna(subset=params)
    if subset.empty:
        return pd.DataFrame()
    
    data = subset.copy()
    data["max_param"] = data[params].max(axis=1)
    data["min_param"] = data[params].min(axis=1)
    data["gap"] = data["max_param"] - data["min_param"]
    
    # Identify which parameter was max and min
    data["strongest"] = data[params].idxmax(axis=1).str.upper()
    data["weakest"] = data[params].idxmin(axis=1).str.upper()
    
    cols = ["name", "rank", "score", "gap", "strongest", "max_param", "weakest", "min_param"]
    result = data[cols].sort_values(by="gap", ascending=False).head(limit)
    return result.round(2).reset_index(drop=True)


# ==============================================================================
# 6. DISTRIBUTION AND STATISTICAL COMPARISON
# ==============================================================================

def compare_top10_vs_rest(df, year=2024, category="Overall"):
    """
    Q6.1: How does the score distribution differ between the top 10 and the remaining institutions?
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["score", "rank"])
    top10 = subset[subset["rank"] <= 10]["score"]
    rest = subset[subset["rank"] > 10]["score"]
    
    summary = pd.DataFrame([
        {
            "group": "Top 10",
            "count": len(top10),
            "mean": round(float(top10.mean()), 2),
            "median": round(float(top10.median()), 2),
            "std_dev": round(float(top10.std()), 2),
            "min": round(float(top10.min()), 2),
            "max": round(float(top10.max()), 2)
        },
        {
            "group": "Rank 11+",
            "count": len(rest),
            "mean": round(float(rest.mean()), 2),
            "median": round(float(rest.median()), 2),
            "std_dev": round(float(rest.std()), 2),
            "min": round(float(rest.min()), 2),
            "max": round(float(rest.max()), 2)
        }
    ])
    return summary, top10, rest


def compare_score_dispersion_across_years(df, category="Overall"):
    """
    Q6.2: Are NIRF scores more dispersed in one year than another?
    Computes Variance, Standard Deviation, and IQR for each year.
    """
    subset = filter_data(df, category=category)
    dispersion = subset.groupby("year")["score"].agg(
        variance=lambda s: s.var(),
        std_dev="std",
        iqr=lambda s: s.quantile(0.75) - s.quantile(0.25),
        count="count"
    ).reset_index()
    return dispersion.round(2)


def get_parameter_variability(df, year=2024, category="Overall"):
    """
    Q6.3: Which NIRF parameter exhibits the greatest variability across institutions?
    Measures Coefficient of Variation (CV = StdDev / Mean * 100) and Standard Deviation.
    """
    params = ["tlr", "rpc", "go", "oi", "perception"]
    subset = filter_data(df, year=year, category=category)
    records = []
    
    for p in params:
        series = subset[p].dropna()
        if len(series) > 1:
            mean_val = series.mean()
            std_val = series.std()
            cv = (std_val / mean_val) * 100 if mean_val > 0 else 0.0
            records.append({
                "parameter": p.upper(),
                "mean": round(float(mean_val), 2),
                "std_dev": round(float(std_val), 2),
                "coefficient_of_variation_pct": round(float(cv), 2)
            })
    
    res = pd.DataFrame(records).sort_values(by="coefficient_of_variation_pct", ascending=False)
    return res.reset_index(drop=True)


def get_median_iqr_trend(df, category="Overall"):
    """
    Q6.4: How do the median and interquartile range of scores change over time?
    """
    subset = filter_data(df, category=category)
    trend = subset.groupby("year")["score"].agg(
        median="median",
        q25=lambda s: s.quantile(0.25),
        q75=lambda s: s.quantile(0.75),
    ).reset_index()
    trend["iqr"] = trend["q75"] - trend["q25"]
    return trend.round(2)


def get_state_score_distribution(df, year=2024, category="Overall", min_institutions=3):
    """
    Q6.5: How does the score distribution differ across states?
    Returns records for states that have at least min_institutions.
    """
    subset = filter_data(df, year=year, category=category)
    state_counts = subset["state"].value_counts()
    valid_states = state_counts[state_counts >= min_institutions].index
    filtered = subset[subset["state"].isin(valid_states)]
    return filtered[["name", "state", "score", "rank"]]


# ==============================================================================
# 7. RANKING TRANSITIONS AND INSTITUTIONAL MOBILITY
# ==============================================================================

def get_band_to_top50_transitions(df, category="Overall", year1=2023, year2=2024):
    """
    Q7.1: How many institutions moved from the 51–100 band into the top 50 between two selected years?
    """
    subset = filter_data(df, category=category)
    y1_data = subset[subset["year"] == year1][["name", "rank", "score"]].rename(
        columns={"rank": "rank_year1", "score": "score_year1"}
    )
    y2_data = subset[subset["year"] == year2][["name", "rank", "score"]].rename(
        columns={"rank": "rank_year2", "score": "score_year2"}
    )
    
    merged = pd.merge(y1_data, y2_data, on="name")
    # Condition: in year1 was between 51 and 100, in year2 is <= 50
    condition = (merged["rank_year1"] > 50) & (merged["rank_year1"] <= 100) & (merged["rank_year2"] <= 50)
    transitions = merged[condition].sort_values("rank_year2")
    return transitions.reset_index(drop=True)


def get_top10_entries_and_exits(df, category="Overall", year1=2023, year2=2024):
    """
    Q7.2: Which institutions entered or exited the top 10 between consecutive years?
    """
    subset = filter_data(df, category=category)
    top10_y1 = set(subset[(subset["year"] == year1) & (subset["rank"] <= 10)]["name"])
    top10_y2 = set(subset[(subset["year"] == year2) & (subset["rank"] <= 10)]["name"])
    
    entries = sorted(list(top10_y2 - top10_y1))
    exits = sorted(list(top10_y1 - top10_y2))
    
    return {"entries": entries, "exits": exits, "retained": sorted(list(top10_y1.intersection(top10_y2)))}


def get_percentage_retained_in_band(df, category="Overall", year1=2023, year2=2024):
    """
    Q7.3: What percentage of institutions remained in the same rank band from one year to the next?
    Bands: Top 10 (1-10), Mid Tier (11-50), Lower Tier (51-100).
    """
    subset = filter_data(df, category=category)
    y1 = subset[subset["year"] == year1][["name", "rank"]].rename(columns={"rank": "r1"})
    y2 = subset[subset["year"] == year2][["name", "rank"]].rename(columns={"rank": "r2"})
    
    merged = pd.merge(y1, y2, on="name")
    
    def get_band(r):
        if r <= 10:
            return "Top 10"
        elif r <= 50:
            return "11-50"
        elif r <= 100:
            return "51-100"
        else:
            return "101+"

    merged["band_y1"] = merged["r1"].apply(get_band)
    merged["band_y2"] = merged["r2"].apply(get_band)
    
    band_summary = []
    for band in ["Top 10", "11-50", "51-100"]:
        in_band_y1 = merged[merged["band_y1"] == band]
        if len(in_band_y1) > 0:
            retained = in_band_y1[in_band_y1["band_y2"] == band]
            pct = (len(retained) / len(in_band_y1)) * 100.0
            band_summary.append({
                "band": band,
                "institutions_start": len(in_band_y1),
                "retained_count": len(retained),
                "retention_percentage": round(pct, 2)
            })
    
    overall_retained = merged[merged["band_y1"] == merged["band_y2"]]
    overall_pct = (len(overall_retained) / len(merged)) * 100 if len(merged) > 0 else 0
    return pd.DataFrame(band_summary), round(overall_pct, 2)


def get_largest_upward_downward_shifts(df, category="Overall", year1=2023, year2=2024, limit=10):
    """
    Q7.4: Which institutions experienced the largest upward and downward rank movements?
    """
    subset = filter_data(df, category=category)
    y1 = subset[subset["year"] == year1][["name", "rank", "score"]].rename(columns={"rank": "rank_prev", "score": "score_prev"})
    y2 = subset[subset["year"] == year2][["name", "rank", "score"]].rename(columns={"rank": "rank_curr", "score": "score_curr"})
    
    merged = pd.merge(y1, y2, on="name")
    # Shift = rank_prev - rank_curr (positive = upward climb, negative = downward drop)
    merged["rank_shift"] = merged["rank_prev"] - merged["rank_curr"]
    
    upward = merged.sort_values(by="rank_shift", ascending=False).head(limit)
    downward = merged.sort_values(by="rank_shift", ascending=True).head(limit)
    return upward.reset_index(drop=True), downward.reset_index(drop=True)


def get_mobility_summary(df, category="Overall", year1=2023, year2=2024):
    """
    Q7.5: How many institutions moved up, moved down, or retained their positions each year?
    """
    subset = filter_data(df, category=category)
    y1 = subset[subset["year"] == year1][["name", "rank"]].rename(columns={"rank": "r1"})
    y2 = subset[subset["year"] == year2][["name", "rank"]].rename(columns={"rank": "r2"})
    
    merged = pd.merge(y1, y2, on="name")
    moved_up = len(merged[merged["r2"] < merged["r1"]])
    moved_down = len(merged[merged["r2"] > merged["r1"]])
    retained = len(merged[merged["r2"] == merged["r1"]])
    
    summary = {
        "moved_up": moved_up,
        "moved_down": moved_down,
        "retained_position": retained,
        "total_compared": len(merged)
    }
    return summary


# ==============================================================================
# 8. OUTLIER DETECTION AND PERFORMANCE GAPS
# ==============================================================================

def get_research_score_outliers(df, year=2024, category="Overall", threshold_std=1.5):
    """
    Q8.1: Which institutions have unusually high research scores relative to their overall scores?
    Fits a linear regression (score -> rpc) and flags institutions with high positive residuals (> threshold * std).
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["score", "rpc"]).copy()
    if len(subset) < 5:
        return pd.DataFrame()
    
    # Linear fit: predicted_rpc = m * score + c
    m, c = np.polyfit(subset["score"], subset["rpc"], 1)
    subset["expected_rpc"] = m * subset["score"] + c
    subset["residual"] = subset["rpc"] - subset["expected_rpc"]
    
    std_res = subset["residual"].std()
    outliers = subset[subset["residual"] > threshold_std * std_res].sort_values(by="residual", ascending=False)
    cols = ["name", "rank", "score", "rpc", "expected_rpc", "residual"]
    return outliers[cols].round(2).reset_index(drop=True)


def get_research_teaching_gap_outliers(df, year=2024, category="Overall", limit=10):
    """
    Q8.2: Which institutions perform substantially better in research than in teaching?
    Gap = RPC - TLR.
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=["rpc", "tlr"]).copy()
    subset["research_teaching_gap"] = subset["rpc"] - subset["tlr"]
    result = subset.sort_values(by="research_teaching_gap", ascending=False).head(limit)
    cols = ["name", "rank", "score", "rpc", "tlr", "research_teaching_gap"]
    return result[cols].round(2).reset_index(drop=True)


def get_score_change_outliers(df, category="Overall", year1=2023, year2=2024, z_threshold=2.0):
    """
    Q8.3: Which institutions experienced an unusually large year-to-year score change?
    Computes delta_score = score_y2 - score_y1 and flags z-score > z_threshold.
    """
    subset = filter_data(df, category=category)
    y1 = subset[subset["year"] == year1][["name", "score"]].rename(columns={"score": "s1"})
    y2 = subset[subset["year"] == year2][["name", "score"]].rename(columns={"score": "s2"})
    
    merged = pd.merge(y1, y2, on="name").dropna(subset=["s1", "s2"])
    merged["score_change"] = merged["s2"] - merged["s1"]
    
    std_change = merged["score_change"].std()
    mean_change = merged["score_change"].mean()
    
    if std_change == 0 or pd.isna(std_change):
        return pd.DataFrame()
        
    merged["z_score"] = (merged["score_change"] - mean_change) / std_change
    outliers = merged[merged["z_score"].abs() >= z_threshold].sort_values(by="score_change", ascending=False)
    return outliers.round(2).reset_index(drop=True)


def get_strong_param_poor_rank(df, year=2024, category="Overall", param="rpc", param_percentile=75, rank_min=50):
    """
    Q8.4: Which institutions have a strong parameter score but a relatively poor overall rank?
    Strong parameter = value >= param_percentile.
    Poor rank = rank > rank_min.
    """
    subset = filter_data(df, year=year, category=category).dropna(subset=[param, "rank"]).copy()
    cutoff = subset[param].quantile(param_percentile / 100.0)
    
    matches = subset[(subset[param] >= cutoff) & (subset["rank"] > rank_min)]
    cols = ["name", "rank", "score", param, "state"]
    return matches[cols].sort_values(by=param, ascending=False).reset_index(drop=True)


def get_rank_volatility(df, category="Overall", min_years=4, limit=10):
    """
    Q8.5: Which institutions have unusually high ranking volatility compared with similar institutions?
    Volatility = Standard Deviation of rank across available years.
    """
    subset = filter_data(df, category=category).dropna(subset=["rank"])
    # Group by institution and calculate standard deviation and count
    volatility = subset.groupby("name")["rank"].agg(
        rank_std_dev="std",
        min_rank="min",
        max_rank="max",
        years_counted="count"
    ).reset_index()
    
    # Filter for institutions appearing at least min_years
    filtered_vol = volatility[volatility["years_counted"] >= min_years]
    result = filtered_vol.sort_values(by="rank_std_dev", ascending=False).head(limit)
    return result.round(2).reset_index(drop=True)
