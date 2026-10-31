"""
NIRF Analytics - FastAPI Backend
==================================
Exposes all Python analysis functions as REST API endpoints.
The React frontend calls these endpoints to get data and charts.

Run with:
    uvicorn api.main:app --reload --port 8000
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from typing import Optional, List

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path so we can import src modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import src.analysis as analysis
import src.visualizations as viz
from src.data_loader import load_master_data
from src.query_engine import parse_query, execute_query

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="NIRF Ranking Analytics API",
    description="REST API for NIRF Ranking data (2017–2025) across all categories.",
    version="1.0.0",
)

# Allow requests from the React dev server (localhost:5173) and any origin in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load master data once at startup ─────────────────────────────────────────
print("Loading master dataset…")
df_master = load_master_data()
print(f"Loaded {len(df_master):,} records.")

# ── Helpers ───────────────────────────────────────────────────────────────────

def df_to_json(df: pd.DataFrame) -> list:
    """Convert a DataFrame to a list of dicts, handling NaN / numpy types."""
    return json.loads(df.to_json(orient="records"))


def safe_float(val):
    """Convert numpy/float NaN to None for JSON serialisation."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    return float(val)


# ── Meta / overview endpoints ─────────────────────────────────────────────────

@app.get("/api/meta", tags=["Meta"])
def get_meta():
    """Returns global dataset metadata: categories, years, states, KPI counts."""
    if df_master.empty:
        raise HTTPException(status_code=503, detail="Master dataset not loaded.")
    return {
        "total_records": len(df_master),
        "total_institutions": int(df_master["name"].nunique()),
        "total_states": int(df_master["state"].nunique()),
        "year_range": [int(df_master["year"].min()), int(df_master["year"].max())],
        "categories": sorted(df_master["category"].unique().tolist()),
        "years": sorted(df_master["year"].unique().tolist()),
        "states": sorted(df_master["state"].unique().tolist()),
        "total_categories": int(df_master["category"].nunique()),
    }


@app.get("/api/top-institutions", tags=["Overview"])
def get_top_institutions(
    year: int = Query(2024),
    category: str = Query("Overall"),
    limit: int = Query(10),
):
    """Top N institutions for a given year and category."""
    filtered = analysis.filter_data(df_master, year=year, category=category)
    top = filtered.sort_values("rank").head(limit)
    cols = ["rank", "name", "score", "city", "state", "tlr", "rpc", "go", "oi", "perception"]
    existing = [c for c in cols if c in top.columns]
    return df_to_json(top[existing].reset_index(drop=True))


@app.get("/api/institutions", tags=["Overview"])
def list_institutions(category: str = Query("Overall")):
    """Return all unique institution names for a category (used in search dropdowns)."""
    subset = analysis.filter_data(df_master, category=category)
    names = sorted(subset["name"].dropna().unique().tolist())
    return {"institutions": names}


# ── Time-series endpoints ─────────────────────────────────────────────────────

@app.get("/api/trend/institution", tags=["Time-Series"])
def institution_rank_trend(
    name: str = Query(..., description="Institution name (partial match)"),
    category: str = Query("Overall"),
):
    """Q1.1 – Rank trajectory of a specific institution over years."""
    result = analysis.get_institution_rank_trend(df_master, name, category=category)
    return df_to_json(result)


@app.get("/api/trend/average-score", tags=["Time-Series"])
def average_score_trend(category: str = Query("Overall")):
    """Q1.4 – Average NIRF score trend per year."""
    result = analysis.get_average_score_trend(df_master, category=category)
    return df_to_json(result)


@app.get("/api/trend/improvements", tags=["Time-Series"])
def biggest_improvements(
    category: str = Query("Overall"),
    start_year: int = Query(2017),
    end_year: int = Query(2024),
    limit: int = Query(10),
):
    """Q1.2 – Institutions with greatest rank improvements."""
    result = analysis.get_biggest_rank_improvements(
        df_master, category=category, start_year=start_year, end_year=end_year, limit=limit
    )
    return df_to_json(result)


