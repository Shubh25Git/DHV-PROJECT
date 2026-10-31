"""
Unit Tests for FastAPI Backend Endpoints
=======================================
Verifies that all endpoint functions defined in api/main.py execute correctly,
return valid schemas and serializable data, and handle edge cases gracefully.
"""

import pytest
import api.main as api


def test_meta_endpoint():
    meta = api.get_meta()
    assert isinstance(meta, dict)
    assert meta["total_records"] > 0
    assert "Overall" in meta["categories"]
    assert 2024 in meta["years"]
    assert len(meta["states"]) > 0


def test_top_institutions_endpoint():
    top = api.get_top_institutions(year=2024, category="Overall", limit=5)
    assert isinstance(top, list)
    assert len(top) == 5
    assert top[0]["rank"] == 1.0
    assert "name" in top[0]
    assert "score" in top[0]


def test_institution_rank_trend():
    trend = api.institution_rank_trend(name="Indian Institute of Technology Madras", category="Overall")
    assert isinstance(trend, list)
    assert len(trend) > 0
    assert all("year" in r and "rank" in r for r in trend)


def test_average_score_trend():
    avg = api.average_score_trend(category="Overall")
    assert isinstance(avg, list)
    assert len(avg) > 0
    assert all("year" in r and "mean_score" in r and "median_score" in r for r in avg)


def test_geospatial_top_states():
    states = api.top_states(year=2024, category="Overall", top_n=100, limit=10)
    assert isinstance(states, list)
    assert len(states) > 0
    assert "state" in states[0]
    assert "institution_count" in states[0]


def test_univariate_score_distribution():
    dist = api.score_distribution(year=2024, category="Overall")
    assert isinstance(dist, dict)
    assert "scores" in dist
    assert len(dist["scores"]) > 0


def test_bivariate_rpc_vs_score():
    res = api.rpc_vs_score(year=2024, category="Overall")
    assert isinstance(res, dict)
    assert "r" in res
    assert res["r"] is not None
    assert len(res["data"]) > 0


def test_multivariate_top_profiles():
    profiles = api.top_profiles(year=2024, category="Overall", top_n=5)
    assert isinstance(profiles, list)
    assert len(profiles) == 5
    assert "tlr" in profiles[0]
    assert "rpc" in profiles[0]


def test_statistics_top10_vs_rest():
    stats = api.top10_vs_rest(year=2024, category="Overall")
    assert isinstance(stats, dict)
    assert "summary" in stats
    assert "top10_scores" in stats
    assert "rest_scores" in stats
    assert len(stats["summary"]) == 2


def test_transitions_top10():
    trans = api.top10_entries_exits(category="Overall", year1=2023, year2=2024)
    assert isinstance(trans, dict)
    assert "entries" in trans
    assert "exits" in trans


def test_outliers_research():
    out = api.research_outliers(year=2024, category="Overall")
    assert isinstance(out, list)
    assert len(out) > 0
    assert "residual" in out[0]


def test_natural_language_query_success():
    req = api.NLQueryRequest(question="Which institution ranked first in Engineering in 2024?")
    res = api.natural_language_query(req)
    assert isinstance(res, dict)
    assert "query_plan" in res
    assert "summary_text" in res
    assert "data" in res
    assert "figure_json" in res
    assert len(res["data"]) > 0
    assert res["query_plan"]["category"] == "Engineering"
    assert res["query_plan"]["primary_year"] == 2024


def test_natural_language_query_institution_trend():
    req = api.NLQueryRequest(question="Show the ranking trend of IIT Madras over time")
    res = api.natural_language_query(req)
    assert isinstance(res, dict)
    assert res["intent"] == "institution_trend"
    assert res["figure_json"] is not None
    assert len(res["data"]) > 0


# ── Regression Tests for Natural Language Query Fixes ────────────────────────

