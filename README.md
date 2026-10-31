# NIRF Ranking Analytics Dashboard (2017–2025)
### Data Handling and Visualization (DHV) Project

---

## 📌 1. Project Overview & Objectives
This project is an end-to-end data analytics and interactive dashboard application built from scratch using official NIRF (National Institutional Ranking Framework) ranking data from **2017 through 2025**.

The project fulfills all three levels of the official evaluation brief (`DHV_Project_Statement_B2.pdf`):
- **Level 1 (10 Marks):** Complete implementation of all 40 official sample questions across 8 analytical groups.
- **Level 2 (5 Marks):** Dynamic Analysis Engine allowing ad-hoc exploration, custom scatter plots, correlation coefficients, regression lines, and custom aggregations for unseen questions.
- **Level 3 (5 Marks):** Local Natural Language Query Interface ("Ask NIRF Data") converting conversational questions into data queries and interactive visualizations without paid API keys.

---

## 🏗️ 2. Project Directory Structure
```text
DHV_NIRF_Dashboard/
|-- DHV_Project_Statement_B2.pdf      # Authoritative project requirements
|-- app.py                            # Streamlit interactive dashboard application
|-- requirements.txt                  # Python dependencies
|-- README.md                         # Comprehensive project documentation & defense guide
|-- .gitignore                        # Git ignore file
|
|-- src/                              # Core source code modules (minimal & focused)
|   |-- nirf_scraper.py               # Official web scraper with caching & error handling
|   |-- data_loader.py                # Raw file loader & manual CSV/Excel importer
|   |-- preprocessing.py              # Data cleaning, deduplication, & validation checks
|   |-- analysis.py                   # Core analytical functions (all 40 sample questions)
|   |-- visualizations.py             # Plotly interactive chart generators
|   |-- query_engine.py               # Natural language query engine (parser + executor)
|
|-- data/                             # Data storage (no empty folders)
|   |-- raw/
|   |   |-- html/                     # Cached HTML pages from nirfindia.org (prevents re-fetching)
|   |   |-- downloads/                # 94 raw category CSVs collected by scraper
|   |-- processed/
|       |-- nirf_master.csv           # Cleaned master dataset (6,843 verified records)
|
|-- logs/                             # System logs and reports
|   |-- scraper.log                   # Web scraping logs
|   |-- data_quality_report.json      # Comprehensive data health and statistics report
|   |-- data_collection_catalog.json  # All discovered category URLs across 2017-2025
|
|-- docs/                             # Project documentation
|   |-- data_dictionary.md            # Detailed schema and parameter descriptions
|   |-- data_collection_status.md     # Official URLs and year-by-year collection status
|   |-- sample_question_coverage.md   # Complete matrix mapping all 40 questions to functions
|
|-- tests/                            # Unit test suite (pytest)
    |-- test_preprocessing.py         # Tests for data cleaning, state fixes, rank parsing
    |-- test_analysis.py              # Tests for ranking trends, mobility, correlations
    |-- test_query_engine.py          # Tests for natural language query engine
```

---

## 🗺️ 3. Developer Guide: Which File Should I Edit for Each Feature?

To keep the code clean and easy for every team member to modify, responsibilities are strictly separated. Use this table whenever you want to add, change, or debug a feature:

