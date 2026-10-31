"""
Data Preprocessing Pipeline
============================
This module cleans, standardizes, validates, and consolidates all raw NIRF ranking
records into a single high-quality master dataset: data/processed/nirf_master.csv.

Key responsibilities:
1. Standardize column names, text fields, and categories.
2. Clean institution names and map state names to official standards.
3. Parse and convert numerical fields (score, rank, TLR, RPC, GO, OI, PERCEPTION).
4. Preserve rank bands without confusing missing ranks.
5. Identify and handle duplicates.
6. Generate a comprehensive data-quality report.
"""

import os
import sys
import re
import json
import logging
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Standard state mapping for Indian States and Union Territories
STATE_MAPPING = {
    "jammu and kashmir": "Jammu and Kashmir",
    "jammu & kashmir": "Jammu and Kashmir",
    "jammu and kashmir": "Jammu and Kashmir",
    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "orissa": "Odisha",
    "odisha": "Odisha",
    "telangana": "Telangana",
    "tamilnadu": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",
    "uttaranchal": "Uttarakhand",
    "uttarakhand": "Uttarakhand",
    "chhatisgarh": "Chhattisgarh",
    "chhattisgarh": "Chhattisgarh",
}

# Category name normalization mapping
CATEGORY_MAPPING = {
    "overall": "Overall",
    "university": "University",
    "college": "College",
    "engineering": "Engineering",
    "management": "Management",
    "pharmacy": "Pharmacy",
    "medical": "Medical",
    "dental": "Dental",
    "law": "Law",
    "architecture": "Architecture",
    "agriculture": "Agriculture",
    "research": "Research",
    "statepublicuniversity": "State Public University",
    "openuniversity": "Open University",
    "skilluniversity": "Skill University",
    "sdginstitutions": "SDG Institutions",
    "innovation": "Innovation",
    "specialrank": "Special Ranking"
}