def test_regression_current_rank_iit_indore():
    """
    Regression test: 'What is the current rank of iit indore?'
    Must retrieve IIT Indore data (never IIT Madras), recognize 'current' as latest year (2025),
    and classify intent as 'institution_rank'.
    """
    req = api.NLQueryRequest(question="What is the current rank of iit indore?", category="Engineering")
    res = api.natural_language_query(req)
    assert res["intent"] == "institution_rank"
    assert res["query_plan"]["primary_year"] == 2025
    assert res["query_plan"]["category"] == "Engineering"
    assert len(res["data"]) == 1
    assert res["data"][0]["name"] == "Indian Institute of Technology Indore"
    assert res["data"][0]["rank"] == 12.0
    assert "Indian Institute of Technology Indore" in res["summary_text"]
    assert "Indian Institute of Technology Madras" not in res["summary_text"]

    # Also test with default (Overall)
    req_default = api.NLQueryRequest(question="What is the current rank of iit indore?")
    res_default = api.natural_language_query(req_default)
    assert res_default["intent"] == "institution_rank"
    assert res_default["query_plan"]["primary_year"] == 2025
    assert res_default["data"][0]["name"] == "Indian Institute of Technology Indore"
    assert res_default["data"][0]["rank"] == 27.0
    assert "Indian Institute of Technology Madras" not in res_default["summary_text"]


def test_regression_rank_iit_madras_engineering_2024():
    """
    Regression test: 'What is the rank of IIT Madras in Engineering in 2024?'
    Must explicitly extract year=2024, category=Engineering, and retrieve IIT Madras Rank 1.
    """
    req = api.NLQueryRequest(question="What is the rank of IIT Madras in Engineering in 2024?")
    res = api.natural_language_query(req)
    assert res["intent"] == "institution_rank"
    assert res["query_plan"]["primary_year"] == 2024
    assert res["query_plan"]["category"] == "Engineering"
    assert len(res["data"]) == 1
    assert res["data"][0]["name"] == "Indian Institute of Technology Madras"
    assert res["data"][0]["rank"] == 1.0
    assert "Indian Institute of Technology Madras" in res["summary_text"]


def test_regression_non_existent_institution():
    """
    Regression test: Query for an institution that does not exist in dataset.
    Must return a clear 'institution not found' message and NOT substitute another institution.
    """
    req = api.NLQueryRequest(question="What is the current rank of Hogwarts School?")
    res = api.natural_language_query(req)
    assert res["intent"] == "institution_rank"
    assert res["data"] == []
    assert res["figure_json"] is None
    assert "not found" in res["summary_text"].lower()
    assert "Hogwarts School" in res["summary_text"]
    assert "Madras" not in res["summary_text"]


def test_regression_query_explicit_year_and_category():
    """
    Regression test: Explicit year and category parsing.
    """
    req = api.NLQueryRequest(question="Top 5 institutions in Engineering in 2023")
    res = api.natural_language_query(req)
    assert res["query_plan"]["primary_year"] == 2023
    assert res["query_plan"]["category"] == "Engineering"
    assert len(res["data"]) > 0
    assert all(r["name"] is not None for r in res["data"])


def test_regression_compare_iit_indore_and_madras_2025_engineering():
    """
    Regression test: 'Compare IIT Indore and IIT Madras in Engineering in 2025.'
    Must classify as 'institution_comparison' (not 'institution_rank'),
    extract both institutions, return both ranks and scores, generate a 2-institution
    comparison chart, and handle parameters accurately.
    """
    import json
    req = api.NLQueryRequest(question="Compare IIT Indore and IIT Madras in Engineering in 2025.")
    res = api.natural_language_query(req)

    # 1. Intent check
    assert res["intent"] == "institution_comparison"
    assert res["query_plan"]["intent"] == "institution_comparison"
    assert res["query_plan"]["primary_year"] == 2025
    assert res["query_plan"]["category"] == "Engineering"

    # 2. Both institutions extracted
    assert len(res["query_plan"]["institutions"]) == 2
    assert "Indian Institute of Technology Indore" in res["query_plan"]["matched_institutions"]
    assert "Indian Institute of Technology Madras" in res["query_plan"]["matched_institutions"]

    # 3. Data records
    assert len(res["data"]) == 2
    data_names = [r["name"] for r in res["data"]]
    assert "Indian Institute of Technology Indore" in data_names
    assert "Indian Institute of Technology Madras" in data_names

    indore_rec = next(r for r in res["data"] if r["name"] == "Indian Institute of Technology Indore")
    madras_rec = next(r for r in res["data"] if r["name"] == "Indian Institute of Technology Madras")

    assert indore_rec["rank"] == 12.0
    assert round(indore_rec["score"], 2) == 66.65
    assert madras_rec["rank"] == 1.0
    assert round(madras_rec["score"], 2) == 88.72

    # 4. Summary text mentions both
    summary = res["summary_text"]
    assert "Indian Institute of Technology Indore" in summary
    assert "Indian Institute of Technology Madras" in summary
    assert "#1" in summary
    assert "#12" in summary
    assert "lower rank number" in summary.lower()

    # 5. Chart contains data for both institutions
    assert res["figure_json"] is not None
    chart_dict = json.loads(res["figure_json"])
    assert len(chart_dict["data"]) >= 2
    trace_names = [t["name"] for t in chart_dict["data"]]
    assert any("Indore" in tn for tn in trace_names)
    assert any("Madras" in tn for tn in trace_names)


