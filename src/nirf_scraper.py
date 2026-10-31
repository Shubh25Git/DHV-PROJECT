"""
NIRF Ranking Web Scraper
=========================
This module collects NIRF ranking data from the official website (https://www.nirfindia.org)
for the years 2017 to 2025 across all available categories.

Key design principles:
- Beginner-friendly, step-by-step code.
- Politeness: uses standard headers, reasonable timeouts, and pauses between requests.
- Local caching: saves raw HTML files into data/raw/html/ so pages are never downloaded twice.
- Robust parsing: extracts institution ID, name, city, state, rank, score,
  and the five main parameters (TLR, RPC, GO, OI, PERCEPTION) when present.
- Records data collection status and logs in logs/scraper.log.
"""

import os
import re
import time
import json
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Setup logging to write both to file and terminal
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "scraper.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Standard browser headers to avoid 403 Forbidden blocks
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# Base landing pages for each NIRF year
YEAR_LANDING_PAGES = {
    2017: "https://www.nirfindia.org/Rankings/2017/Ranking2017.html",
    2018: "https://www.nirfindia.org/Rankings/2018/Ranking2018.html",
    2019: "https://www.nirfindia.org/Rankings/2019/Ranking2019.html",
    2020: "https://www.nirfindia.org/Rankings/2020/Ranking2020.html",
    2021: "https://www.nirfindia.org/Rankings/2021/Ranking.html",
    2022: "https://www.nirfindia.org/Rankings/2022/Ranking.html",
    2023: "https://www.nirfindia.org/Rankings/2023/Ranking.html",
    2024: "https://www.nirfindia.org/Rankings/2024/Ranking.html",
    2025: "https://www.nirfindia.org/Rankings/2025/Ranking.html",
}

# Directories for raw data storage
HTML_DIR = os.path.join("data", "raw", "html")
DOWNLOADS_DIR = os.path.join("data", "raw", "downloads")


def ensure_directories_exist():
    """Create necessary folder structure if it does not already exist."""
    os.makedirs(HTML_DIR, exist_ok=True)
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)


def download_html(url, cache_filename=None, delay_seconds=0.5):
    """
    Download HTML from a given URL with local caching.
    
    If cache_filename is provided and exists locally, load it from disk
    instead of making an unnecessary network request.
    """
    if cache_filename:
        cache_path = os.path.join(HTML_DIR, cache_filename)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return f.read(), True
            except Exception as e:
                logging.warning(f"Failed to read cache {cache_filename}: {e}. Re-downloading.")

    # Polite pause before request to prevent server strain
    time.sleep(delay_seconds)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            html_text = response.text
            # Save to local cache
            if cache_filename:
                cache_path = os.path.join(HTML_DIR, cache_filename)
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(html_text)
            return html_text, False
        else:
            logging.error(f"HTTP {response.status_code} when fetching {url}")
            return None, False
    except Exception as e:
        logging.error(f"Network error fetching {url}: {e}")
        return None, False


def discover_categories_for_year(year):
    """
    Discover all category ranking links available on the official landing page for a year.
    Returns a list of dicts with category name, link href, and full URL.
    """
    landing_url = YEAR_LANDING_PAGES.get(year)
    if not landing_url:
        logging.warning(f"No landing URL configured for year {year}")
        return []

    cache_file = f"landing_{year}.html"
    html_content, _ = download_html(landing_url, cache_filename=cache_file)
    if not html_content:
        logging.error(f"Could not load landing page for {year}")
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    categories = []
    seen_hrefs = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text().strip()
        h_lower = href.lower()

        # Keep links pointing to category ranking html pages
        if "ranking" in h_lower and not href.startswith("#") and "flipbook" not in h_lower and "report" not in h_lower:
            # Skip self-links to the landing page
            if href in seen_hrefs or href in ["Ranking.html", f"Ranking{year}.html"]:
                continue
            seen_hrefs.add(href)

            full_url = urljoin(landing_url, href)
            # Standardize category name from filename
            cat_name = href.split("/")[-1].replace("Ranking.html", "").replace(".html", "").replace("Ranking", "").strip()
            if not cat_name and text:
                cat_name = text
            
            categories.append({
                "year": year,
                "category": cat_name,
                "href": href,
                "url": full_url
            })

    logging.info(f"Year {year}: Discovered {len(categories)} categories: {[c['category'] for c in categories]}")
    return categories