@app.get("/api/trend/declines", tags=["Time-Series"])
def biggest_declines(
    category: str = Query("Overall"),
    start_year: int = Query(2017),
    end_year: int = Query(2024),
    limit: int = Query(10),
):
    """Q1.3 – Institutions with biggest rank declines."""
    result = analysis.get_biggest_rank_declines(
        df_master, category=category, start_year=start_year, end_year=end_year, limit=limit
    )
    return df_to_json(result)


@app.get("/api/trend/consistent-top", tags=["Time-Series"])
def consistent_top(
    category: str = Query("Overall"),
    top_n: int = Query(10),
    min_years: int = Query(5),
):
    """Q1.5 – Institutions consistently ranked in top N for multiple years."""
    result = analysis.get_consistent_top_institutions(
        df_master, category=category, top_n=top_n, min_years=min_years
    )
    return df_to_json(result)


# ── Geospatial endpoints ──────────────────────────────────────────────────────

@app.get("/api/geo/top-states", tags=["Geospatial"])
def top_states(
    year: int = Query(2024),
    category: str = Query("Overall"),
    top_n: int = Query(100),
    limit: int = Query(15),
):
    """Q2.1 – States with most institutions in top N."""
    result = analysis.get_states_top_institutions(
        df_master, year=year, category=category, top_n=top_n, limit=limit
    )
    return df_to_json(result)


@app.get("/api/geo/distribution-trend", tags=["Geospatial"])
def geo_distribution_trend(
    category: str = "Overall",
    top_n: int = 100,
):
    """Q2.2 – Geographical distribution trend of top-ranked institutions across years (2017–2025)."""
    pivot_df = analysis.get_geo_distribution_trend(df_master, category=category, top_n=top_n)
    fig_json = None
    if not pivot_df.empty:
        fig = viz.plot_geo_distribution_heatmap(pivot_df, category=category, top_n=top_n)
        fig_json = json.loads(fig.to_json()) if fig else None
    
    year_cols = [c for c in pivot_df.columns if c != "state"]
    return {
        "records": df_to_json(pivot_df),
        "figure": fig_json,
        "count": len(pivot_df),
        "years": year_cols,
        "category": category,
        "top_n": top_n,
    }


@app.get("/api/geo/state-growth", tags=["Geospatial"])
def state_growth(
    category: str = Query("Overall"),
    start_year: int = Query(2017),
    end_year: int = Query(2024),
):
    """Q2.3 – States that improved representation in top 100 over time."""
    result = analysis.get_state_representation_growth(
        df_master, category=category, start_year=start_year, end_year=end_year
    )
    return df_to_json(result)


@app.get("/api/geo/compare-states", tags=["Geospatial"])
def compare_states(
    state1: str = Query("Karnataka"),
    state2: str = Query("Tamil Nadu"),
    category: str = Query("Overall"),
    year: int = Query(2024),
):
    """Q2.4 – Side-by-side state comparison."""
    summary_df, raw_df = analysis.compare_two_states(
        df_master, state1=state1, state2=state2, category=category, year=year
    )
    return {"summary": df_to_json(summary_df), "records": df_to_json(raw_df)}


@app.get("/api/geo/newly-appearing", tags=["Geospatial"])
def newly_appearing(
    category: str = Query("Overall"),
    base_year: int = Query(2017),
    recent_year: int = Query(2024),
):
    """Q2.5 – Newly appearing institutions by state."""
    summary_df, raw_df = analysis.get_newly_appearing_institutions_by_state(
        df_master, category=category, base_year=base_year, recent_year=recent_year
    )
    return {"summary": df_to_json(summary_df), "records": df_to_json(raw_df)}


# ── Univariate endpoints ───────────────────────────────────────────────────────

@app.get("/api/univariate/score-distribution", tags=["Univariate"])
def score_distribution(year: int = Query(2024), category: str = Query("Overall")):
    """Q3.1 – Score distribution (list of scores) for histogram."""
    scores = analysis.get_score_distribution(df_master, year=year, category=category)
    return {"scores": scores.tolist()}


