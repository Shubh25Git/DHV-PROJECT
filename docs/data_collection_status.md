# NIRF Ranking Data Collection Status (2017–2025)

## 1. Overview
This document records the exact status of data collection from the official National Institutional Ranking Framework (NIRF) website ([https://www.nirfindia.org/](https://www.nirfindia.org/)).

- **Collection Date:** October 2026
- **Source Website:** [https://www.nirfindia.org](https://www.nirfindia.org)
- **Years Target:** 2017 to 2025 (9 consecutive years)
- **Total Datasets Collected:** 94 category-year CSV files
- **Total Real Records Extracted:** 6,924 records

---

## 2. Year-wise Collection Summary

| Year | Landing Page URL | Categories Available | Categories Successfully Extracted | Total Records Extracted |
|------|------------------|----------------------|-----------------------------------|-------------------------|
| **2017** | `https://www.nirfindia.org/Rankings/2017/Ranking2017.html` | 6 | 6 (Overall, Engineering, Management, University, College, Pharmacy) | 500 |
| **2018** | `https://www.nirfindia.org/Rankings/2018/Ranking2018.html` | 10 | 9 (Overall, University, Engineering, College, Management, Pharmacy, Medical, Architecture, Law) | 545 |
| **2019** | `https://www.nirfindia.org/Rankings/2019/Ranking2019.html` | 9 | 9 (Overall, University, Engineering, College, Management, Pharmacy, Law, Architecture, Medical) | 710 |
| **2020** | `https://www.nirfindia.org/Rankings/2020/Ranking2020.html` | 10 | 10 (Overall, University, Engineering, Management, Pharmacy, College, Medical, Law, Architecture, Dental) | 761 |
| **2021** | `https://www.nirfindia.org/Rankings/2021/Ranking.html` | 11 | 11 (Overall, University, Engineering, Management, Pharmacy, College, Medical, Law, Architecture, Dental, Research) | 845 |
| **2022** | `https://www.nirfindia.org/Rankings/2022/Ranking.html` | 11 | 11 (Overall, University, College, Research, Engineering, Management, Pharmacy, Medical, Dental, Law, Architecture) | 902 |
| **2023** | `https://www.nirfindia.org/Rankings/2023/Ranking.html` | 13 | 12 (Overall, University, College, Research, Engineering, Management, Pharmacy, Medical, Dental, Law, Architecture, Agriculture) | 840 |
| **2024** | `https://www.nirfindia.org/Rankings/2024/Ranking.html` | 16 | 13 (Overall, University, College, Research, Engineering, Management, Pharmacy, Medical, Dental, Law, Architecture, Agriculture, State Public University) | 910 |
| **2025** | `https://www.nirfindia.org/Rankings/2025/Ranking.html` | 17 | 13 (Overall, University, College, Research, Engineering, Management, Pharmacy, Medical, Dental, Law, Architecture, Agriculture, State Public University) | 911 |
| **Total**| - | - | **94 datasets** | **6,924 records** |

---

## 3. Extracted Fields per Record
Every extracted record from the ranking tables contains:
1. `year`: Ranking year (2017–2025)
2. `category`: Normalized ranking discipline (e.g., Overall, Engineering, University, etc.)
3. `institute_id`: Official NIRF institute identifier (e.g., `IR-O-U-0456`)
4. `name`: Cleaned name of the higher educational institution
5. `city`: City where the institution is located
6. `state`: State or Union Territory of the institution
7. `score`: Overall NIRF weighted score (0–100 scale)
8. `rank`: Official integer rank or rank band
9. `tlr`: Teaching, Learning and Resources score (0–100)
10. `rpc`: Research and Professional Practice score (0–100)
11. `go`: Graduation Outcomes score (0–100)
12. `oi`: Outreach and Inclusivity score (0–100)
13. `perception`: Peer & Employer Perception score (0–100)
14. `source_url`: Exact official webpage URL from which data was retrieved

---

## 4. Notable Category Notes and Limitations
1. **Evolution of Categories:** In 2017, NIRF ranked only 6 categories. By 2025, 17 categories existed.
2. **Report / Non-Table Categories:** Certain newer categories such as `Innovation` (earlier ARIIA), `Open University`, `Skill University`, and `SDG Institutions` publish PDF flipbooks or reports rather than HTML ranking tables. These were detected by the scraper and documented as non-table categories.
3. **Manual Import Fallback:** The project provides a manual import pipeline in `src/data_loader.py` and via the Streamlit UI to easily add any custom or additional category files.
4. **Data Verification:** Every single collected record comes from official HTML pages cached in `data/raw/html/` and parsed CSV files in `data/raw/downloads/`. No synthetic records or placeholders are mixed into the ranking dataset.