| If you want to... | Edit this file | What it contains |
|---|---|---|
| **Add a new UI tab, metric card, or page filter** | [`app.py`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/app.py) | Main Streamlit layout, sidebar menus, and user interactions. |
| **Add or modify analytical calculations** (e.g. new ranking logic, stats, filters) | [`src/analysis.py`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/src/analysis.py) | Pure Pandas calculations for all 40 questions; no UI code. |
| **Change how charts look** (colors, axes, tooltips, chart types) | [`src/visualizations.py`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/src/visualizations.py) | Plotly chart definitions; no mathematical logic. |
| **Support new phrasing in the chatbox / NLP query** | [`src/query_engine.py`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/src/query_engine.py) | Rule-based parser & executor for plain-English questions. |
| **Adjust data cleaning rules** (e.g. fix state typos, institution names) | [`src/preprocessing.py`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/src/preprocessing.py) | Data cleaning, deduplication, and data quality checks. |
| **Add support for new raw data formats** (CSV, Excel, custom columns) | [`src/data_loader.py`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/src/data_loader.py) | Functions for reading files into DataFrames. |
| **Scrape newly added years or official ranking pages** | [`src/nirf_scraper.py`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/src/nirf_scraper.py) | Web scraping logic and HTML caching. |
| **Add new automated unit tests** | [`tests/`](file:///c:/Users/hp/OneDrive/Desktop/DHV_PROJECT/tests/) | Pytest test cases for calculations and data pipelines. |

---

## 💻 4. Technology Stack Explained

| Technology | Purpose in Project |
|---|---|
| **Python 3.10+** | Core programming language. Code is written in simple, commented, beginner-friendly style. |
| **Pandas** | High-performance tabular data handling, filtering, pivoting, grouping, and aggregations. |
| **NumPy** | Statistical calculations, polyfit linear regressions, and quantile computations. |
| **Requests & BeautifulSoup4** | Polite HTTP web scraping and HTML table parsing from `nirfindia.org`. |
| **Plotly Express & Graph Objects** | Interactive, responsive data visualizations (line charts, radar charts, box plots, scatter plots). |
| **Streamlit** | Modern, fast interactive web dashboard framework. |
| **OpenPyXL** | Reading and importing manual Excel spreadsheets (`.xlsx`). |
| **Pytest** | Automated unit testing framework for validating calculations and data pipelines. |

---

## 🚀 5. How to Set Up and Run Locally

### Step 1: Open Terminal (Windows PowerShell)
Navigate to your project directory:
```powershell
cd c:\Users\hp\OneDrive\Desktop\DHV_PROJECT
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Web Scraper (Optional - Data is Already Scraped)
The project comes with all 94 datasets already cached and parsed into `data/raw/downloads/`. To re-run or update:
```powershell
python src/nirf_scraper.py
```

### Step 4: Run the Preprocessing Pipeline
To generate the clean master dataset `data/processed/nirf_master.csv` and the data quality audit report:
```powershell
python src/preprocessing.py
```

### Step 5: Run the Automated Unit Tests
Verify all 18 unit tests pass:
```powershell
pytest tests/
```

### Step 6: Launch the Streamlit Dashboard
```powershell
streamlit run app.py
```
The interactive dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## 📊 5. Summary of the Eight Analysis Categories

### 1. Time-Series and Trend Analysis (Q1.1 – Q1.5)
- Tracks individual institutional rank trajectory over time with inverted rank y-axes (Rank 1 at the top).
- Computes rank improvements ($Rank_{start} - Rank_{end}$) and declines.
- Analyzes average score trends and consistency in the Top 10 across years.

### 2. Geospatial and Regional Analysis (Q2.1 – Q2.5)
- Evaluates states with the highest representation in the Top 100.
- Tracks multi-year geographical shifts across Indian States and UTs.
- Features head-to-head state comparisons (e.g., Karnataka vs Tamil Nadu) with boxplots and summaries.
- Identifies newly emerging institutions by state.

### 3. Univariate Analysis (Q3.1 – Q3.5)
- Distribution histograms with marginal box plots for scores and ranks.
- Descriptive statistics: Mean, Median, Min, Max, and Standard Deviation.
- Score quartile classification (Q1 to Q4).
- Category score spread comparisons.

### 4. Bivariate Analysis and Correlation (Q4.1 – Q4.5)
- Pearson correlation coefficient ($r$) calculation between parameters and overall scores.
- Scatter plots with linear regression trendlines ($y = mx + c$).
- Evolution of research correlation from 2017 to 2025.
- **Select-Two-Variables Dynamic Explorer** allowing users to pick any two variables and immediately generate a scatter plot and regression line.

### 5. Multivariate Analysis (Q5.1 – Q5.5)
- Radar (spider) charts comparing Top 5 institutions across all 5 parameters: TLR, RPC, GO, OI, Perception.
- Detection of institutional trade-offs: High Research / Low Teaching, and High Teaching / Low Perception.
- Identification of largest parameter gaps ($\max - \min$).

### 6. Distribution and Statistical Comparison (Q6.1 – Q6.5)
- Boxplot comparison of Top 10 institutions versus the remaining institutions.
- Multi-year score dispersion analysis using Variance and Interquartile Range (IQR).
- Parameter variability ranking using the Coefficient of Variation ($CV = \frac{\sigma}{\mu} \times 100\%$).
- State-wise score distributions.

### 7. Ranking Transitions and Institutional Mobility (Q7.1 – Q7.5)
- Tracking institutions transitioning from the 51–100 band into the Top 50.
- Top 10 entrant and exit accounting between consecutive years.
- Rank band retention rates across Top 10, 11–50, and 51–100.
- Donut charts summarizing institutional mobility (Moved Up, Moved Down, Retained Position).

### 8. Outlier Detection and Performance Gaps (Q8.1 – Q8.5)
- Regression residual outliers: institutions with unusually high research output relative to their score.
- Research vs Teaching gap outliers ($RPC - TLR$).
- Year-to-year score change outliers using Z-scores ($|Z| \ge 2.0$).
- Institutional ranking volatility measured via the Standard Deviation of rank across years.

---

## 💬 6. Level 3 Natural-Language Query Flow
The "Ask NIRF Data" module uses a rule-based Natural Language Processing (NLP) pipeline:
1. **User Input:** Plain English question (e.g., *"Which states have the most Engineering institutions in the top 100 in 2025?"*).
2. **Entity Extraction (`src/query_engine.py`):**
   - Identifies years (`2025`), categories (`Engineering`), states (`Tamil Nadu`), parameters (`TLR`, `RPC`), institutions (`IIT Madras`).
3. **Intent Recognition:**
   - Maps phrasing to safe analytical plans (`top_states`, `institution_trend`, `two_var_correlation`, `band_to_top50`, etc.).
4. **Execution & Visualization (`src/query_engine.py`):**
   - Executes the corresponding Pandas function in `src/analysis.py`.
   - Renders a custom Plotly chart and returns a clear, textual summary answering the question.

---

## 🎓 7. How to Explain the Project During Evaluation (Viva Guide)

When presenting this project to your professor or evaluator, use these structured points:

1. **Where did you get the data?**
   > *"We scraped official NIRF ranking pages from `nirfindia.org` covering all years from 2017 to 2025. We saved the raw HTML pages in `data/raw/html/` to maintain source provenance, polite access, and reproducibility. The final cleaned dataset contains 6,843 real records across 13 standardized categories."*

2. **How did you clean the data?**
   > *"In `src/preprocessing.py`, we cleaned institutional names by stripping nested HTML buttons (e.g. 'More Details'), standardized state names (e.g., mapping 'Tamilnadu' and 'New Delhi' to standard states), parsed numeric ranks while preserving rank bands (e.g., 101–150), and ensured numerical fields are valid numbers between 0 and 100 without inventing fake zeros."*

3. **How does Level 2 Dynamic Analysis work?**
   > *"In Level 2, instead of hardcoding charts, the user can select any combination of variables on the X and Y axes, choose a grouping factor, apply sliders for years and ranks, and select chart types. The engine calculates correlations, regression slopes, and aggregations dynamically."*

4. **How does the Natural Language Query (Level 3) work without an API key?**
   > *"We built a local rule-based entity and intent parser in `src/query_engine.py`. It extracts years, categories, institutions, and metrics using regular expressions and keyword matching, and safely routes them to tested functions in `analysis.py` and `visualizations.py`."*