def test_regression_compare_with_missing_institution():
    """
    Regression test: Comparison question where one institution does not exist.
    Must return clear missing institution message and not fabricate data.
    """
    req = api.NLQueryRequest(question="Compare IIT Indore and Hogwarts in 2025")
    res = api.natural_language_query(req)

    assert res["intent"] == "institution_comparison"
    assert res["data"] == []
    assert res["figure_json"] is None
    assert "Hogwarts" in res["summary_text"]
    assert "not found" in res["summary_text"].lower()
    assert "Madras" not in res["summary_text"]


def test_regression_compare_unranked_category():
    """
    Regression test: Comparison where institution is not ranked in requested category.
    """
    req = api.NLQueryRequest(question="Compare IIT Indore and IIT Madras in Architecture in 2025")
    res = api.natural_language_query(req)

    assert res["intent"] == "institution_comparison"
    assert res["data"] == []
    assert res["figure_json"] is None
    assert "not ranked in the **Architecture** category" in res["summary_text"]


def test_historical_milestone_iit_madras_first_rank():
    """
    Test historical question: 'In which year did IIT Madras first rank #1 in Engineering?'
    Must classify as 'historical_milestone', target_mode='exact', target_rank=1,
    search across 2017-2025, and return 2017.
    """
    req = api.NLQueryRequest(question="In which year did IIT Madras first rank #1 in Engineering?", category="Engineering")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_milestone"
    assert res["query_plan"]["category"] == "Engineering"
    assert res["query_plan"]["target_rank"] == 1
    assert res["query_plan"]["target_mode"] == "exact"
    assert "2017" in res["summary_text"]
    assert "Indian Institute of Technology Madras" in res["summary_text"]
    assert "first ranked **#1**" in res["summary_text"]
    assert len(res["data"]) >= 1
    # First matching row should be 2017
    assert res["data"][0]["year"] == 2017
    assert res["figure_json"] is not None