@app.get("/api/univariate/rank-distribution", tags=["Univariate"])
def rank_distribution(year: int = 2024, category: str = "Overall"):
    """Q3.2 – Distribution of overall ranks across institutions."""
    subset = analysis.filter_data(df_master, year=year, category=category)
    ranks = subset["rank"].dropna()
    
    bins = [0, 10, 25, 50, 100, 150, 1000]
    labels = ["Rank 1–10 (Top 10)", "Rank 11–25", "Rank 26–50", "Rank 51–100", "Rank 101–150", "Rank 151+"]
    band_series = pd.cut(ranks, bins=bins, labels=labels, right=True)
    band_counts = band_series.value_counts(sort=False).reindex(labels, fill_value=0)
    
    bands = [{"band": band, "count": int(count)} for band, count in band_counts.items() if count > 0 or band in labels[:4]]
    
    fig = viz.plot_rank_distribution(subset, year=year, category=category)
    fig_json = json.loads(fig.to_json()) if fig else None
    
    records = subset[["name", "rank", "score", "state"]].sort_values("rank").dropna(subset=["rank"])
    
    return {
        "records": df_to_json(records),
        "bands": bands,
        "figure": fig_json,
        "total_ranked": len(ranks),
        "year": year,
        "category": category,
    }


@app.get("/api/univariate/summary-stats", tags=["Univariate"])
def summary_stats(year: int = Query(2024), category: str = Query("Overall")):
    """Q3.3 – Mean, median, min, max, std of scores."""
    return analysis.get_score_summary_stats(df_master, year=year, category=category)


@app.get("/api/univariate/quartiles", tags=["Univariate"])
def score_quartiles(year: int = Query(2024), category: str = Query("Overall")):
    """Q3.4 – Score quartile breakdown."""
    result = analysis.get_score_quartiles(df_master, year=year, category=category)
    return df_to_json(result)


@app.get("/api/univariate/spread-by-category", tags=["Univariate"])
def spread_by_category(year: int = Query(2024)):
    """Q3.5 – Score spread comparison across all categories."""
    result = analysis.get_score_spread_by_category(df_master, year=year)
    return df_to_json(result)


# ── Bivariate / Correlation endpoints ────────────────────────────────────────

@app.get("/api/bivariate/rpc-vs-score", tags=["Bivariate"])
def rpc_vs_score(year: int = Query(2024), category: str = Query("Overall")):
    """Q4.1 – RPC vs Overall Score correlation."""
    r, data = analysis.get_rpc_vs_score_correlation(df_master, year=year, category=category)
    return {"r": safe_float(r), "data": df_to_json(data)}


@app.get("/api/bivariate/perception-vs-score", tags=["Bivariate"])
def perception_vs_score(year: int = Query(2024), category: str = Query("Overall")):
    """Q4.2 – Perception vs Overall Score correlation."""
    r, data = analysis.get_perception_vs_score_correlation(df_master, year=year, category=category)
    return {"r": safe_float(r), "data": df_to_json(data)}


@app.get("/api/bivariate/all-parameters", tags=["Bivariate"])
def all_parameters_correlation(year: int = Query(2024), category: str = Query("Overall")):
    """Q4.3 – Correlation of each parameter against overall score."""
    result = analysis.get_all_parameters_correlation(df_master, year=year, category=category)
    return df_to_json(result)


@app.get("/api/bivariate/tlr-vs-rpc", tags=["Bivariate"])
def tlr_vs_rpc(year: int = Query(2024), category: str = Query("Overall")):
    """Q4.4 – TLR vs RPC scatter data."""
    r, data = analysis.get_tlr_vs_rpc_relation(df_master, year=year, category=category)
    return {"r": safe_float(r), "data": df_to_json(data)}


@app.get("/api/bivariate/two-variable", tags=["Bivariate"])
def two_variable_correlation(
    v1: str = Query("rpc"),
    v2: str = Query("score"),
    year: int = Query(2024),
    category: str = Query("Overall"),
):
    """Dynamic 2-variable correlation scatter."""
    result = analysis.get_two_variable_correlation(df_master, v1, v2, year=year, category=category)
    return {
        "r": safe_float(result["r"]),
        "slope": safe_float(result["slope"]),
        "intercept": safe_float(result["intercept"]),
        "data": df_to_json(result["data"]),
    }


