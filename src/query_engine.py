"""
Natural Language Query Engine (Level 3)
========================================
This module combines query parsing and execution into a single, cohesive file.
It accepts natural language questions, extracts entities and analytical intent,
executes verified functions from analysis.py, and returns interactive Plotly charts.

Key Features:
- 100% local rule-based processing (no external or paid API key needed).
- Completely safe execution: no dynamic eval() or raw SQL.
- Extracts: years, categories, institutions, states, parameters.
- Generates: Plotly chart, textual summary, and structured underlying data.
"""

import re
import pandas as pd
import numpy as np

import src.analysis as analysis
import src.visualizations as viz

# Supported Categories
CATEGORIES = [
    "overall", "engineering", "management", "university", "college",
    "pharmacy", "medical", "dental", "law", "architecture", "agriculture",
    "research", "state public university"
]

# Supported Parameters
PARAMETERS = {
    "tlr": "tlr",
    "teaching": "tlr",
    "rpc": "rpc",
    "research": "rpc",
    "go": "go",
    "graduation": "go",
    "oi": "oi",
    "outreach": "oi",
    "perception": "perception",
    "pr": "perception",
    "score": "score",
    "rank": "rank"
}

# Supported States
STATES = [
    "andhra pradesh", "assam", "bihar", "chandigarh", "chhattisgarh", "delhi",
    "goa", "gujarat", "haryana", "himachal pradesh", "jammu and kashmir",
    "jharkhand", "karnataka", "kerala", "madhya pradesh", "maharashtra",
    "odisha", "puducherry", "punjab", "rajasthan", "tamil nadu",
    "telangana", "uttar pradesh", "uttarakhand", "west bengal"
]


# ==============================================================================
# Part 1: Rule-Based Entity Extraction & Intent Parsing
# ==============================================================================

def extract_years(text):
    """Extract 4-digit years between 2016 and 2026 mentioned in text."""
    years = [int(y) for y in re.findall(r"\b(201[6-9]|202[0-6])\b", text)]
    return sorted(list(set(years)))


def extract_category(text):
    """Identify if a specific ranking category is explicitly mentioned in text."""
    text_lower = text.lower()
    for cat in CATEGORIES:
        if re.search(r"\b" + re.escape(cat) + r"\b", text_lower):
            return cat.title()
    return None


def extract_states(text):
    """Find Indian states mentioned in text."""
    text_lower = text.lower()
    found_states = []
    for state in STATES:
        pattern = r"\b" + re.escape(state) + r"\b"
        if re.search(pattern, text_lower):
            found_states.append(state.title())
    return found_states


def extract_parameters(text):
    """Identify NIRF parameter keywords mentioned in text."""
    text_lower = text.lower()
    found_params = []
    for keyword, param in PARAMETERS.items():
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            if param not in found_params:
                found_params.append(param)
    return found_params


# Expanded shorthand aliases for Indian universities, IITs, IIMs, NITs, and institutes
INSTITUTION_ALIASES = {
    "iit indore": "Indian Institute of Technology Indore",
    "iit madras": "Indian Institute of Technology Madras",
    "iit bombay": "Indian Institute of Technology Bombay",
    "iit delhi": "Indian Institute of Technology Delhi",
    "iit kanpur": "Indian Institute of Technology Kanpur",
    "iit kharagpur": "Indian Institute of Technology Kharagpur",
    "iit roorkee": "Indian Institute of Technology Roorkee",
    "iit guwahati": "Indian Institute of Technology Guwahati",
    "iit hyderabad": "Indian Institute of Technology Hyderabad",
    "iit bhu": "Indian Institute of Technology (BHU) Varanasi",
    "iit varanasi": "Indian Institute of Technology (BHU) Varanasi",
    "iit gandhinagar": "Indian Institute of Technology Gandhinagar",
    "iit ropar": "Indian Institute of Technology Ropar",
    "iit patna": "Indian Institute of Technology Patna",
    "iit mandi": "Indian Institute of Technology Mandi",
    "iit jodhpur": "Indian Institute of Technology Jodhpur",
    "iit bhubaneswar": "Indian Institute of Technology Bhubaneswar",
    "iit tirupati": "Indian Institute of Technology Tirupati",
    "iit palakkad": "Indian Institute of Technology Palakkad",
    "iit dharwad": "Indian Institute of Technology Dharwad",
    "iit bhilai": "Indian Institute of Technology Bhilai",
    "iit goa": "Indian Institute of Technology Goa",
    "iit jammu": "Indian Institute of Technology Jammu",
    "iit ism": "Indian Institute of Technology (Indian School of Mines), Dhanbad",
    "iit dhanbad": "Indian Institute of Technology (Indian School of Mines), Dhanbad",
    "iisc": "Indian Institute of Science",
    "iisc bangalore": "Indian Institute of Science",
    "iisc bengaluru": "Indian Institute of Science",
    "miranda house": "Miranda House",
    "aiims": "All India Institute of Medical Sciences",
    "aiims new delhi": "All India Institute of Medical Sciences, New Delhi",
    "jnu": "Jawaharlal Nehru University",
    "manipal": "Manipal Academy of Higher Education",
    "bits pilani": "Birla Institute of Technology & Science - Pilani",
    "bhu": "Banaras Hindu University",
    "du": "University of Delhi",
    "delhi university": "University of Delhi",
    "anna university": "Anna University",
    "jadavpur university": "Jadavpur University",
}


def resolve_single_institution(cand, known_institutions=None):
    """
    Resolves a raw candidate institution string against aliases and known institutions.
    Returns: (canonical_or_extracted_name, matched_canonical_name_or_None)
    """
    cand = cand.strip()
    cand = re.sub(r"^(the|an|a)\s+", "", cand, flags=re.IGNORECASE).strip()
    cand_clean = re.sub(r"[\?\.!,]", "", cand.lower()).strip()

    # 1. Alias map check
    for alias, canonical in INSTITUTION_ALIASES.items():
        if alias == cand_clean or re.search(r"\b" + re.escape(alias) + r"\b", cand_clean):
            if known_institutions:
                matches = [k for k in known_institutions if canonical.lower() in k.lower()]
                matched = matches[0] if matches else canonical
                return matched, matched
            return canonical, canonical

    # 2. Known institutions full-name match (longest first)
    if known_institutions:
        sorted_known = sorted(known_institutions, key=lambda x: len(str(x)), reverse=True)
        for inst in sorted_known:
            if len(str(inst)) >= 4 and (cand_clean == str(inst).lower() or str(inst).lower() in cand_clean):
                return inst, inst

    # 3. Acronym expansion
    expanded = cand_clean
    expanded = re.sub(r"\biit\s+([a-z]+)\b", r"indian institute of technology \1", expanded)
    expanded = re.sub(r"\biim\s+([a-z]+)\b", r"indian institute of management \1", expanded)
    expanded = re.sub(r"\bnit\s+([a-z]+)\b", r"national institute of technology \1", expanded)
    expanded = re.sub(r"\biiit\s+([a-z]+)\b", r"indian institute of information technology \1", expanded)

    if known_institutions:
        for inst in sorted_known:
            if len(str(inst)) >= 4 and (expanded == str(inst).lower() or str(inst).lower() in expanded):
                return inst, inst

    # 4. Substring match
    if known_institutions and len(cand_clean) >= 4:
        for inst in sorted_known:
            if cand_clean in inst.lower():
                return inst, inst

    return cand, None