def clean_text_field(value):
    """Trim leading/trailing spaces and collapse internal consecutive whitespaces."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return " ".join(text.split())


def standardize_state(raw_state):
    """Map state variations or typos to standardized official state names."""
    if pd.isna(raw_state):
        return "Unknown"
    cleaned = clean_text_field(raw_state)
    lower = cleaned.lower()
    return STATE_MAPPING.get(lower, cleaned.title())


def standardize_category(raw_category):
    """Normalize category names to standard Title Case format."""
    if pd.isna(raw_category):
        return "Overall"
    key = str(raw_category).strip().lower().replace(" ", "").replace("_", "")
    return CATEGORY_MAPPING.get(key, str(raw_category).strip().title())


def parse_rank_value(raw_rank):
    """
    Extract numeric rank if available.
    For rank bands like '101-150', returns the midpoint (e.g., 125.5) or lower bound,
    while storing the raw band in a separate column.
    """
    if pd.isna(raw_rank):
        return np.nan
    s = str(raw_rank).strip()
    # If pure number
    if s.isdigit():
        return float(s)
    # If rank band like '101-150' or '151-200'
    match = re.search(r"(\d+)\s*-\s*(\d+)", s)
    if match:
        lower = float(match.group(1))
        upper = float(match.group(2))
        return (lower + upper) / 2.0
    # If rank like '100+'
    num_match = re.search(r"(\d+)", s)
    if num_match:
        return float(num_match.group(1))
    return np.nan


def clean_institution_name(name):
    """
    Standardize institution name across years:
    - Strips leftover HTML tags or buttons (e.g. 'More Details', 'Close |')
    - Removes duplicate spaces
    - Standardizes common abbreviations like 'I.I.T.' -> 'IIT', 'N.I.T.' -> 'NIT'
    """
    if pd.isna(name):
        return "Unknown Institution"
    s = str(name).strip()
    s = re.split(r"More Details|Close\s*\||TLR\s*\(", s, flags=re.IGNORECASE)[0]
    s = " ".join(s.split())
    # Clean leading/trailing punctuation
    s = s.strip(" ,.-")
    return s


def preprocess_nirf_dataframe(df):
    """
    Preprocess a raw NIRF DataFrame:
    1. Standardizes text fields (name, city, state, category).
    2. Converts numerical fields (score, rank, tlr, rpc, go, oi, perception).
    3. Handles duplicates.
    4. Validates ranges.
    """
    if df.empty:
        return df

    cleaned = df.copy()

    # 1. Standardize year
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce").fillna(2024).astype(int)

    # 2. Standardize category
    cleaned["category"] = cleaned["category"].apply(standardize_category)

    # 3. Clean institution names and IDs
    cleaned["name"] = cleaned["name"].apply(clean_institution_name)
    cleaned["institute_id"] = cleaned["institute_id"].fillna("").astype(str).str.strip()

    # 4. Standardize geographic locations
    cleaned["city"] = cleaned["city"].apply(clean_text_field)
    cleaned["state"] = cleaned["state"].apply(standardize_state)

    # 5. Numerical conversion for overall score
    cleaned["score"] = pd.to_numeric(cleaned["score"], errors="coerce")
    # Score must be between 0 and 100
    cleaned.loc[(cleaned["score"] < 0) | (cleaned["score"] > 100), "score"] = np.nan

    # 6. Parse rank into numeric rank, preserving raw string
    cleaned["raw_rank"] = cleaned["rank"].astype(str)
    cleaned["rank"] = cleaned["rank"].apply(parse_rank_value)
    # Rank must be strictly positive
    cleaned.loc[cleaned["rank"] <= 0, "rank"] = np.nan

    # 7. Convert the five NIRF parameters (TLR, RPC, GO, OI, PERCEPTION)
    param_columns = ["tlr", "rpc", "go", "oi", "perception"]
    for param in param_columns:
        if param in cleaned.columns:
            cleaned[param] = pd.to_numeric(cleaned[param], errors="coerce")
            # Values should be within 0 to 100
            cleaned.loc[(cleaned[param] < 0) | (cleaned[param] > 100), param] = np.nan
        else:
            cleaned[param] = np.nan

    # 8. Deduplication:
    # A single institution should only appear once per year and per category.
    # Prefer non-empty institute_id when deduplicating; fallback to name.
    dedup_subset = ["year", "category", "name"]
    initial_count = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=dedup_subset, keep="first")
    removed_duplicates = initial_count - len(cleaned)
    if removed_duplicates > 0:
        logging.info(f"Deduplication removed {removed_duplicates} duplicate records.")

    # 9. Sort cleanly by Year, Category, Rank
    cleaned = cleaned.sort_values(by=["year", "category", "rank"], ascending=[True, True, True]).reset_index(drop=True)

    return cleaned


# ==============================================================================
# Validation Functions (Consolidated into Preprocessing)
# ==============================================================================

def validate_schema(df, required_columns=None):
    """Checks whether required columns are present in the DataFrame."""
    if required_columns is None:
        required_columns = ["year", "category", "name", "score", "rank"]
    missing = [col for col in required_columns if col not in df.columns]
    return len(missing) == 0, missing


def validate_score_ranges(df):
    """Validates that scores and parameters fall strictly between 0 and 100."""
    score_columns = ["score", "tlr", "rpc", "go", "oi", "perception"]
    invalid_counts = {}
    for col in score_columns:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            out_of_bounds = series[(series < 0) | (series > 100)]
            invalid_counts[col] = len(out_of_bounds)
    return invalid_counts


def validate_rank_ranges(df):
    """Validates that ranks are strictly positive numbers."""
    if "rank" not in df.columns:
        return 0
    ranks = pd.to_numeric(df["rank"], errors="coerce").dropna()
    return len(ranks[ranks <= 0])


def check_duplicates(df, subset=None):
    """Checks for duplicate records across subset columns."""
    if subset is None:
        subset = ["year", "category", "name"]
    valid_subset = [c for c in subset if c in df.columns]
    if not valid_subset:
        return 0, pd.DataFrame()
    dup_mask = df.duplicated(subset=valid_subset, keep=False)
    dup_count = dup_mask.sum()
    sample_dups = df[dup_mask].head(10) if dup_count > 0 else pd.DataFrame()
    return dup_count, sample_dups


def validate_master_dataset(df):
    """Runs verification checks against the dataset and returns a summary dict."""
    is_schema_ok, missing_cols = validate_schema(df)
    score_invalids = validate_score_ranges(df)
    rank_invalids = validate_rank_ranges(df)
    dup_count, _ = check_duplicates(df)

    has_issues = (
        not is_schema_ok
        or any(c > 0 for c in score_invalids.values())
        or rank_invalids > 0
        or dup_count > 0
    )

    return {
        "valid": not has_issues,
        "missing_columns": missing_cols,
        "invalid_scores": score_invalids,
        "invalid_ranks": rank_invalids,
        "duplicate_records": dup_count,
        "total_records": len(df)
    }


def generate_data_quality_report(df, output_path="logs/data_quality_report.json"):
    """
    Computes a comprehensive data-quality summary:
    - Total record count
    - Year coverage
    - Category breakdown
    - Missing value percentages for each column
    - Score and rank summary statistics
    - Parameter availability by year
    """
    report = {
        "total_records": int(len(df)),
        "unique_institutions": int(df["name"].nunique()),
        "unique_states": int(df["state"].nunique()),
        "years_covered": sorted([int(y) for y in df["year"].unique()]),
        "categories_covered": sorted(df["category"].unique().tolist()),
        "records_per_year": {str(k): int(v) for k, v in df["year"].value_counts().sort_index().items()},
        "records_per_category": {str(k): int(v) for k, v in df["category"].value_counts().items()},
        "missing_values": {str(k): int(v) for k, v in df.isnull().sum().items()},
        "missing_percentages": {str(k): round(float(v / len(df) * 100), 2) for k, v in df.isnull().sum().items()},
        "score_statistics": {
            "mean": round(float(df["score"].mean()), 2) if not df["score"].isnull().all() else None,
            "median": round(float(df["score"].median()), 2) if not df["score"].isnull().all() else None,
            "min": round(float(df["score"].min()), 2) if not df["score"].isnull().all() else None,
            "max": round(float(df["score"].max()), 2) if not df["score"].isnull().all() else None,
        }
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def run_pipeline():
    """
    Executes the entire data cleaning pipeline:
    1. Loads raw scraped datasets.
    2. Runs preprocessing and standardization.
    3. Saves master CSV to data/processed/nirf_master.csv.
    4. Generates data quality report.
    """
    from src.data_loader import load_raw_scraped_data

    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    raw_df = load_raw_scraped_data()
    if raw_df.empty:
        logging.warning("No data found to process.")
        return None

    logging.info(f"Starting preprocessing on {len(raw_df)} raw records...")
    master_df = preprocess_nirf_dataframe(raw_df)

    processed_path = os.path.join("data", "processed", "nirf_master.csv")
    master_df.to_csv(processed_path, index=False, encoding="utf-8")
    logging.info(f"Successfully saved master dataset with {len(master_df)} records to {processed_path}")

    # Generate data quality report
    report = generate_data_quality_report(master_df)
    logging.info(f"Data quality report created. Total records: {report['total_records']}, Institutions: {report['unique_institutions']}")

    return master_df


if __name__ == "__main__":
    run_pipeline()