@app.get("/api/bivariate/correlation-trend", tags=["Bivariate"])
def correlation_trend(
    param1: str = Query("rpc"),
    param2: str = Query("score"),
    category: str = Query("Overall"),
):
    """Q4.5 – Correlation coefficient evolution over years."""
    result = analysis.get_correlation_trend_over_time(df_master, param1=param1, param2=param2, category=category)
    return df_to_json(result)


# ── Dynamic Explorer endpoints ───────────────────────────────────────────────

class DynamicDataRequest(BaseModel):
    category: Optional[str] = "Overall"
    start_year: Optional[int] = 2017
    end_year: Optional[int] = 2025
    states: Optional[List[str]] = None
    institutions: Optional[List[str]] = None
    top_n: Optional[int] = None


@app.post("/api/dynamic/filter", tags=["Dynamic"])
def dynamic_filter(req: DynamicDataRequest):
    """
    Level 2: Filter master dataset dynamically across multiple years, states, institutions, and top N.
    """
    subset = df_master.copy()
    if req.category and req.category != "All":
        subset = subset[subset["category"] == req.category]
    if req.start_year is not None:
        subset = subset[subset["year"] >= req.start_year]
    if req.end_year is not None:
        subset = subset[subset["year"] <= req.end_year]
    if req.states and len(req.states) > 0:
        subset = subset[subset["state"].isin(req.states)]
    if req.institutions and len(req.institutions) > 0:
        subset = subset[subset["name"].isin(req.institutions)]
    if req.top_n and req.top_n > 0:
        subset = subset[subset["rank"].notna() & (subset["rank"] <= req.top_n)]

    subset = subset.sort_values(by=["year", "rank"], ascending=[False, True])

    # Category base for available filter options
    cat_df = df_master[df_master["category"] == req.category] if req.category and req.category != "All" else df_master
    if req.start_year is not None and req.end_year is not None:
        cat_df = cat_df[(cat_df["year"] >= req.start_year) & (cat_df["year"] <= req.end_year)]

    available_states = sorted([s for s in cat_df["state"].dropna().unique().tolist() if s])
    
    # If states are filtered, available institutions should be from those states
    inst_df = cat_df[cat_df["state"].isin(req.states)] if req.states and len(req.states) > 0 else cat_df
    available_institutions = sorted([n for n in inst_df["name"].dropna().unique().tolist() if n])

    cols = ["name", "rank", "score", "tlr", "rpc", "go", "oi", "perception", "city", "state", "year", "category"]
    available_cols = [c for c in cols if c in subset.columns]
    recs = df_to_json(subset[available_cols])
    for r in recs:
        r["institution"] = r.get("name", "")

    return {
        "records": recs,
        "data": recs,
        "total_count": len(subset),
        "total": len(subset),
        "available_states": available_states,
        "available_institutions": available_institutions,
        "category": req.category,
        "start_year": req.start_year,
        "end_year": req.end_year,
    }


# ── Multivariate endpoints ────────────────────────────────────────────────────

@app.get("/api/multivariate/top-profiles", tags=["Multivariate"])
def top_profiles(year: int = Query(2024), category: str = Query("Overall"), top_n: int = Query(5)):
    """Q5.1 – Top N institution multivariate parameter profiles (for radar chart)."""
    result = analysis.get_top_n_multivariate_profile(df_master, year=year, category=category, top_n=top_n)
    return df_to_json(result)


@app.get("/api/multivariate/high-research-low-teaching", tags=["Multivariate"])
def high_research_low_teaching(year: int = Query(2024), category: str = Query("Overall")):
    """Q5.2 – Institutions with high RPC but low TLR."""
    result = analysis.get_high_research_low_teaching(df_master, year=year, category=category)
    return df_to_json(result)