def extract_institutions(text, known_institutions=None):
    """
    Extracts all institution names mentioned in the question.
    Returns: (list_of_extracted_names, list_of_matched_canonical_names_or_None)
    """
    text_clean = text.strip()
    stopwords = {
        "institution", "institutions", "first", "top 10", "top 5", "top 100",
        "college", "colleges", "university", "engineering", "overall",
        "state", "states", "score", "scores", "rank", "ranks", "ranking",
        "parameter", "parameters", "tlr", "rpc", "go", "oi", "perception",
        "teaching", "research", "graduation", "outreach"
    }
    param_words = {"tlr", "rpc", "go", "oi", "perception", "score", "scores", "teaching", "research", "graduation", "outreach", "parameter", "parameters"}

    # 1. Comparison clause pattern matching (support 2, 3, or more institutions)
    clause_pat = r"(?:compare|comparison\s+(?:of|between)|difference\s+between|diff\s+between)\s+(.+?)(?:\s+in\b|\s+for\b|\s+from\b|\?|$|\.)"
    m = re.search(clause_pat, text_clean, re.IGNORECASE)
    if m:
        raw_clause = m.group(1).strip()
        parts = re.split(r",\s*(?:and\s+)?|\s+(?:and|versus|\bvs\b|\bvs\.\b)\s+", raw_clause, flags=re.IGNORECASE)
        cand_list = [p.strip() for p in parts if p.strip()]

        # Ensure this clause is not comparing parameters or states
        has_param_in_clause = any(any(pw in re.sub(r"[^\w\s]", "", c.lower()).split() for pw in param_words) for c in cand_list)
        has_state_in_clause = any(c.lower() in [s.lower() for s in STATES] for c in cand_list)

        if not has_param_in_clause and not has_state_in_clause and len(cand_list) >= 2:
            insts = []
            matches = []
            for c in cand_list:
                c_clean = re.sub(r"^(the|an|a)\s+", "", c, flags=re.IGNORECASE).strip()
                if c_clean.lower() not in stopwords and len(c_clean) >= 2:
                    r_name, r_match = resolve_single_institution(c_clean, known_institutions)
                    insts.append(r_name)
                    matches.append(r_match)
            if len(insts) >= 2:
                return insts, matches

    # Also handle 'A vs B vs C' pattern outside of 'compare' clause
    vs_pat = r"([A-Za-z0-9\s,.-]+?)\s+(?:versus|\bvs\b|\bvs\.\b)\s+([A-Za-z0-9\s,.-]+?)(?:\s+in\b|\s+for\b|\s+from\b|\?|$|\.)"
    m_vs = re.search(vs_pat, text_clean, re.IGNORECASE)
    if m_vs:
        c1, c2 = m_vs.group(1).strip(), m_vs.group(2).strip()
        c1_clean = re.sub(r"^(the|an|a)\s+", "", c1, flags=re.IGNORECASE).strip()
        c2_clean = re.sub(r"^(the|an|a)\s+", "", c2, flags=re.IGNORECASE).strip()
        if c1_clean.lower() not in stopwords and c2_clean.lower() not in stopwords and len(c1_clean) >= 2 and len(c2_clean) >= 2:
            r1_name, r1_match = resolve_single_institution(c1_clean, known_institutions)
            r2_name, r2_match = resolve_single_institution(c2_clean, known_institutions)
            if r1_match or r2_match:
                return [r1_name, r2_name], [r1_match, r2_match]

    # 2. Alias occurrences with start index (preserves text order)
    found = []
    text_lower = text.lower()
    for alias, canonical in INSTITUTION_ALIASES.items():
        for m_alias in re.finditer(r"\b" + re.escape(alias) + r"\b", text_lower):
            matched = canonical
            if known_institutions:
                matches = [k for k in known_institutions if canonical.lower() in k.lower()]
                matched = matches[0] if matches else canonical
            found.append((m_alias.start(), m_alias.end(), matched, matched))

    # 3. Known institutions full-name match
    if known_institutions:
        sorted_known = sorted(known_institutions, key=lambda x: len(str(x)), reverse=True)
        for inst in sorted_known:
            if len(str(inst)) >= 4:
                for m_inst in re.finditer(r"\b" + re.escape(str(inst).lower()) + r"\b", text_lower):
                    found.append((m_inst.start(), m_inst.end(), inst, inst))

    if found:
        found.sort(key=lambda x: x[0])
        insts = []
        matches = []
        for _, _, iname, imatch in found:
            if iname not in insts:
                insts.append(iname)
                matches.append(imatch)
        return insts, matches

    # 4. Regex extraction for candidate institution name (single)
    patterns = [
        r"(?:rank|ranking|standing|position|trajectory)\s+(?:of|for)\s+([A-Za-z0-9\s,.-]+?)(?:\s+in\b|\s+for\b|\s+from\b|\s+over\b|\?|$|\.)",
        r"(?:where\s+does|how\s+does)\s+([A-Za-z0-9\s,.-]+?)\s+rank",
        r"(?:what\s+is\s+(?:the\s+)?(?:current\s+)?rank\s+of)\s+([A-Za-z0-9\s,.-]+?)(?:\s+in\b|\?|$|\.)",
        r"(?:what\s+was|what\s+is)\s+([A-Za-z0-9\s,.-]+?)(?:'s|’s)?\s+(?:best|highest|peak)\s+rank",
        r"(?:did|has)\s+([A-Za-z0-9\s,.-]+?)\s+(?:improve|drop|decline)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            cand = m.group(1).strip()
            cand = re.sub(r"^(the|an|a)\s+", "", cand, flags=re.IGNORECASE).strip()
            cand = re.sub(r"('s|’s)$", "", cand).strip()
            if cand.lower() not in stopwords and len(cand) >= 2:
                r_name, r_match = resolve_single_institution(cand, known_institutions)
                return [r_name], [r_match]

    return [], []


def extract_institution(text, known_institutions=None):
    """
    Extract institution names mentioned in the question.
    Returns: (extracted_or_canonical_name, matched_canonical_name_or_None)
    """
    insts, matches = extract_institutions(text, known_institutions)
    if insts:
        return insts[0], matches[0]
    return None, None


def parse_query(question, known_institutions=None, default_category=None, default_year=None, max_year=2025):
    """
    Translates a plain-English question into a structured query plan.
    """
    q = question.strip()
    q_lower = q.lower()

    explicit_years = extract_years(q)
    has_current = bool(re.search(r"\b(current|latest|present|now|recent|currently)\b", q_lower))
    is_historical_rank_status = bool(re.search(
        r"\b(ever\s+lose|ever\s+lost|ever\s+drop(?:ped)?|ever\s+f[ae]ll|ever\s+slip(?:ped)?|ever\s+held?|remain(?:ed)?\s+(?:at|ranked)?|stay(?:ed)?\s+(?:at|ranked)?|consistently\s+(?:ranked|held|at)|always\s+(?:ranked|held|at))\b",
        q_lower
    ))
    is_historical_milestone = bool(re.search(r"\b(in which year|which year|when did|when was|what year|first year|earliest year|first reach|first reached|first enter|first entered|first ranked?|enter(?:ed)? the top|reach(?:ed)? the top)\b", q_lower))
    is_trend = any(w in q_lower for w in ["trend", "trajectory", "changed", "over time", "history", "years", "evolution"]) or bool(re.search(r"\bfrom\s+\d{4}\s+to\s+\d{4}\b", q_lower))
    is_comparison = bool(re.search(r"\b(compare|comparison|versus|\bvs\b|\bvs\.\b|difference\s+between|diff\s+between)\b", q_lower))
    is_best_rank = bool(re.search(r"\b(best\s+rank|highest\s+rank|peak\s+rank|top\s+rank\s+achieved|lowest\s+rank\s+number)\b", q_lower))
    is_progression = bool(re.search(
        r"\b(improve(?:d)?\s+(?:its\s+)?rank\s+every\s+year|rank\s+improve(?:d)?\s+every\s+year|improve\s+every\s+year|improve\s+or\s+decline|years\s+did\s+.+?\s+(?:improve|decline)|year\s+(?:by|on)\s+year\s+rank|consecutive\s+years?)\b",
        q_lower
    ))

    # Target rank and mode for milestone and rank status queries (e.g. "top 10", "top 5", "rank #1")
    target_rank = None
    target_mode = "exact"
    if is_historical_milestone or is_historical_rank_status:
        top_n_match = re.search(r'\btop\s+(\d+)\b', q_lower)
        exact_rank_match = re.search(r'(?:rank(?:ed)?\s*#?|#\s*)(\d+)\b', q_lower)
        is_rank_1_synonym = bool(re.search(r'\b(number\s+one|no\.?\s*1|ranked?\s+first|first\s+position|first\s+place)\b', q_lower)) or bool(re.search(r'\bfirst\s+rank\b', q_lower))

        if top_n_match:
            target_mode = "threshold"
            target_rank = int(top_n_match.group(1))
        elif exact_rank_match:
            target_mode = "exact"
            target_rank = int(exact_rank_match.group(1))
        elif is_rank_1_synonym:
            target_mode = "exact"
            target_rank = 1
        else:
            target_mode = "exact"
            target_rank = 1

    explicit_cat = extract_category(q)
    category = explicit_cat or default_category or "Overall"

    states = extract_states(q)
    params = extract_parameters(q)
    institutions, matched_institutions = extract_institutions(q, known_institutions)
    institution = institutions[0] if institutions else None
    matched_institution = matched_institutions[0] if matched_institutions else None

    # Intent determination with strict precedence hierarchy
    if is_historical_rank_status and institution:
        intent = "historical_rank_status"
    elif is_historical_milestone and institution:
        intent = "historical_milestone"
    elif is_comparison and len(params) >= 2 and len(institutions) <= 1:
        intent = "parameter_comparison"
    elif is_best_rank and institution:
        intent = "best_rank"
    elif is_progression and institution:
        intent = "rank_progression"
    elif institution and is_trend:
        intent = "institution_trend"
    elif is_comparison:
        if len(states) >= 2 or ("state" in q_lower and len(states) >= 1):
            intent = "compare_states"
        elif len(institutions) >= 2:
            intent = "institution_comparison"
        else:
            intent = "institution_comparison"
    elif institution:
        intent = "institution_rank"
    elif is_trend:
        if "correlation" in q_lower:
            intent = "correlation_trend"
        elif "average" in q_lower or "score" in q_lower:
            intent = "score_trend"
        else:
            intent = "score_trend"

    elif any(w in q_lower for w in ["improvement", "improved", "climbed", "gained"]):
        if "state" in q_lower or "representation" in q_lower:
            intent = "state_growth"
        else:
            intent = "biggest_improvements"

    elif any(w in q_lower for w in ["decline", "dropped", "fell", "worsened"]):
        intent = "biggest_declines"

    elif any(w in q_lower for w in ["consistent", "consistently in the top", "stayed"]):
        intent = "consistent_top"

    elif any(w in q_lower for w in ["compare", "comparison"]):
        if len(states) >= 2 or ("state" in q_lower and len(states) >= 1):
            intent = "compare_states"
        else:
            intent = "compare_institutions"

    elif any(w in q_lower for w in ["state", "states", "geographical", "region"]):
        if len(states) >= 2 or "compare" in q_lower:
            intent = "compare_states"
        elif "new" in q_lower or "newly" in q_lower:
            intent = "newly_appearing_states"
        else:
            intent = "top_states"

    elif any(w in q_lower for w in ["correlation", "associated", "related", "relationship"]):
        if len(params) >= 2:
            intent = "two_var_correlation"
        elif "rpc" in q_lower or "research" in q_lower:
            intent = "rpc_correlation"
        elif "perception" in q_lower:
            intent = "perception_correlation"
        elif "tlr" in q_lower:
            intent = "tlr_rpc_relation"
        else:
            intent = "all_parameters_correlation"

    elif any(w in q_lower for w in ["distribution", "histogram", "spread", "quartile"]):
        if "quartile" in q_lower:
            intent = "score_quartiles"
        elif "category" in q_lower or "categories" in q_lower:
            intent = "score_spread_categories"
        elif "top 10" in q_lower or "remaining" in q_lower:
            intent = "top10_vs_rest"
        else:
            intent = "score_distribution"

    elif any(w in q_lower for w in ["outlier", "unusually", "gap", "better in research", "volatility"]):
        if "volatility" in q_lower or "volatile" in q_lower:
            intent = "rank_volatility"
        elif "teaching" in q_lower and "research" in q_lower:
            intent = "research_teaching_gap"
        elif "score change" in q_lower:
            intent = "score_change_outliers"
        elif "poor rank" in q_lower:
            intent = "strong_param_poor_rank"
        else:
            intent = "research_outliers"

    elif any(w in q_lower for w in ["transition", "moved from", "enter", "exit", "retained", "mobility"]):
        if "51-100" in q_lower or "top 50" in q_lower:
            intent = "band_to_top50"
        elif "top 10" in q_lower:
            intent = "top10_entries_exits"
        elif "retained" in q_lower or "percentage" in q_lower:
            intent = "band_retention"
        else:
            intent = "mobility_summary"

    elif any(w in q_lower for w in ["top 10", "top 5", "top 100", "top institutions", "highest score", "leader", "ranked first", "rank 1", "first in"]):
        intent = "top_institutions"

    # Year determination logic
    if explicit_years and intent not in ["historical_milestone", "historical_rank_status", "best_rank", "rank_progression", "institution_trend"]:
        primary_year = explicit_years[-1]
        start_year = explicit_years[0] if len(explicit_years) > 1 else 2017
        end_year = explicit_years[-1] if len(explicit_years) > 1 else primary_year
        year_mode = "explicit"
    elif has_current and intent not in ["historical_milestone", "historical_rank_status", "best_rank", "rank_progression", "institution_trend"]:
        primary_year = max_year
        start_year = 2017
        end_year = max_year
        year_mode = "current"
    elif intent in ["historical_milestone", "historical_rank_status", "best_rank", "rank_progression", "institution_trend"] or is_trend:
        primary_year = None
        start_year = explicit_years[0] if len(explicit_years) > 1 else 2017
        end_year = explicit_years[-1] if len(explicit_years) > 1 else max_year
        year_mode = "full_history"
    elif default_year:
        primary_year = int(default_year)
        start_year = 2017
        end_year = int(default_year)
        year_mode = "default"
    else:
        primary_year = max_year
        start_year = 2017
        end_year = max_year
        year_mode = "default_latest"

    return {
        "original_query": q,
        "intent": intent,
        "category": category,
        "category_explicit": bool(explicit_cat),
        "years": explicit_years,
        "primary_year": primary_year,
        "start_year": start_year,
        "end_year": end_year,
        "year_mode": year_mode,
        "states": states,
        "parameters": params,
        "institution": institution,
        "matched_institution": matched_institution,
        "institutions": institutions,
        "matched_institutions": matched_institutions,
        "target_rank": target_rank,
        "target_mode": target_mode,
        "limit": 10,
    }


# ==============================================================================
# Part 2: Query Execution & Visualization Dispatcher
# ==============================================================================

def execute_query(query_plan, df_master):
    """
    Executes a structured query plan against the cleaned master dataset.
    Returns: {"figure": PlotlyFig, "summary_text": str, "data": DataFrame, "intent": str}
    """
    intent = query_plan.get("intent", "general_overview")
    cat = query_plan.get("category", "Overall")
    year = query_plan.get("primary_year")
    start_year = query_plan.get("start_year", 2017)
    end_year = query_plan.get("end_year", 2025)
    max_dataset_year = int(df_master["year"].max()) if not df_master.empty else 2025
    if year is None:
        year = max_dataset_year

    institution = query_plan.get("institution")
    matched_institution = query_plan.get("matched_institution")
    institutions = query_plan.get("institutions", [institution] if institution else [])
    matched_institutions = query_plan.get("matched_institutions", [matched_institution] if matched_institution else [])
    states = query_plan.get("states", [])
    params = query_plan.get("parameters", [])
    year_mode = query_plan.get("year_mode", "explicit")

    # 0a. Historical Rank Status Query (e.g. "Did IIT Madras ever lose its #1 position in Engineering?")
    if intent == "historical_rank_status":
        if not matched_institution:
            return {
                "figure": None,
                "summary_text": f"Institution **'{institution}'** was not found in the NIRF dataset. Please check the spelling or search for another institution.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        target_rank = query_plan.get("target_rank", 1) or 1
        target_mode = query_plan.get("target_mode", "exact")
        q_text = query_plan.get("original_query", "").lower()
        is_lose_query = bool(re.search(r'\b(lose|lost|drop(?:ped)?|f[ae]ll|slip(?:ped)?)\b', q_text))

        inst_records = df_master[(df_master["name"] == matched_institution) & (df_master["category"].str.lower() == cat.lower())].sort_values(by="year")

        if inst_records.empty:
            other_cats = df_master[df_master["name"] == matched_institution]["category"].unique().tolist()
            cats_msg = f" (ranked in: {', '.join(other_cats)})" if other_cats else ""
            return {
                "figure": None,
                "summary_text": f"**{matched_institution}** has no ranking records in the **{cat}** category{cats_msg} across 2017–{end_year}.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        all_years = sorted(df_master["year"].unique().tolist())
        year_to_rank = {int(r["year"]): (int(r["rank"]) if pd.notna(r["rank"]) and r["rank"] == int(r["rank"]) else r["rank"]) for _, r in inst_records.iterrows()}

        def meets(y):
            if y not in year_to_rank:
                return False
            return (year_to_rank[y] <= target_rank) if target_mode == "threshold" else (year_to_rank[y] == target_rank)

        satisfied_years = [y for y in all_years if meets(y)]
        lost_years = [y for y in all_years if y in year_to_rank and not meets(y)]
        unranked_years = [y for y in all_years if y not in year_to_rank]

        rank_label = f"top {target_rank}" if target_mode == "threshold" else f"#{target_rank}"

        if len(satisfied_years) == len(all_years):
            if is_lose_query:
                direct_ans = f"No. **{matched_institution}** remained ranked **{rank_label}** in **{cat}** from {all_years[0]} through {all_years[-1]}."
            else:
                direct_ans = f"Yes. **{matched_institution}** remained ranked **{rank_label}** in **{cat}** continuously from {all_years[0]} through {all_years[-1]}."

            summary = (
                f"{direct_ans}\n\n"
                f"- It held **{rank_label}** across all **{len(all_years)}** NIRF ranking cycles ({all_years[0]} to {all_years[-1]}).\n"
                f"- It has never dropped below {rank_label} in {cat}."
            )
        elif len(satisfied_years) == 0:
            best_row = inst_records.sort_values(by="rank").iloc[0]
            best_rank = int(best_row["rank"]) if pd.notna(best_row["rank"]) and best_row["rank"] == int(best_row["rank"]) else best_row["rank"]
            best_year = int(best_row["year"])
            summary = (
                f"**{matched_institution}** has never held **{rank_label}** in the **{cat}** category across 2017 to {end_year}.\n\n"
                f"- Its highest rank achieved to date in **{cat}** is **#{best_rank}** in **{best_year}** (overall score: **{best_row['score']:.2f}**)."
            )
        else:
            lost_details = [f"- **{y}**: Rank **#{year_to_rank[y]}**" for y in lost_years]
            if unranked_years:
                lost_details.extend([f"- **{y}**: Unranked" for y in unranked_years])
            lost_str = "\n".join(lost_details)

            sat_years_str = f"{satisfied_years[0]} to {satisfied_years[-1]}" if len(satisfied_years) > 2 and satisfied_years == list(range(satisfied_years[0], satisfied_years[-1] + 1)) else ", ".join(str(y) for y in satisfied_years)

            if is_lose_query:
                direct_ans = f"Yes. **{matched_institution}** lost its **{rank_label}** position in **{cat}**."
            else:
                direct_ans = f"No. **{matched_institution}** did not consistently remain at **{rank_label}** in **{cat}**."

            summary = (
                f"{direct_ans}\n\n"
                f"While it held **{rank_label}** in {sat_years_str}, it was not ranked at {rank_label} in the following year(s):\n"
                f"{lost_str}"
            )

        trend_df = analysis.get_institution_rank_trend(df_master, matched_institution, category=cat)
        fig = viz.plot_institution_rank_trend(trend_df, matched_institution) if not trend_df.empty else None
        data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
        existing_cols = [c for c in data_cols if c in inst_records.columns]
        return {
            "figure": fig,
            "summary_text": summary,
            "data": inst_records[existing_cols].sort_values(by="year").reset_index(drop=True),
            "intent": intent,
        }

    # 0b. Historical Milestone Query (e.g. "In which year did IIT Madras first rank #1 in Engineering?")
    if intent == "historical_milestone":
        if not matched_institution:
            return {
                "figure": None,
                "summary_text": f"Institution **'{institution}'** was not found in the NIRF dataset. Please check the spelling or search for another institution.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        target_rank = query_plan.get("target_rank", 1) or 1
        target_mode = query_plan.get("target_mode", "exact")
        inst_records = df_master[(df_master["name"] == matched_institution) & (df_master["category"].str.lower() == cat.lower())]

        if inst_records.empty:
            other_cats = df_master[df_master["name"] == matched_institution]["category"].unique().tolist()
            cats_msg = f" (ranked in: {', '.join(other_cats)})" if other_cats else ""
            return {
                "figure": None,
                "summary_text": f"**{matched_institution}** has no ranking records in the **{cat}** category{cats_msg} across 2017–{end_year}.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        # Filter by target rank or top-N threshold across all available years (2017-2025)
        if target_mode == "threshold":
            rank_matches = inst_records[inst_records["rank"] <= target_rank].sort_values(by="year")
            milestone_label = f"the top {target_rank}"
        else:
            rank_matches = inst_records[inst_records["rank"] == target_rank].sort_values(by="year")
            milestone_label = f"#{target_rank}"

        if not rank_matches.empty:
            first_row = rank_matches.iloc[0]
            first_yr = int(first_row["year"])
            actual_rank = int(first_row["rank"]) if pd.notna(first_row["rank"]) and first_row["rank"] == int(first_row["rank"]) else first_row["rank"]
            score_val = first_row["score"]
            all_matching_years = sorted(rank_matches["year"].astype(int).tolist())

            if target_mode == "threshold":
                rank_phrase = f", achieving Rank **#{actual_rank}**"
                action_verb = "first entered"
                if len(all_matching_years) == 1:
                    duration_msg = f"It appeared in **{milestone_label}** in **{first_yr}**."
                elif len(all_matching_years) == len(inst_records["year"].unique()):
                    duration_msg = f"It has stayed within **{milestone_label}** continuously across all **{len(all_matching_years)}** ranking cycles from {all_matching_years[0]} to {all_matching_years[-1]}."
                else:
                    years_str = ", ".join(str(y) for y in all_matching_years)
                    duration_msg = f"It has been ranked within **{milestone_label}** in **{len(all_matching_years)}** ranking cycles ({years_str})."
            else:
                rank_phrase = ""
                action_verb = "first ranked"
                if len(all_matching_years) == 1:
                    duration_msg = f"It achieved this rank in **{first_yr}**."
                elif len(all_matching_years) == len(inst_records["year"].unique()):
                    duration_msg = f"It has held Rank **#{target_rank}** continuously in all **{len(all_matching_years)}** ranking cycles from {all_matching_years[0]} to {all_matching_years[-1]}."
                else:
                    years_str = ", ".join(str(y) for y in all_matching_years)
                    duration_msg = f"It has achieved Rank **#{target_rank}** in **{len(all_matching_years)}** ranking cycles ({years_str})."

            summary = (
                f"**{matched_institution}** {action_verb} **{milestone_label}** in the **{cat}** category in **{first_yr}**{rank_phrase} "
                f"with an overall score of **{score_val:.2f}**.\n\n"
                f"- {duration_msg}\n"
                f"- **Parameter Breakdown in {first_yr}**:\n"
                f"  - Teaching, Learning & Resources (TLR): **{first_row.get('tlr', '—')}**\n"
                f"  - Research and Professional Practice (RPC): **{first_row.get('rpc', '—')}**\n"
                f"  - Graduation Outcomes (GO): **{first_row.get('go', '—')}**\n"
                f"  - Outreach and Inclusivity (OI): **{first_row.get('oi', '—')}**\n"
                f"  - Peer Perception (PR): **{first_row.get('perception', '—')}**"
            )

            trend_df = analysis.get_institution_rank_trend(df_master, matched_institution, category=cat)
            fig = viz.plot_institution_rank_trend(trend_df, matched_institution) if not trend_df.empty else None
            data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
            existing_cols = [c for c in data_cols if c in rank_matches.columns]
            return {
                "figure": fig,
                "summary_text": summary,
                "data": rank_matches[existing_cols].reset_index(drop=True),
                "intent": intent,
            }
        else:
            best_row = inst_records.sort_values(by="rank").iloc[0]
            best_rank = int(best_row["rank"]) if pd.notna(best_row["rank"]) and best_row["rank"] == int(best_row["rank"]) else best_row["rank"]
            best_year = int(best_row["year"])
            neg_verb = "entered" if target_mode == "threshold" else "ranked"
            summary = (
                f"**{matched_institution}** has never {neg_verb} **{milestone_label}** in the **{cat}** category across any available NIRF year (2017 to {end_year}).\n\n"
                f"- Its highest rank achieved to date in **{cat}** is **#{best_rank}** in **{best_year}** (overall score: **{best_row['score']:.2f}**)."
            )
            trend_df = analysis.get_institution_rank_trend(df_master, matched_institution, category=cat)
            fig = viz.plot_institution_rank_trend(trend_df, matched_institution) if not trend_df.empty else None
            data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
            existing_cols = [c for c in data_cols if c in inst_records.columns]
            return {
                "figure": fig,
                "summary_text": summary,
                "data": inst_records[existing_cols].sort_values(by="year").reset_index(drop=True),
                "intent": intent,
            }

    # 0c. Parameter Comparison for single institution (e.g. "Compare IIT Indore's TLR and RPC scores in Engineering in 2025.")
    if intent == "parameter_comparison":
        if not matched_institution:
            return {
                "figure": None,
                "summary_text": f"Institution **'{institution}'** was not found in the NIRF dataset. Please check the spelling or search for another institution.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        cat_year_match = df_master[(df_master["name"] == matched_institution) & (df_master["year"] == year) & (df_master["category"].str.lower() == cat.lower())]
        if cat_year_match.empty:
            return {
                "figure": None,
                "summary_text": f"**{matched_institution}** was not ranked in the **{cat}** category in **{year}**.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        row = cat_year_match.iloc[0]
        compare_params = params if len(params) >= 2 else ["tlr", "rpc"]
        param_labels = {
            "tlr": "Teaching, Learning & Resources (TLR)",
            "rpc": "Research and Professional Practice (RPC)",
            "go": "Graduation Outcomes (GO)",
            "oi": "Outreach and Inclusivity (OI)",
            "perception": "Peer Perception (PR)",
            "score": "Overall Score"
        }
        short_labels = {
            "tlr": "TLR",
            "rpc": "RPC",
            "go": "GO",
            "oi": "OI",
            "perception": "Perception",
            "score": "Overall Score"
        }

        p_names = [short_labels.get(p, p.upper()) for p in compare_params]
        p_vals = [float(row[p]) if pd.notna(row.get(p)) else 0.0 for p in compare_params]

        max_idx = int(np.argmax(p_vals))
        min_idx = int(np.argmin(p_vals))
        p_diff = p_vals[max_idx] - p_vals[min_idx]

        summary_lines = [
            f"Parameter Comparison for **{matched_institution}** in **{cat}** ({year}):",
            ""
        ]
        for p, val in zip(compare_params, p_vals):
            summary_lines.append(f"- **{param_labels.get(p, p.upper())}**: **{val:.2f}**")

        if len(compare_params) == 2:
            lead_name = short_labels.get(compare_params[max_idx], compare_params[max_idx].upper())
            trail_name = short_labels.get(compare_params[min_idx], compare_params[min_idx].upper())
            summary_lines.append("")
            summary_lines.append(f"**{lead_name}** is higher than **{trail_name}** by **{p_diff:.2f}** points ({p_vals[max_idx]:.2f} vs {p_vals[min_idx]:.2f}).")
        else:
            lead_name = short_labels.get(compare_params[max_idx], compare_params[max_idx].upper())
            summary_lines.append("")
            summary_lines.append(f"Highest parameter is **{lead_name}** with a score of **{p_vals[max_idx]:.2f}**.")

        fig = viz.plot_parameter_comparison(matched_institution, cat, year, p_names, p_vals)
        data_cols = ["year", "category", "name", "rank", "score"] + [p for p in compare_params if p in row.index]
        existing_cols = [c for c in data_cols if c in cat_year_match.columns]
        return {
            "figure": fig,
            "summary_text": "\n".join(summary_lines),
            "data": cat_year_match[existing_cols].reset_index(drop=True),
            "intent": intent,
        }

    # 0d. Best Rank Query (e.g. "What was IIT Indore's best rank in Engineering?")
    if intent == "best_rank":
        if not matched_institution:
            return {
                "figure": None,
                "summary_text": f"Institution **'{institution}'** was not found in the NIRF dataset. Please check the spelling or search for another institution.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        inst_records = df_master[(df_master["name"] == matched_institution) & (df_master["category"].str.lower() == cat.lower())].sort_values(by="year")
        if inst_records.empty:
            other_cats = df_master[df_master["name"] == matched_institution]["category"].unique().tolist()
            cats_msg = f" (ranked in: {', '.join(other_cats)})" if other_cats else ""
            return {
                "figure": None,
                "summary_text": f"**{matched_institution}** has no ranking records in the **{cat}** category{cats_msg} across 2017–{end_year}.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        best_row = inst_records.sort_values(by=["rank", "score"], ascending=[True, False]).iloc[0]
        best_rank = int(best_row["rank"]) if pd.notna(best_row["rank"]) and best_row["rank"] == int(best_row["rank"]) else best_row["rank"]
        best_year = int(best_row["year"])
        best_score = best_row["score"]

        all_best = inst_records[inst_records["rank"] == best_row["rank"]]
        best_years = sorted(all_best["year"].astype(int).tolist())
        best_years_str = ", ".join(str(y) for y in best_years)

        latest_row = inst_records.iloc[-1]
        latest_year = int(latest_row["year"])
        latest_rank = int(latest_row["rank"]) if pd.notna(latest_row["rank"]) and latest_row["rank"] == int(latest_row["rank"]) else latest_row["rank"]

        summary = (
            f"The best NIRF rank achieved by **{matched_institution}** in the **{cat}** category is **#{best_rank}** in **{best_years_str}** "
            f"with an overall score of **{best_score:.2f}**.\n\n"
            f"- **Best Ranking Year**: {best_years_str} (Score: **{best_score:.2f}**, TLR: **{best_row.get('tlr', '—')}**, RPC: **{best_row.get('rpc', '—')}**)\n"
            f"- **Latest Standing ({latest_year})**: Rank **#{latest_rank}** (Score: **{latest_row['score']:.2f}**)\n"
            f"- Note: A lower rank number indicates superior performance (Rank #1 is top position)."
        )

        trend_df = analysis.get_institution_rank_trend(df_master, matched_institution, category=cat)
        fig = viz.plot_institution_rank_trend(trend_df, matched_institution) if not trend_df.empty else None
        data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
        existing_cols = [c for c in data_cols if c in inst_records.columns]
        return {
            "figure": fig,
            "summary_text": summary,
            "data": inst_records[existing_cols].reset_index(drop=True),
            "intent": intent,
        }

    # 0e. Rank Progression Query (e.g. "Did IIT Indore improve its rank every year in Engineering?")
    if intent == "rank_progression":
        if not matched_institution:
            return {
                "figure": None,
                "summary_text": f"Institution **'{institution}'** was not found in the NIRF dataset. Please check the spelling or search for another institution.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        inst_records = df_master[(df_master["name"] == matched_institution) & (df_master["category"].str.lower() == cat.lower())].sort_values(by="year")
        if inst_records.empty:
            other_cats = df_master[df_master["name"] == matched_institution]["category"].unique().tolist()
            cats_msg = f" (ranked in: {', '.join(other_cats)})" if other_cats else ""
            return {
                "figure": None,
                "summary_text": f"**{matched_institution}** has no ranking records in the **{cat}** category{cats_msg} across 2017–{end_year}.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        all_dataset_years = sorted(df_master["year"].unique().tolist())
        q_text = query_plan.get("original_query", "").lower()
        is_every_year_query = bool(re.search(r'\b(every\s+year|each\s+year|consistently|consecutive)\b', q_text))

        records_years = set(inst_records["year"].astype(int).tolist())
        year_to_row = {int(r["year"]): r for _, r in inst_records.iterrows()}
        sorted_recorded_years = sorted(records_years)

        improved_transitions = []
        declined_transitions = []
        unchanged_transitions = []

        for i in range(1, len(sorted_recorded_years)):
            y_prev = sorted_recorded_years[i-1]
            y_curr = sorted_recorded_years[i]
            r_prev = year_to_row[y_prev]["rank"]
            r_curr = year_to_row[y_curr]["rank"]

            # Lower rank number is better! (e.g. 15 -> 10: 15 - 10 = +5 improvement)
            diff = r_prev - r_curr
            if diff > 0:
                improved_transitions.append((y_prev, y_curr, int(r_prev), int(r_curr), int(diff)))
            elif diff < 0:
                declined_transitions.append((y_prev, y_curr, int(r_prev), int(r_curr), int(abs(diff))))
            else:
                unchanged_transitions.append((y_prev, y_curr, int(r_curr)))

        # Did it improve every year?
        improved_every_year = (
            len(declined_transitions) == 0 and 
            len(unchanged_transitions) == 0 and 
            len(improved_transitions) == (len(all_dataset_years) - 1) and
            len(records_years) == len(all_dataset_years)
        )

        if is_every_year_query:
            if improved_every_year:
                direct_ans = f"Yes. **{matched_institution}** improved its rank every year in **{cat}** from {all_dataset_years[0]} to {all_dataset_years[-1]}."
            else:
                direct_ans = f"No. **{matched_institution}** did not improve its rank every year in **{cat}**."
        else:
            direct_ans = f"Rank Progression Analysis for **{matched_institution}** in **{cat}** ({sorted_recorded_years[0]}–{sorted_recorded_years[-1]}):"

        summary_lines = [direct_ans, ""]

        if improved_transitions:
            summary_lines.append("**Years Improved (lower rank number):**")
            for y_prev, y_curr, r_p, r_c, diff in improved_transitions:
                summary_lines.append(f"- **{y_curr}**: Rank **#{r_c}** (improved by **{diff}** positions from #{r_p} in {y_prev})")
            summary_lines.append("")

        if declined_transitions:
            summary_lines.append("**Years Declined:**")
            for y_prev, y_curr, r_p, r_c, diff in declined_transitions:
                summary_lines.append(f"- **{y_curr}**: Rank **#{r_c}** (dropped by **{diff}** positions from #{r_p} in {y_prev})")
            summary_lines.append("")

        if unchanged_transitions:
            summary_lines.append("**Years Unchanged:**")
            for y_prev, y_curr, r_c in unchanged_transitions:
                summary_lines.append(f"- **{y_curr}**: Retained Rank **#{r_c}** from {y_prev}")
            summary_lines.append("")

        missing_dataset_years = [y for y in all_dataset_years if y not in records_years]
        if missing_dataset_years:
            summary_lines.append(f"*(Note: Unranked / no records in {', '.join(str(y) for y in missing_dataset_years)})*")

        trend_df = analysis.get_institution_rank_trend(df_master, matched_institution, category=cat)
        fig = viz.plot_institution_rank_trend(trend_df, matched_institution) if not trend_df.empty else None
        data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
        existing_cols = [c for c in data_cols if c in inst_records.columns]
        return {
            "figure": fig,
            "summary_text": "\n".join(summary_lines).strip(),
            "data": inst_records[existing_cols].reset_index(drop=True),
            "intent": intent,
        }

    # 0b. Dedicated Institution Comparison
    if intent == "institution_comparison":
        target_insts = matched_institutions if matched_institutions else ([matched_institution] if matched_institution else [])
        raw_insts = institutions if institutions else ([institution] if institution else [])

        # Check for any unmatched / not found institutions
        missing_insts = [raw_insts[i] for i, m in enumerate(target_insts) if not m]
        if missing_insts:
            missing_str = ", ".join([f"**'{m}'**" for m in missing_insts])
            return {
                "figure": None,
                "summary_text": f"Institution {missing_str} was not found in the NIRF dataset. Cannot perform comparison.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        if len(target_insts) < 2:
            return {
                "figure": None,
                "summary_text": "Comparison requires at least two institutions. Please specify both institutions to compare.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        # Check records for requested year and category
        records_list = []
        missing_records = []
        for inst_name in target_insts:
            match = df_master[(df_master["name"] == inst_name) & (df_master["year"] == year) & (df_master["category"].str.lower() == cat.lower())]
            if match.empty:
                missing_records.append(inst_name)
            else:
                records_list.append(match)

        if missing_records:
            missing_str = ", ".join([f"**{m}**" for m in missing_records])
            verb = "was" if len(missing_records) == 1 else "were"
            return {
                "figure": None,
                "summary_text": f"{missing_str} {verb} not ranked in the **{cat}** category in **{year}**. Available records could not complete the comparison.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        comp_df = pd.concat(records_list, ignore_index=True)
        sorted_comp = comp_df.sort_values(by="rank", ascending=True)
        top_inst = sorted_comp.iloc[0]
        runner_up = sorted_comp.iloc[1]

        r1_rank = int(top_inst["rank"]) if pd.notna(top_inst["rank"]) and top_inst["rank"] == int(top_inst["rank"]) else top_inst["rank"]
        r2_rank = int(runner_up["rank"]) if pd.notna(runner_up["rank"]) and runner_up["rank"] == int(runner_up["rank"]) else runner_up["rank"]
        score_diff = top_inst["score"] - runner_up["score"]
        rank_diff = abs(int(r2_rank) - int(r1_rank)) if isinstance(r1_rank, (int, float)) and isinstance(r2_rank, (int, float)) else None

        num_insts = len(sorted_comp)
        summary_lines = [
            f"Comparison of {num_insts} institutions in **{cat}** ({year}):",
            ""
        ]
        for _, row in sorted_comp.iterrows():
            r_val = int(row["rank"]) if pd.notna(row["rank"]) and row["rank"] == int(row["rank"]) else row["rank"]
            summary_lines.append(f"- **{row['name']}**: Rank **#{r_val}** (overall score: **{row['score']:.2f}**)")

        summary_lines.append("")
        if num_insts == 2:
            summary_lines.append(f"- **{top_inst['name']}** leads by **{score_diff:.2f}** points" + (f" and **{rank_diff}** rank positions" if rank_diff else "") + " (note: a lower rank number indicates higher standing).")
        else:
            summary_lines.append(f"- **{top_inst['name']}** leads the group at Rank **#{r1_rank}** by **{score_diff:.2f}** points over 2nd place (**{runner_up['name']}**). Note: a lower rank number indicates higher standing.")

        summary_lines.append("")
        summary_lines.append("**Parameter Breakdown:**")

        metrics = [
            ("TLR (Teaching & Resources)", "tlr"),
            ("RPC (Research & Practice)", "rpc"),
            ("GO (Graduation Outcomes)", "go"),
            ("OI (Outreach & Inclusivity)", "oi"),
            ("Perception", "perception")
        ]
        for m_label, m_col in metrics:
            inst_vals = []
            for _, r in sorted_comp.iterrows():
                short = r["name"].replace("Indian Institute of Technology", "IIT").replace("National Institute of Technology", "NIT")
                val = r.get(m_col, "—")
                val_str = f"{val:.2f}" if isinstance(val, (int, float)) and pd.notna(val) else str(val)
                inst_vals.append(f"{short} ({val_str})")
            summary_lines.append(f"- **{m_label}**: {' vs '.join(inst_vals)}")

        year_note = ""
        if year_mode == "default_latest":
            year_note = f"\n\n*(Note: No year was specified in your question; displaying comparison for the latest available year, **{year}**.)*"

        summary_text = "\n".join(summary_lines) + year_note

        fig = viz.plot_multi_institution_comparison(comp_df, title=f"Comparison: {cat} ({year})")
        data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
        existing_cols = [c for c in data_cols if c in comp_df.columns]
        return {
            "figure": fig,
            "summary_text": summary_text,
            "data": comp_df[existing_cols].reset_index(drop=True),
            "intent": intent,
        }

    # 1. Institution Queries (Rank or Trend)
    if intent in ["institution_rank", "institution_trend"] or (institution and intent not in ["compare_states", "institution_comparison", "parameter_comparison", "best_rank", "rank_progression", "historical_milestone", "historical_rank_status"]):
        if not matched_institution:
            return {
                "figure": None,
                "summary_text": f"Institution **'{institution}'** was not found in the NIRF dataset. Please check the spelling or search for another institution.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        inst_records = df_master[df_master["name"] == matched_institution]
        if inst_records.empty:
            return {
                "figure": None,
                "summary_text": f"Institution **'{matched_institution}'** was not found in the NIRF dataset.",
                "data": pd.DataFrame(),
                "intent": intent,
            }

        # Sub-case A: Institution Trend over time
        if intent == "institution_trend":
            trend_df = analysis.get_institution_rank_trend(df_master, matched_institution, category=cat)
            if not trend_df.empty:
                fig = viz.plot_institution_rank_trend(trend_df, matched_institution)
                first_rank = int(trend_df.iloc[0]["rank"]) if pd.notna(trend_df.iloc[0]["rank"]) and trend_df.iloc[0]["rank"] == int(trend_df.iloc[0]["rank"]) else trend_df.iloc[0]["rank"]
                last_rank = int(trend_df.iloc[-1]["rank"]) if pd.notna(trend_df.iloc[-1]["rank"]) and trend_df.iloc[-1]["rank"] == int(trend_df.iloc[-1]["rank"]) else trend_df.iloc[-1]["rank"]
                first_yr = trend_df.iloc[0]["year"]
                last_yr = trend_df.iloc[-1]["year"]
                rank_shift = (first_rank - last_rank) if isinstance(first_rank, (int, float)) and isinstance(last_rank, (int, float)) else 0
                summary = (
                    f"**{matched_institution}** ({cat} Category):\n"
                    f"- Started at Rank **{first_rank}** in {first_yr}\n"
                    f"- Reached Rank **{last_rank}** in {last_yr}\n"
                    f"- Net Rank Shift: **{rank_shift:+d}** positions."
                )
                return {"figure": fig, "summary_text": summary, "data": trend_df, "intent": intent}
            else:
                other_cats = inst_records["category"].unique().tolist()
                summary = f"**{matched_institution}** has no ranking records in the **{cat}** category. (Ranked in: {', '.join(other_cats)})."
                return {"figure": None, "summary_text": summary, "data": pd.DataFrame(), "intent": intent}

        # Sub-case B: Institution Rank for a specific year
        year_note = ""
        if year_mode == "default_latest":
            year_note = f"\n\n*(Note: No year was specified in your question; displaying results for the latest available year, **{year}**.)*"

        cat_year_match = inst_records[(inst_records["year"] == year) & (inst_records["category"].str.lower() == cat.lower())]
        if not cat_year_match.empty:
            row = cat_year_match.iloc[0]
            rank_val = int(row["rank"]) if pd.notna(row["rank"]) and row["rank"] == int(row["rank"]) else row["rank"]
            score_val = row["score"]
            summary = (
                f"In **{year}**, **{matched_institution}** was ranked **#{rank_val}** in the **{cat}** category "
                f"with an overall NIRF score of **{score_val:.2f}**.\n\n"
                f"**Parameter Breakdown:**\n"
                f"- Teaching, Learning & Resources (TLR): **{row.get('tlr', '—')}**\n"
                f"- Research and Professional Practice (RPC): **{row.get('rpc', '—')}**\n"
                f"- Graduation Outcomes (GO): **{row.get('go', '—')}**\n"
                f"- Outreach and Inclusivity (OI): **{row.get('oi', '—')}**\n"
                f"- Peer Perception (PR): **{row.get('perception', '—')}**"
                f"{year_note}"
            )
            trend_df = analysis.get_institution_rank_trend(df_master, matched_institution, category=cat)
            fig = viz.plot_institution_rank_trend(trend_df, matched_institution) if not trend_df.empty else None
            data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
            existing_cols = [c for c in data_cols if c in cat_year_match.columns]
            return {
                "figure": fig,
                "summary_text": summary,
                "data": cat_year_match[existing_cols].reset_index(drop=True),
                "intent": "institution_rank",
            }
        else:
            other_cats = inst_records[inst_records["year"] == year]
            if not other_cats.empty:
                cat_ranks = [f"**{r['category']}** (Rank #{int(r['rank']) if pd.notna(r['rank']) and r['rank'] == int(r['rank']) else r['rank']}, Score {r['score']})" for _, r in other_cats.iterrows()]
                summary = (
                    f"**{matched_institution}** was not ranked in the **{cat}** category in **{year}**.\n\n"
                    f"In **{year}**, it is ranked in the following categories:\n"
                    + "\n".join([f"- {cr}" for cr in cat_ranks])
                )
                data_cols = ["year", "category", "name", "rank", "score", "tlr", "rpc", "go", "oi", "perception"]
                existing_cols = [c for c in data_cols if c in other_cats.columns]
                return {
                    "figure": None,
                    "summary_text": summary,
                    "data": other_cats[existing_cols].reset_index(drop=True),
                    "intent": "institution_rank",
                }
            else:
                available_years = sorted(inst_records["year"].unique().tolist())
                summary = (
                    f"**{matched_institution}** was not ranked in **{year}** (available ranking years: {min(available_years)}–{max(available_years)})."
                )
                return {
                    "figure": None,
                    "summary_text": summary,
                    "data": pd.DataFrame(),
                    "intent": "institution_rank",
                }

    # 2. Biggest Improvements
    if intent == "biggest_improvements":
        imp_df = analysis.get_biggest_rank_improvements(df_master, category=cat, start_year=start_year, end_year=end_year)
        if not imp_df.empty:
            fig = viz.plot_biggest_rank_movers(imp_df, f"Top Rank Improvements ({start_year} to {end_year})")
            top_mover = imp_df.iloc[0]
            summary = (
                f"Between {start_year} and {end_year} in **{cat}**:\n"
                f"- Greatest improvement: **{top_mover['name']}** climbing **{int(top_mover['rank_improvement'])}** positions "
                f"(from Rank {int(top_mover['start_rank'])} to Rank {int(top_mover['end_rank'])})."
            )
            return {"figure": fig, "summary_text": summary, "data": imp_df, "intent": intent}

    # 3. Biggest Declines
    if intent == "biggest_declines":
        dec_df = analysis.get_biggest_rank_declines(df_master, category=cat, start_year=start_year, end_year=end_year)
        if not dec_df.empty:
            fig = viz.plot_biggest_rank_movers(dec_df, f"Largest Rank Declines ({start_year} to {end_year})")
            top_drop = dec_df.iloc[0]
            summary = (
                f"Between {start_year} and {end_year} in **{cat}**:\n"
                f"- Largest decline: **{top_drop['name']}** dropped **{int(top_drop['rank_decline'])}** positions "
                f"(from Rank {int(top_drop['start_rank'])} to Rank {int(top_drop['end_rank'])})."
            )
            return {"figure": fig, "summary_text": summary, "data": dec_df, "intent": intent}

    # 4. Score Trend Over Time
    if intent == "score_trend":
        trend_df = analysis.get_average_score_trend(df_master, category=cat)
        if not trend_df.empty:
            fig = viz.plot_score_trend(trend_df)
            start_mean = trend_df.iloc[0]["mean_score"]
            end_mean = trend_df.iloc[-1]["mean_score"]
            summary = (
                f"Average Score Trajectory in **{cat}**:\n"
                f"- {trend_df.iloc[0]['year']} Average: **{start_mean:.2f}**\n"
                f"- {trend_df.iloc[-1]['year']} Average: **{end_mean:.2f}**\n"
                f"- Score Trend: **{end_mean - start_mean:+.2f}** points over the analyzed period."
            )
            return {"figure": fig, "summary_text": summary, "data": trend_df, "intent": intent}

    # 5. Top States Distribution
    if intent == "top_states":
        state_df = analysis.get_states_top_institutions(df_master, year=year, category=cat, top_n=100)
        if not state_df.empty:
            fig = viz.plot_state_distribution(state_df, f"Top States with Institutions in Top 100 ({year})")
            top_state = state_df.iloc[0]
            summary = (
                f"In **{year}** for **{cat}** category:\n"
                f"- State with the most institutions in top 100: **{top_state['state']}** with **{top_state['institution_count']}** institutions.\n"
                f"- Followed by **{state_df.iloc[1]['state']}** with **{state_df.iloc[1]['institution_count']}**."
            )
            return {"figure": fig, "summary_text": summary, "data": state_df, "intent": intent}

    # 6. Compare Two States
    if intent == "compare_states":
        s1 = states[0] if len(states) >= 1 else "Karnataka"
        s2 = states[1] if len(states) >= 2 else "Tamil Nadu"
        comp_summary, raw_comp = analysis.compare_two_states(df_master, state1=s1, state2=s2, category=cat, year=year)
        if not raw_comp.empty:
            fig = viz.plot_two_states_comparison(raw_comp)
            summary = (
                f"Comparison between **{s1}** and **{s2}** in {year} ({cat}):\n"
                f"- **{s1}**: {comp_summary.iloc[0]['total_institutions']} institutions, avg score {comp_summary.iloc[0]['average_score']}\n"
                f"- **{s2}**: {comp_summary.iloc[1]['total_institutions']} institutions, avg score {comp_summary.iloc[1]['average_score']}"
            )
            return {"figure": fig, "summary_text": summary, "data": comp_summary, "intent": intent}

    # 7. Score Distribution
    if intent == "score_distribution":
        scores = analysis.get_score_distribution(df_master, year=year, category=cat)
        stats = analysis.get_score_summary_stats(df_master, year=year, category=cat)
        if not scores.empty:
            fig = viz.plot_score_histogram(scores, year=year)
            summary = (
                f"Score Distribution in **{year}** ({cat}):\n"
                f"- Mean Score: **{stats['mean']}**, Median: **{stats['median']}**\n"
                f"- Min Score: **{stats['min']}**, Max Score: **{stats['max']}**, Std Dev: **{stats['std_dev']}**"
            )
            return {"figure": fig, "summary_text": summary, "data": pd.DataFrame([stats]), "intent": intent}

    # 8. Correlation Analysis
    if intent in ["rpc_correlation", "all_parameters_correlation", "two_var_correlation"]:
        v1 = params[0] if len(params) >= 1 else "rpc"
        v2 = params[1] if len(params) >= 2 else "score"
        two_var = analysis.get_two_variable_correlation(df_master, v1, v2, year=year, category=cat)
        if not two_var["data"].empty:
            fig = viz.plot_scatter_with_trendline(
                two_var["data"], v1, v2, corr_val=two_var["r"],
                title=f"Correlation: {v1.upper()} vs {v2.upper()} in {year} (r = {two_var['r']})"
            )
            summary = (
                f"Correlation Analysis in **{year}** ({cat}):\n"
                f"- Correlation between **{v1.upper()}** and **{v2.upper()}**: **r = {two_var['r']}**\n"
                f"- Trend Line Equation: `{v2.upper()} = {two_var['slope']} * {v1.upper()} + {two_var['intercept']}`"
            )
            return {"figure": fig, "summary_text": summary, "data": two_var["data"], "intent": intent}

    # 9. Top 10 Entries and Exits
    if intent == "top10_entries_exits":
        top10_info = analysis.get_top10_entries_and_exits(df_master, category=cat, year1=start_year, year2=end_year)
        entries_str = ", ".join(top10_info["entries"]) if top10_info["entries"] else "None"
        exits_str = ", ".join(top10_info["exits"]) if top10_info["exits"] else "None"
        summary = (
            f"Top 10 Mobility between **{start_year}** and **{end_year}** ({cat}):\n"
            f"- **New Entrants into Top 10**: {entries_str}\n"
            f"- **Exited Top 10**: {exits_str}\n"
            f"- **Consistently Retained**: {len(top10_info['retained'])} institutions"
        )
        data_df = pd.DataFrame({
            "New Entrants into Top 10": pd.Series(top10_info["entries"]),
            "Exited Top 10": pd.Series(top10_info["exits"])
        })
        return {"figure": None, "summary_text": summary, "data": data_df, "intent": intent}

    # Fallback to Top Institutions
    top_insts = analysis.filter_data(df_master, year=year, category=cat).sort_values("rank").head(10)
    if not top_insts.empty:
        fig = viz.plot_score_histogram(top_insts["score"], year=year)
        summary = (
            f"Showing top institutions in **{year}** for **{cat}** category. "
            f"Rank 1 is **{top_insts.iloc[0]['name']}** with score **{top_insts.iloc[0]['score']}**."
        )
        return {"figure": fig, "summary_text": summary, "data": top_insts[["name", "rank", "score", "state"]], "intent": "general_overview"}

    return {
        "figure": None,
        "summary_text": "Could not determine exact analysis. Please rephrase or use dashboard filters.",
        "data": pd.DataFrame(),
        "intent": intent
    }