def test_historical_milestone_first_enter_top_10():
    """
    Regression test: 'When did IIT Indore first enter the top 10 in Engineering?'
    Must detect target_mode='threshold' and target_rank=10, search across years,
    and directly return 2020 at Rank #10 without claiming 'never ranked #1'.
    """
    req = api.NLQueryRequest(question="When did IIT Indore first enter the top 10 in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_milestone"
    assert res["query_plan"]["target_rank"] == 10
    assert res["query_plan"]["target_mode"] == "threshold"
    assert res["query_plan"]["category"] == "Engineering"

    summary = res["summary_text"]
    assert "Indian Institute of Technology Indore" in summary
    assert "first entered **the top 10**" in summary
    assert "2020" in summary
    assert "#10" in summary
    assert "never ranked #1" not in summary.lower()
    assert "never ranked" not in summary.lower()

    assert len(res["data"]) >= 1
    assert res["data"][0]["year"] == 2020
    assert res["figure_json"] is not None


def test_historical_milestone_first_enter_top_5():
    """
    Regression test: 'When did IIT Indore first enter the top 5 in Engineering?'
    Must detect target_mode='threshold' and target_rank=5, recognize that IIT Indore
    never entered top 5 (best rank was #10 in 2020), and NOT say 'never ranked #1'.
    """
    req = api.NLQueryRequest(question="When did IIT Indore first enter the top 5 in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_milestone"
    assert res["query_plan"]["target_rank"] == 5
    assert res["query_plan"]["target_mode"] == "threshold"

    summary = res["summary_text"]
    assert "Indian Institute of Technology Indore" in summary
    assert "never entered **the top 5**" in summary
    assert "ranked #1" not in summary.lower()
    assert "#10" in summary
    assert "2020" in summary
    assert res["figure_json"] is not None


def test_historical_milestone_unachieved_rank():
    """
    Test historical question where rank was never achieved:
    'In which year did IIT Indore first rank #1 in Engineering?'
    Must inform user it was never achieved and report the best rank.
    """
    req = api.NLQueryRequest(question="In which year did IIT Indore first rank #1 in Engineering?", category="Engineering")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_milestone"
    assert "never ranked" in res["summary_text"].lower()
    assert "#10" in res["summary_text"]
    assert res["figure_json"] is not None


def test_query_without_explicit_year_defaults_to_latest():
    """
    Test query where no year is mentioned:
    'What is the rank of IIT Indore in Engineering?'
    Must use latest available year (2025) and include an explicit note rather than silently defaulting.
    """
    req = api.NLQueryRequest(question="What is the rank of IIT Indore in Engineering?", category="Engineering")
    res = api.natural_language_query(req)

    assert res["intent"] == "institution_rank"
    assert res["query_plan"]["primary_year"] == 2025
    assert res["query_plan"]["year_mode"] == "default_latest"
    assert "2025" in res["summary_text"]
    assert "No year was specified" in res["summary_text"]


def test_historical_rank_status_iit_madras_lose_1():
    """
    Regression test: 'Did IIT Madras ever lose its #1 position in Engineering?'
    Must classify as 'historical_rank_status', check all years (2017-2025),
    and answer directly with 'No. IIT Madras remained ranked #1 in Engineering from 2017 through 2025.'
    """
    req = api.NLQueryRequest(question="Did IIT Madras ever lose its #1 position in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_rank_status"
    assert res["query_plan"]["target_rank"] == 1
    assert res["query_plan"]["target_mode"] == "exact"
    assert res["query_plan"]["category"] == "Engineering"

    summary = res["summary_text"]
    assert summary.startswith("No.")
    assert "remained ranked **#1** in **Engineering** from 2017 through 2025" in summary
    assert "Indian Institute of Technology Madras" in summary
    assert len(res["data"]) == 9
    assert res["figure_json"] is not None


def test_historical_rank_status_consistently_ranked():
    """
    Test: 'Has IIT Madras consistently ranked #1 in Engineering?'
    Must classify as 'historical_rank_status' and directly answer 'Yes.'
    """
    req = api.NLQueryRequest(question="Has IIT Madras consistently ranked #1 in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_rank_status"
    summary = res["summary_text"]
    assert summary.startswith("Yes.")
    assert "remained ranked **#1** in **Engineering** continuously from 2017 through 2025" in summary


def test_historical_rank_status_position_lost():
    """
    Test: 'Did IIT Indore ever lose its top 10 position in Engineering?'
    Must classify as 'historical_rank_status', answer 'Yes.', and specify the years and ranks lost.
    """
    req = api.NLQueryRequest(question="Did IIT Indore ever lose its top 10 position in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_rank_status"
    assert res["query_plan"]["target_rank"] == 10
    assert res["query_plan"]["target_mode"] == "threshold"

    summary = res["summary_text"]
    assert summary.startswith("Yes.")
    assert "lost its **top 10** position" in summary
    assert "2022" in summary
    assert "#16" in summary
    assert "2024" in summary


def test_historical_rank_status_never_held():
    """
    Test: 'Did IIT Indore ever lose its #1 position in Engineering?'
    Must recognize that it never held #1 to lose.
    """
    req = api.NLQueryRequest(question="Did IIT Indore ever lose its #1 position in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "historical_rank_status"
    summary = res["summary_text"]
    assert "never held **#1**" in summary
    assert "#10" in summary


def test_multi_institution_comparison_three_institutions():
    """
    Regression test: 'Compare IIT Indore, IIT Madras, and IIT Bombay in Engineering in 2025.'
    Must parse all 3 institutions in order, retrieve all 3 records, report all 3 in summary and table,
    and generate a multi-institution comparison chart.
    """
    import json
    req = api.NLQueryRequest(question="Compare IIT Indore, IIT Madras, and IIT Bombay in Engineering in 2025.")
    res = api.natural_language_query(req)

    assert res["intent"] == "institution_comparison"
    assert res["query_plan"]["intent"] == "institution_comparison"
    assert res["query_plan"]["primary_year"] == 2025
    assert res["query_plan"]["category"] == "Engineering"

    # All 3 institutions extracted in order
    insts = res["query_plan"]["institutions"]
    assert len(insts) == 3
    assert insts[0] == "Indian Institute of Technology Indore"
    assert insts[1] == "Indian Institute of Technology Madras"
    assert insts[2] == "Indian Institute of Technology Bombay"

    # All 3 in data
    assert len(res["data"]) == 3
    names = [r["name"] for r in res["data"]]
    assert "Indian Institute of Technology Indore" in names
    assert "Indian Institute of Technology Madras" in names
    assert "Indian Institute of Technology Bombay" in names

    # Summary text
    summary = res["summary_text"]
    assert "Comparison of 3 institutions" in summary
    assert "Indian Institute of Technology Madras" in summary
    assert "Indian Institute of Technology Bombay" in summary
    assert "Indian Institute of Technology Indore" in summary
    assert "#1" in summary
    assert "#3" in summary
    assert "#12" in summary
    assert "leads the group at Rank **#1**" in summary
    # Parameter breakdown has all 3
    assert "TLR" in summary
    assert "RPC" in summary
    assert "IIT Madras" in summary
    assert "IIT Bombay" in summary
    assert "IIT Indore" in summary

    # Chart verification
    assert res["figure_json"] is not None
    chart = json.loads(res["figure_json"])
    assert len(chart["data"]) >= 3


def test_parameter_comparison_single_institution():
    """
    Test parameter comparison: 'Compare IIT Indore's TLR and RPC scores in Engineering in 2025.'
    Must classify as 'parameter_comparison', evaluate TLR vs RPC, report difference,
    and generate a parameter bar chart.
    """
    req = api.NLQueryRequest(question="Compare IIT Indore's TLR and RPC scores in Engineering in 2025.")
    res = api.natural_language_query(req)

    assert res["intent"] == "parameter_comparison"
    assert res["query_plan"]["primary_year"] == 2025
    assert res["query_plan"]["category"] == "Engineering"
    assert len(res["data"]) == 1
    assert res["data"][0]["name"] == "Indian Institute of Technology Indore"

    summary = res["summary_text"]
    assert "Indian Institute of Technology Indore" in summary
    assert "81.25" in summary
    assert "59.55" in summary
    assert "21.70" in summary
    assert "TLR is higher than RPC" in summary or "TLR** is higher than **RPC" in summary
    assert res["figure_json"] is not None


def test_rank_progression_engineering():
    """
    Test rank progression: 'Did IIT Indore improve its rank every year in Engineering?'
    Must classify as 'rank_progression', evaluate all transitions, and answer 'No.'
    with detailed breakdown of improvements and declines.
    """
    req = api.NLQueryRequest(question="Did IIT Indore improve its rank every year in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "rank_progression"
    summary = res["summary_text"]
    assert summary.startswith("No.")
    assert "did not improve its rank every year in **Engineering**" in summary
    assert "Years Improved" in summary
    assert "Years Declined" in summary
    assert "2018" in summary
    assert "2020" in summary
    assert "2021" in summary
    assert "2022" in summary
    assert len(res["data"]) == 9
    assert res["figure_json"] is not None


def test_rank_progression_overall():
    """
    Test rank progression in Overall: 'Did IIT Indore improve its rank every year?'
    Must classify as 'rank_progression', answer 'No.', and note missing/unranked years.
    """
    req = api.NLQueryRequest(question="Did IIT Indore improve its rank every year?")
    res = api.natural_language_query(req)

    assert res["intent"] == "rank_progression"
    summary = res["summary_text"]
    assert summary.startswith("No.")
    assert "did not improve its rank every year in **Overall**" in summary
    assert "Unranked" in summary or "no records" in summary
    assert res["figure_json"] is not None


def test_best_rank_engineering():
    """
    Test best rank: 'What was IIT Indore's best rank in Engineering?'
    Must classify as 'best_rank', search all years, and return #10 in 2020.
    """
    req = api.NLQueryRequest(question="What was IIT Indore's best rank in Engineering?")
    res = api.natural_language_query(req)

    assert res["intent"] == "best_rank"
    summary = res["summary_text"]
    assert "best NIRF rank achieved" in summary
    assert "#10" in summary
    assert "2020" in summary
    assert "62.88" in summary
    assert res["figure_json"] is not None


def test_best_rank_overall():
    """
    Test best rank in Overall: 'What was IIT Indore's best rank?'
    Must classify as 'best_rank' and return #23 in 2020.
    """
    req = api.NLQueryRequest(question="What was IIT Indore's best rank?")
    res = api.natural_language_query(req)

    assert res["intent"] == "best_rank"
    summary = res["summary_text"]
    assert "#23" in summary
    assert "2020" in summary
    assert "55.94" in summary
    assert res["figure_json"] is not None


# ── Tests for Q6.5 and Q7.1 Endpoints ──────────────────────────────────────────

def test_endpoint_state_score_distribution_success():
    """
    Q6.5 Endpoint: Test /api/stats/state-score-distribution with default parameters.
    Must return records for states with >= 3 institutions, valid Plotly box plot figure,
    and metadata.
    """
    res = api.state_score_distribution(year=2024, category="Overall", min_institutions=3)
    assert isinstance(res, dict)
    assert "records" in res
    assert "figure" in res
    assert "count" in res
    assert "states_count" in res
    assert res["count"] > 0
    assert res["states_count"] > 0
    assert res["year"] == 2024
    assert res["category"] == "Overall"
    assert res["min_institutions"] == 3

    # Check records format
    first = res["records"][0]
    assert "name" in first
    assert "state" in first
    assert "score" in first
    assert "rank" in first

    # Check figure format (Plotly Box plot)
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert len(fig["data"]) > 0
    assert fig["data"][0]["type"] == "box"


def test_endpoint_state_score_distribution_filtering():
    """
    Q6.5 Endpoint: Test with different category, year, and high threshold.
    """
    res_eng = api.state_score_distribution(year=2023, category="Engineering", min_institutions=5)
    assert res_eng["year"] == 2023
    assert res_eng["category"] == "Engineering"
    assert res_eng["count"] > 0
    # Every state in records must have at least 5 institutions
    from collections import Counter
    state_counts = Counter(r["state"] for r in res_eng["records"])
    assert all(count >= 5 for count in state_counts.values())

    # Empty result test with unrealistically high threshold
    res_empty = api.state_score_distribution(year=2024, category="Overall", min_institutions=100)
    assert res_empty["count"] == 0
    assert res_empty["records"] == []
    assert res_empty["figure"] is None


def test_endpoint_band_to_top50_success():
    """
    Q7.1 Endpoint: Test /api/transitions/band-to-top50 between 2023 and 2024.
    Must find institutions that moved from 51-100 to <= 50.
    """
    res = api.band_to_top50(category="Overall", year1=2023, year2=2024)
    assert isinstance(res, dict)
    assert "records" in res
    assert "figure" in res
    assert "transition_count" in res
    assert res["transition_count"] == 2
    assert len(res["records"]) == 2

    # Check columns
    row = res["records"][0]
    assert "name" in row
    assert "rank_year1" in row
    assert "rank_year2" in row
    assert "score_year1" in row
    assert "score_year2" in row

    # Confirm transition condition: 51 <= rank_year1 <= 100, rank_year2 <= 50
    for r in res["records"]:
        assert 50 < r["rank_year1"] <= 100
        assert r["rank_year2"] <= 50

    # Figure validation
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert fig["data"][0]["type"] == "scatter"


def test_endpoint_band_to_top50_validation():
    """
    Q7.1 Endpoint: Test validation on same years and invalid year inputs.
    """
    from fastapi import HTTPException
    import pytest

    # Same year error
    with pytest.raises(HTTPException) as exc_same:
        api.band_to_top50(category="Overall", year1=2024, year2=2024)
    assert exc_same.value.status_code == 400
    assert "must be different" in exc_same.value.detail.lower()

    # Invalid year error (outside 2017-2025)
    with pytest.raises(HTTPException) as exc_invalid:
        api.band_to_top50(category="Overall", year1=2010, year2=2024)
    assert exc_invalid.value.status_code == 400
    assert "invalid year" in exc_invalid.value.detail.lower()


def test_endpoint_rank_distribution():
    """
    Q3.2 Endpoint: Test /api/univariate/rank-distribution.
    Verifies rank bands, total_ranked, records, and Plotly figure.
    """
    res = api.rank_distribution(year=2024, category="Overall")
    assert isinstance(res, dict)
    assert "records" in res
    assert "bands" in res
    assert "figure" in res
    assert "total_ranked" in res
    assert res["total_ranked"] == 100
    assert res["year"] == 2024
    assert res["category"] == "Overall"

    # Verify bands structure
    bands = res["bands"]
    assert len(bands) >= 4
    band_names = [b["band"] for b in bands]
    assert any("Top 10" in b for b in band_names)
    assert any("11–25" in b for b in band_names)
    assert any("26–50" in b for b in band_names)
    assert any("51–100" in b for b in band_names)

    # Verify figure
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert fig["data"][0]["type"] == "bar"


def test_endpoint_high_teaching_low_perception():
    """
    Q5.3 Endpoint: Test /api/multivariate/high-teaching-low-perception.
    Verifies thresholds, outlier records, and scatter figure with reference lines.
    """
    res = api.high_teaching_low_perception(year=2024, category="Overall", percentile_high=75.0, percentile_low=50.0)
    assert isinstance(res, dict)
    assert "records" in res
    assert "figure" in res
    assert "tlr_threshold" in res
    assert "perception_threshold" in res
    assert res["count"] == len(res["records"])
    assert res["count"] > 0

    # Verify condition: tlr >= threshold and perception <= threshold
    tlr_th = res["tlr_threshold"]
    pr_th = res["perception_threshold"]
    for row in res["records"]:
        assert row["tlr"] >= tlr_th - 0.01
        assert row["perception"] <= pr_th + 0.01

    # Verify figure
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert len(fig["data"]) >= 1


def test_endpoint_research_teaching_gap():
    """
    Q8.2 Endpoint: Test /api/outliers/research-teaching-gap.
    Verifies gap calculation (RPC - TLR), limit, and horizontal bar chart figure.
    """
    res = api.research_teaching_gap_outliers(year=2024, category="Overall", limit=10)
    assert isinstance(res, dict)
    assert "records" in res
    assert "figure" in res
    assert res["count"] == 10
    assert len(res["records"]) == 10

    # Verify gap = rpc - tlr
    for row in res["records"]:
        assert "research_teaching_gap" in row
        expected_gap = round(row["rpc"] - row["tlr"], 2)
        assert abs(row["research_teaching_gap"] - expected_gap) < 0.02

    # Verify figure
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert fig["data"][0]["type"] == "bar"
    assert fig["data"][0]["orientation"] == "h"


def test_endpoint_strong_param_poor_rank():
    """
    Q8.4 Endpoint: Test /api/outliers/strong-param-poor-rank.
    Verifies param filtering, rank > cutoff condition, reversed rank axis, and validation.
    """
    from fastapi import HTTPException
    import pytest

    # Test with TLR parameter (has matches in 2024 Overall)
    res = api.strong_param_poor_rank(year=2024, category="Overall", param="tlr", param_percentile=75.0, rank_min=50)
    assert isinstance(res, dict)
    assert "records" in res
    assert "figure" in res
    assert res["param"] == "tlr"
    assert res["count"] == len(res["records"])
    assert res["count"] > 0

    # Verify every match has rank > 50 and tlr >= threshold
    for row in res["records"]:
        assert row["rank"] > 50
        assert row["tlr"] >= res["param_threshold"] - 0.01

    # Figure validation
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert fig["layout"]["yaxis"]["autorange"] == "reversed"

    # Validation: invalid parameter raises 400
    with pytest.raises(HTTPException) as exc_invalid:
        api.strong_param_poor_rank(year=2024, category="Overall", param="invalid_param")
    assert exc_invalid.value.status_code == 400
    assert "invalid parameter" in exc_invalid.value.detail.lower()


def test_endpoint_geo_distribution_trend():
    """
    Q2.2 Endpoint: Test /api/geo/distribution-trend.
    Verifies state-by-year pivot data, Plotly heatmap figure, and category filtering.
    """
    res = api.geo_distribution_trend(category="Overall", top_n=100)
    assert isinstance(res, dict)
    assert "records" in res
    assert "figure" in res
    assert "count" in res
    assert "years" in res
    assert res["count"] > 0
    assert len(res["years"]) >= 8
    assert res["category"] == "Overall"
    assert res["top_n"] == 100

    # Verify heatmap figure
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert fig["data"][0]["type"] == "heatmap"

    # Verify records have state and year columns
    first_row = res["records"][0]
    assert "state" in first_row
    assert any(str(yr) in first_row or yr in first_row for yr in [2017, 2024])

    # Category filtering
    res_eng = api.geo_distribution_trend(category="Engineering", top_n=50)
    assert res_eng["category"] == "Engineering"
    assert res_eng["top_n"] == 50
    assert res_eng["count"] > 0


def test_endpoint_improved_score_declining_params():
    """
    Q5.4 Endpoint: Test /api/multivariate/improved-score-declining-params.
    Verifies qualifying institutions with overall gain > 0 and num_declined >= 1,
    and checks the diverging bar chart figure.
    """
    res = api.improved_score_declining_params(category="Overall", start_year=2017, end_year=2024)
    assert isinstance(res, dict)
    assert "records" in res
    assert "figure" in res
    assert "count" in res
    assert res["count"] > 0
    assert res["start_year"] == 2017
    assert res["end_year"] == 2024

    # Verify analytical correctness of records
    for row in res["records"]:
        assert row["score_improvement"] > 0
        assert row["end_score"] > row["start_score"]
        assert row["num_declined"] >= 1
        assert len(row["declined_parameters"]) > 0

    # Verify figure
    fig = res["figure"]
    assert fig is not None
    assert "data" in fig
    assert len(fig["data"]) == 2  # Overall gain trace & Worst decline trace
    assert fig["layout"]["barmode"] == "relative"


def test_endpoint_improved_score_declining_params_validation():
    """
    Q5.4 Endpoint: Test validation on invalid year ranges and non-existent years.
    """
    from fastapi import HTTPException
    import pytest

    # Invalid start year >= end year
    with pytest.raises(HTTPException) as exc_range:
        api.improved_score_declining_params(category="Overall", start_year=2024, end_year=2020)
    assert exc_range.value.status_code == 400
    assert "start year must be earlier" in exc_range.value.detail.lower()

    # Same year
    with pytest.raises(HTTPException) as exc_same:
        api.improved_score_declining_params(category="Overall", start_year=2024, end_year=2024)
    assert exc_same.value.status_code == 400
    assert "start year must be earlier" in exc_same.value.detail.lower()

    # Out of range year
    with pytest.raises(HTTPException) as exc_out:
        api.improved_score_declining_params(category="Overall", start_year=2005, end_year=2024)
    assert exc_out.value.status_code == 400
    assert "invalid year range" in exc_out.value.detail.lower()


def test_endpoint_dynamic_filter():
    """
    Test POST /api/dynamic/filter endpoint with filters matching Level 2 Dynamic Explorer defaults.
    """
    req = api.DynamicDataRequest(
        category="Engineering",
        start_year=2021,
        end_year=2025,
        states=["Karnataka", "Tamil Nadu"],
        top_n=100,
    )
    res = api.dynamic_filter(req)
    assert "data" in res
    assert "total" in res
    assert res["total"] > 0
    assert len(res["data"]) == res["total"]
    # Check that returned records only have Karnataka and Tamil Nadu
    states = {r["state"] for r in res["data"]}
    assert states.issubset({"Karnataka", "Tamil Nadu"})
    # Check that available_states and available_institutions are returned
    assert "available_states" in res
    assert len(res["available_states"]) > 0
    assert "Karnataka" in res["available_states"]
    assert "available_institutions" in res
    assert len(res["available_institutions"]) > 0











