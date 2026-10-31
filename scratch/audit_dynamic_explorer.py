"""
Audit script for Dynamic Analysis Explorer backend endpoint and calculations.
"""
import sys, os
sys.path.insert(0, os.path.abspath("."))
import api.main as api
import pandas as pd
import numpy as np

def run_audit():
    print("=== AUDIT 1: Verify Endpoint /api/dynamic/filter with 2017-2025 Real NIRF Data ===")
    for cat in ["Engineering", "Management", "Overall", "Pharmacy"]:
        req = api.DynamicDataRequest(category=cat, start_year=2017, end_year=2025, top_n=100)
        res = api.dynamic_filter(req)
        print(f"Category '{cat}': {res['total_count']} records, available states: {len(res['available_states'])}, available institutions: {len(res['available_institutions'])}")
        assert res["total_count"] > 0
        assert len(res["available_states"]) > 0
        assert len(res["available_institutions"]) > 0

    print("\n=== AUDIT 2: Top N filtering based on actual NIRF rank ===")
    for top_n in [5, 10, 20, 50, 100]:
        req = api.DynamicDataRequest(category="Overall", start_year=2024, end_year=2024, top_n=top_n)
        res = api.dynamic_filter(req)
        ranks = [r["rank"] for r in res["records"]]
        print(f"Top N={top_n}: {len(ranks)} records returned. Min rank: {min(ranks)}, Max rank: {max(ranks)}")
        assert max(ranks) <= top_n

    print("\n=== AUDIT 3: State Filtering & Institution List Consistency ===")
    req_ka = api.DynamicDataRequest(category="Engineering", start_year=2024, end_year=2024, states=["Karnataka"], top_n=100)
    res_ka = api.dynamic_filter(req_ka)
    ka_states = set(r["state"] for r in res_ka["records"])
    print(f"Karnataka only: {len(res_ka['records'])} records, states present: {ka_states}")
    assert ka_states == {"Karnataka"}
    # Verify institution options are from Karnataka
    assert "Indian Institute of Science" in res_ka["available_institutions"] or any("Karnataka" in i or "Bangalore" in i or "Bengaluru" in i for i in res_ka["available_institutions"])

    print("\n=== AUDIT 4: Correlation Coefficient (Pearson r) Calculation ===")
    req_corr = api.DynamicDataRequest(category="Engineering", start_year=2024, end_year=2024, top_n=100)
    res_corr = api.dynamic_filter(req_corr)
    df_c = pd.DataFrame(res_corr["records"])
    r_val = df_c["tlr"].corr(df_c["score"])
    print(f"Engineering 2024 (Top 100): Pearson r between TLR and Score = {r_val:.4f}")
    assert not np.isnan(r_val)

    print("\n=== AUDIT 5: Empty Result & Invalid Filter Handling ===")
    req_empty = api.DynamicDataRequest(category="Engineering", start_year=2024, end_year=2024, states=["NonExistentState"])
    res_empty = api.dynamic_filter(req_empty)
    print(f"Non-existent state count: {res_empty['total_count']}, records: {len(res_empty['records'])}")
    assert res_empty["total_count"] == 0

    print("\nALL BACKEND AUDIT CHECKS PASSED!")

if __name__ == "__main__":
    run_audit()