@app.get("/api/multivariate/high-teaching-low-perception", tags=["Multivariate"])
def high_teaching_low_perception(
    year: int = 2024,
    category: str = "Overall",
    percentile_high: float = 75.0,
    percentile_low: float = 50.0,
):
    """Q5.3 – Institutions with high TLR (teaching) but relatively low perception."""
    subset = analysis.filter_data(df_master, year=year, category=category).dropna(subset=["tlr", "perception"])
    if subset.empty:
        tlr_threshold = 0.0
        pr_threshold = 0.0
        matches = pd.DataFrame()
    else:
        tlr_threshold = float(subset["tlr"].quantile(percentile_high / 100.0))
        pr_threshold = float(subset["perception"].quantile(percentile_low / 100.0))
        matches = analysis.get_high_teaching_low_perception(
            df_master, year=year, category=category, percentile_high=percentile_high, percentile_low=percentile_low
        )
    
    fig_json = None
    if not subset.empty:
        fig = viz.plot_high_teaching_low_perception(
            subset, tlr_threshold=tlr_threshold, pr_threshold=pr_threshold, year=year, category=category
        )
        fig_json = json.loads(fig.to_json())
        
    return {
        "records": df_to_json(matches),
        "figure": fig_json,
        "count": len(matches),
        "tlr_threshold": round(tlr_threshold, 2),
        "perception_threshold": round(pr_threshold, 2),
        "year": year,
        "category": category,
    }


@app.get("/api/multivariate/improved-score-declining-params", tags=["Multivariate"])
def improved_score_declining_params(
    category: str = "Overall",
    start_year: int = 2017,
    end_year: int = 2024,
):
    """Q5.4 – Institutions improving overall score despite declining individual parameters."""
    available_years = sorted(df_master["year"].unique().tolist())
    if start_year not in available_years or end_year not in available_years:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid year range ({start_year}, {end_year}). Available years are {available_years[0]} to {available_years[-1]}.",
        )
    if start_year >= end_year:
        raise HTTPException(
            status_code=400,
            detail="Start year must be earlier than end year.",
        )
    
    res_df = analysis.get_improved_score_with_declining_parameters(
        df_master, category=category, start_year=start_year, end_year=end_year
    )
    fig_json = None
    if not res_df.empty:
        fig = viz.plot_improved_score_with_declining_parameters(
            res_df, category=category, start_year=start_year, end_year=end_year
        )
        fig_json = json.loads(fig.to_json()) if fig else None
        
    return {
        "records": df_to_json(res_df),
        "figure": fig_json,
        "count": len(res_df),
        "start_year": start_year,
        "end_year": end_year,
        "category": category,
    }


@app.get("/api/multivariate/strongest-weakest-gap", tags=["Multivariate"])
def strongest_weakest_gap(year: int = Query(2024), category: str = Query("Overall")):
    """Q5.5 – Largest gap between an institution's strongest and weakest parameter."""
    result = analysis.get_strongest_weakest_parameter_gap(df_master, year=year, category=category)
    return df_to_json(result)


# ── Statistical comparison endpoints ─────────────────────────────────────────

@app.get("/api/stats/top10-vs-rest", tags=["Statistics"])
def top10_vs_rest(year: int = Query(2024), category: str = Query("Overall")):
    """Q6.1 – Summary stats comparing top 10 vs remaining institutions."""
    summary, top10, rest = analysis.compare_top10_vs_rest(df_master, year=year, category=category)
    return {
        "summary": df_to_json(summary),
        "top10_scores": top10.tolist() if hasattr(top10, "tolist") else list(top10),
        "rest_scores": rest.tolist() if hasattr(rest, "tolist") else list(rest),
    }


@app.get("/api/stats/dispersion", tags=["Statistics"])
def score_dispersion(category: str = Query("Overall")):
    """Q6.2 – Score dispersion (std, IQR) across years."""
    result = analysis.compare_score_dispersion_across_years(df_master, category=category)
    return df_to_json(result)


@app.get("/api/stats/parameter-variability", tags=["Statistics"])
def parameter_variability(year: int = Query(2024), category: str = Query("Overall")):
    """Q6.3 – Coefficient of variation for each NIRF parameter."""
    result = analysis.get_parameter_variability(df_master, year=year, category=category)
    return df_to_json(result)


@app.get("/api/stats/median-iqr-trend", tags=["Statistics"])
def median_iqr_trend(category: str = Query("Overall")):
    """Q6.4 – Median and IQR evolution over years."""
    result = analysis.get_median_iqr_trend(df_master, category=category)
    return df_to_json(result)


