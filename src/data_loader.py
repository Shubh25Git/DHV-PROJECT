"""
Data Loader Module
==================
This module is responsible for reading NIRF ranking datasets into Pandas DataFrames.

It supports:
1. Loading all raw CSV files downloaded by the scraper from data/raw/downloads/.
2. Manually importing individual CSV or Excel (.xlsx, .xls) files uploaded by users.
3. Loading the cleaned master dataset from data/processed/nirf_master.csv.

Every function is kept simple and beginner-friendly with clear docstrings and error handling.
"""

import os
import glob
import logging
import pandas as pd

DOWNLOADS_DIR = os.path.join("data", "raw", "downloads")
PROCESSED_FILE = os.path.join("data", "processed", "nirf_master.csv")

# Expected standard columns for NIRF data
EXPECTED_COLUMNS = [
    "year",
    "category",
    "institute_id",
    "name",
    "tlr",
    "rpc",
    "go",
    "oi",
    "perception",
    "city",
    "state",
    "score",
    "rank"
]


def load_raw_scraped_data(directory=DOWNLOADS_DIR):
    """
    Finds and reads all raw CSV files created by the scraper in data/raw/downloads/.
    Returns a combined raw DataFrame.
    """
    csv_pattern = os.path.join(directory, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        logging.warning(f"No raw CSV files found in {directory}. Please run the scraper first.")
        return pd.DataFrame()

    dataframes = []
    for filepath in csv_files:
        try:
            df = pd.read_csv(filepath, encoding="utf-8")
            dataframes.append(df)
        except Exception as e:
            logging.error(f"Error reading {filepath}: {e}")

    if not dataframes:
        return pd.DataFrame()

    combined_df = pd.concat(dataframes, ignore_index=True)
    logging.info(f"Loaded {len(combined_df)} raw records across {len(dataframes)} files.")
    return combined_df


def load_manual_file(file_source, filename="custom_file"):
    """
    Reads an uploaded or placed file (CSV or Excel) and maps its columns to the standard NIRF schema.
    
    Parameters:
    - file_source: A file path (string) or an in-memory file-like object (from Streamlit uploader).
    - filename: The name of the file (used to determine whether it's CSV or Excel).
    
    Returns:
    - (DataFrame, None) on success.
    - (None, error_message) on failure.
    """
    filename_lower = str(filename).lower()
    df = None

    try:
        if filename_lower.endswith(".csv"):
            df = pd.read_csv(file_source, encoding="utf-8")
        elif filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
            df = pd.read_excel(file_source)
        else:
            return None, "Unsupported file format. Please upload a .csv or .xlsx file."
    except Exception as e:
        return None, f"Failed to read file: {e}"

    if df is None or df.empty:
        return None, "The uploaded file is empty."

    # Column name normalization (lowercase, stripped whitespace)
    normalized_cols = {col: str(col).strip().lower().replace(" ", "_") for col in df.columns}
    df = df.rename(columns=normalized_cols)

    # Check for minimum required columns: name and rank or score
    has_name = any(c in df.columns for c in ["name", "institution_name", "institute_name", "college_name"])
    has_rank_or_score = any(c in df.columns for c in ["rank", "score"])

    if not has_name or not has_rank_or_score:
        return None, "File missing required columns. It must include institution name and either rank or score."

    # Standardize column names if common aliases are used
    column_mapping = {
        "institution_name": "name",
        "institute_name": "name",
        "college_name": "name",
        "overall_score": "score",
        "overall_rank": "rank",
        "ranking": "rank"
    }
    df = df.rename(columns=column_mapping)

    return df, None


def load_master_data(filepath=PROCESSED_FILE):
    """
    Loads the cleaned master NIRF dataset from data/processed/nirf_master.csv.
    If the file does not exist, returns an empty DataFrame.
    """
    if not os.path.exists(filepath):
        logging.warning(f"Master file {filepath} not found. Running preprocessing may be needed.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(filepath, encoding="utf-8")
        # Ensure numerical types
        numeric_cols = ["year", "score", "rank", "tlr", "rpc", "go", "oi", "perception"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        logging.error(f"Error loading master dataset from {filepath}: {e}")
        return pd.DataFrame()