def clean_institution_name(raw_name):
    """
    Remove extra HTML noise such as 'More Details', 'Close |', parameter texts,
    and multiple whitespace characters from the institution name.
    """
    if not raw_name:
        return ""
    # Split at 'More Details', 'Close', or parameter abbreviations if glued
    cleaned = re.split(r"More Details|Close\s*\||TLR\s*\(", raw_name, flags=re.IGNORECASE)[0]
    # Replace multiple spaces/newlines with single space
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def parse_ranking_table(html_content, year, category, source_url):
    """
    Parse the ranking table from the category HTML page.
    Extracts Institute ID, Name, City, State, Score, Rank, and the 5 parameters.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        return []

    main_table = tables[0]
    records = []

    for tr in main_table.find_all("tr"):
        tds = tr.find_all("td", recursive=False)
        # Standard NIRF ranking rows have 6 direct td cells:
        # [0: Institute ID, 1: Name & Parameter Accordion, 2: City, 3: State, 4: Score, 5: Rank]
        if len(tds) == 6:
            inst_id = tds[0].get_text().strip()
            name_cell = tds[1]
            raw_name = name_cell.get_text()
            inst_name = clean_institution_name(raw_name)

            # Extract the 5 parameters from the nested table inside name_cell
            tlr, rpc, go, oi, perception = None, None, None, None, None
            nested_table = name_cell.find("table")
            if nested_table:
                p_rows = nested_table.find_all("tr")
                if len(p_rows) >= 2:
                    p_headers = [th.get_text().strip().upper() for th in p_rows[0].find_all(["th", "td"])]
                    p_vals = [td.get_text().strip() for td in p_rows[1].find_all(["th", "td"])]
                    for h, v in zip(p_headers, p_vals):
                        if "TLR" in h:
                            tlr = v
                        elif "RPC" in h:
                            rpc = v
                        elif "GO" in h:
                            go = v
                        elif "OI" in h:
                            oi = v
                        elif "PERCEPTION" in h or "PR" in h:
                            perception = v

            city = " ".join(tds[2].get_text().split())
            state = " ".join(tds[3].get_text().split())
            score = tds[4].get_text().strip()
            rank = tds[5].get_text().strip()

            records.append({
                "year": int(year),
                "category": category,
                "institute_id": inst_id,
                "name": inst_name,
                "tlr": tlr,
                "rpc": rpc,
                "go": go,
                "oi": oi,
                "perception": perception,
                "city": city,
                "state": state,
                "score": score,
                "rank": rank,
                "source_url": source_url
            })

    return records


def scrape_category(year, category_info):
    """
    Scrape a single category for a given year.
    Saves parsed records to CSV in data/raw/downloads/.
    """
    cat_name = category_info["category"]
    url = category_info["url"]
    cache_file = f"ranking_{year}_{cat_name}.html"

    logging.info(f"Fetching Year {year} - Category '{cat_name}' from {url}")
    html_content, from_cache = download_html(url, cache_filename=cache_file)
    if not html_content:
        logging.error(f"Failed to obtain HTML for {year} {cat_name}")
        return None

    records = parse_ranking_table(html_content, year, cat_name, url)
    if not records:
        logging.warning(f"No records parsed for {year} {cat_name} (might be empty or report format)")
        return None

    df = pd.DataFrame(records)
    csv_filename = f"nirf_{year}_{cat_name.lower()}.csv"
    csv_path = os.path.join(DOWNLOADS_DIR, csv_filename)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    logging.info(f"Saved {len(df)} records to {csv_path} (from_cache={from_cache})")
    return df


def scrape_all_years(start_year=2017, end_year=2025):
    """
    Main scraping controller. Iterates through all years and categories,
    collects data, saves individual raw CSVs, and logs status.
    """
    ensure_directories_exist()
    all_data = []
    status_summary = []

    for year in range(start_year, end_year + 1):
        logging.info(f"\n==================== PROCESSING YEAR {year} ====================")
        categories = discover_categories_for_year(year)
        if not categories:
            status_summary.append({
                "year": year,
                "status": "Landing page unavailable or no categories found",
                "categories_count": 0,
                "records_collected": 0
            })
            continue

        year_records_count = 0
        for cat_info in categories:
            df = scrape_category(year, cat_info)
            if df is not None and not df.empty:
                all_data.append(df)
                year_records_count += len(df)
                status_summary.append({
                    "year": year,
                    "category": cat_info["category"],
                    "url": cat_info["url"],
                    "status": "Success",
                    "records": len(df)
                })
            else:
                status_summary.append({
                    "year": year,
                    "category": cat_info["category"],
                    "url": cat_info["url"],
                    "status": "No table records found",
                    "records": 0
                })

        logging.info(f"Finished Year {year}: Total {year_records_count} records collected.")

    # Save summary report to JSON
    summary_path = os.path.join("logs", "collection_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(status_summary, f, indent=2)

    total_records = sum(len(df) for df in all_data)
    logging.info(f"\nScraping complete! Total datasets: {len(all_data)}, Total records: {total_records}")
    return all_data


if __name__ == "__main__":
    scrape_all_years(2017, 2025)