@app.get("/api/stats/state-score-distribution", tags=["Statistics"])
def state_score_distribution(
    year: int = Query(2024),
    category: str = Query("Overall"),
    min_institutions: int = Query(3),
):
    """Q6.5 – State-wise score distribution box plot."""
    filtered_df = analysis.get_state_score_distribution(
        df_master, year=year, category=category, min_institutions=min_institutions
    )
    fig_json = None
    if not filtered_df.empty:
        fig = viz.plot_state_score_box(filtered_df)
        fig_json = json.loads(fig.to_json())
    return {
        "records": df_to_json(filtered_df),
        "figure": fig_json,
        "count": len(filtered_df),
        "states_count": int(filtered_df["state"].nunique()) if not filtered_df.empty else 0,
        "year": year,
        "category": category,
        "min_institutions": min_institutions,
    }


# ── Ranking Transitions endpoints ─────────────────────────────────────────────

@app.get("/api/transitions/band-to-top50", tags=["Transitions"])
def band_to_top50(
    category: str = Query("Overall"),
    year1: int = Query(2023),
    year2: int = Query(2024),
):
    """Q7.1 – Institutions moving from 51–100 band into the top 50 between two selected years."""
    available_years = sorted(df_master["year"].unique().tolist())
    if year1 not in available_years or year2 not in available_years:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid year selection ({year1}, {year2}). Available years are {available_years[0]} to {available_years[-1]}.",
        )
    if year1 == year2:
        raise HTTPException(status_code=400, detail="Base year (year1) and comparison year (year2) must be different.")

    trans_df = analysis.get_band_to_top50_transitions(
        df_master, category=category, year1=year1, year2=year2
    )
    fig_json = None
    if not trans_df.empty:
        fig = viz.plot_band_transitions_scatter(trans_df, year1=year1, year2=year2)
        fig_json = json.loads(fig.to_json())
    return {
        "records": df_to_json(trans_df),
        "figure": fig_json,
        "transition_count": len(trans_df),
        "year1": year1,
        "year2": year2,
        "category": category,
    }

@app.get("/api/transitions/top10-entries-exits", tags=["Transitions"])
def top10_entries_exits(
    category: str = Query("Overall"),
    year1: int = Query(2023),
    year2: int = Query(2024),
):
    """Q7.2 – Institutions that entered/exited the top 10."""
    result = analysis.get_top10_entries_and_exits(df_master, category=category, year1=year1, year2=year2)
    return result


@app.get("/api/transitions/band-retention", tags=["Transitions"])
def band_retention(
    category: str = Query("Overall"),
    year1: int = Query(2023),
    year2: int = Query(2024),
):
    """Q7.3 – Percentage of institutions that stayed in the same rank band."""
    band_df, overall_pct = analysis.get_percentage_retained_in_band(
        df_master, category=category, year1=year1, year2=year2
    )
    return {"overall_pct": safe_float(overall_pct), "bands": df_to_json(band_df)}


@app.get("/api/transitions/largest-shifts", tags=["Transitions"])
def largest_shifts(
    category: str = Query("Overall"),
    year1: int = Query(2023),
    year2: int = Query(2024),
):
    """Q7.4 – Largest upward and downward rank movements."""
    up, down = analysis.get_largest_upward_downward_shifts(
        df_master, category=category, year1=year1, year2=year2
    )
    return {"upward": df_to_json(up), "downward": df_to_json(down)}


@app.get("/api/transitions/mobility-summary", tags=["Transitions"])
def mobility_summary(
    category: str = Query("Overall"),
    year1: int = Query(2023),
    year2: int = Query(2024),
):
    """Q7.5 – Count of institutions that moved up, down, or stayed."""
    return analysis.get_mobility_summary(df_master, category=category, year1=year1, year2=year2)


# ── Outlier endpoints ─────────────────────────────────────────────────────────

@app.get("/api/outliers/research-outliers", tags=["Outliers"])
def research_outliers(year: int = Query(2024), category: str = Query("Overall")):
    """Q8.1 – Institutions with unusually high research scores relative to overall."""
    result = analysis.get_research_score_outliers(df_master, year=year, category=category)
    return df_to_json(result)


@app.get("/api/outliers/rank-volatility", tags=["Outliers"])
def rank_volatility(category: str = Query("Overall"), min_years: int = Query(4)):
    """Q8.5 – Institutions with highest rank volatility (std dev of rank)."""
    result = analysis.get_rank_volatility(df_master, category=category, min_years=min_years)
    return df_to_json(result)


@app.get("/api/outliers/score-change", tags=["Outliers"])
def score_change_outliers(
    category: str = Query("Overall"),
    year1: int = Query(2023),
    year2: int = Query(2024),
):
    """Q8.3 – Unusually large year-to-year score changes (Z-score method)."""
    result = analysis.get_score_change_outliers(df_master, category=category, year1=year1, year2=year2)
    return df_to_json(result)


@app.get("/api/outliers/research-teaching-gap", tags=["Outliers"])
def research_teaching_gap_outliers(
    year: int = 2024,
    category: str = "Overall",
    limit: int = 15,
):
    """Q8.2 – Institutions performing substantially better in research than teaching."""
    gap_df = analysis.get_research_teaching_gap_outliers(
        df_master, year=year, category=category, limit=limit
    )
    fig_json = None
    if not gap_df.empty:
        fig = viz.plot_research_teaching_gap(gap_df, year=year, category=category, top_n=limit)
        fig_json = json.loads(fig.to_json())
        
    return {
        "records": df_to_json(gap_df),
        "figure": fig_json,
        "count": len(gap_df),
        "year": year,
        "category": category,
    }


@app.get("/api/outliers/strong-param-poor-rank", tags=["Outliers"])
def strong_param_poor_rank(
    year: int = 2024,
    category: str = "Overall",
    param: str = "rpc",
    param_percentile: float = 75.0,
    rank_min: int = 50,
):
    """Q8.4 – Institutions with a strong parameter score but a relatively poor overall rank."""
    p = param.lower().strip()
    valid_params = ["rpc", "tlr", "go", "oi", "perception", "score"]
    if p not in valid_params:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameter '{param}'. Must be one of: {', '.join(valid_params)}."
        )
    
    subset = analysis.filter_data(df_master, year=year, category=category).dropna(subset=[p, "rank"])
    param_threshold = float(subset[p].quantile(param_percentile / 100.0)) if not subset.empty else 0.0
    
    matches = analysis.get_strong_param_poor_rank(
        df_master, year=year, category=category, param=p, param_percentile=param_percentile, rank_min=rank_min
    )
    
    fig_json = None
    if not subset.empty:
        fig = viz.plot_strong_param_poor_rank(
            subset, param=p, param_threshold=param_threshold, rank_cutoff=rank_min, year=year, category=category
        )
        fig_json = json.loads(fig.to_json())
        
    return {
        "records": df_to_json(matches),
        "figure": fig_json,
        "count": len(matches),
        "param": p,
        "param_threshold": round(param_threshold, 2),
        "rank_cutoff": rank_min,
        "year": year,
        "category": category,
    }


# ── Natural Language Query endpoint ───────────────────────────────────────────

class NLQueryRequest(BaseModel):
    question: str
    category: Optional[str] = None
    year: Optional[int] = None


@app.post("/api/query/natural-language", tags=["NL Query"])
def natural_language_query(req: NLQueryRequest):
    """
    Level 3 – Natural language query engine.
    Accepts a plain-English question and returns a textual summary + structured data.
    Charts are rendered on the frontend using the returned data.
    """
    known_institutions = df_master["name"].unique().tolist()
    max_year = int(df_master["year"].max()) if not df_master.empty else 2025
    plan = parse_query(
        req.question,
        known_institutions=known_institutions,
        default_category=req.category,
        default_year=req.year,
        max_year=max_year,
    )
    result = execute_query(plan, df_master)

    # Plotly figure is serialised to JSON dict for the frontend
    fig_json = None
    if result.get("figure") is not None:
        fig_json = result["figure"].to_json()

    return {
        "query_plan": plan,
        "summary_text": result.get("summary_text", ""),
        "data": df_to_json(result["data"]) if not result["data"].empty else [],
        "figure_json": fig_json,
        "intent": result.get("intent", ""),
    }


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {"message": "NIRF Analytics API is running. Visit /docs for the interactive API explorer."}
