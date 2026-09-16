import json
import csv
import io
import requests
from thefuzz import fuzz
import jaro

OIG_URL = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"
NPPES_API_URL = "https://npiregistry.cms.hhs.gov/api/"

def download_oig_list():
    print("Downloading OIG exclusion list...")
    try:
        response = requests.get(OIG_URL, timeout=30)
        response.raise_for_status()
        content = response.content.decode("latin-1")
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
    except Exception as e:
        print(f"Error downloading OIG list: {e}")
        return []

def resolve_npi_identity(npi_string):
    """Queries NPPES API to resolve provider legal name and registered aliases for NPI inputs."""
    try:
        response = requests.get(NPPES_API_URL, params={"number": npi_string, "version": "2.1"}, timeout=10)
        if response.status_code != 200:
            return None, []
        data = response.json()
        if not data.get("results"):
            return None, []
        
        basic = data["results"][0].get("basic", {})
        first_name = basic.get("first_name", "").strip()
        last_name = basic.get("last_name", "").strip()
        primary_name = f"{first_name} {last_name}".strip()
        
        # Extract registered aliases/other names
        other_names = data["results"][0].get("other_names", [])
        aliases = []
        for o in other_names:
            o_first = o.get("first_name", "").strip()
            o_last = o.get("last_name", "").strip()
            if o_first or o_last:
                aliases.append(f"{o_first} {o_last}".strip())
                
        return primary_name, aliases
    except Exception as e:
        print(f"Error querying NPPES for NPI {npi_string}: {e}")
        return None, []

def token_sort_match(names, oig_list):
    best_score = 0
    best_match = None
    for name in names:
        if not name:
            continue
        for entry in oig_list:
            first = entry.get("FIRSTNAME", "").strip()
            last = entry.get("LASTNAME", "").strip()
            entry_full = f"{first} {last}".upper()
            score = fuzz.token_sort_ratio(name.upper(), entry_full)
            if score > best_score:
                best_score = score
                best_match = entry_full
    return best_score, best_match

def jaro_winkler_match(names, oig_list):
    best_score = 0
    best_match = None
    for name in names:
        if not name:
            continue
        for entry in oig_list:
            first = entry.get("FIRSTNAME", "").strip()
            last = entry.get("LASTNAME", "").strip()
            entry_full = f"{first} {last}".upper()
            score = jaro.jaro_winkler_metric(name.upper(), entry_full)
            score_normalized = round(score * 100, 2)
            if score_normalized > best_score:
                best_score = score_normalized
                best_match = entry_full
    return best_score, best_match

def classify(score, flagged_threshold=98, review_threshold=80):
    if score >= flagged_threshold:
        return "flagged"
    elif score >= review_threshold:
        return "review"
    else:
        return "clear"

def run_comparison():
    print("Loading test cases...")
    with open("tests/test_cases.json", "r") as f:
        test_suite = json.load(f)

    oig_list = download_oig_list()
    print(f"Loaded {len(oig_list)} OIG records\n")

    all_cases = test_suite.get("test_cases", [])
    results = []

    print(f"{'ID':<8} {'Cat':<5} {'Input/Resolved Name':<30} {'TSR Score':<10} {'TSR Class':<10} {'JW Score':<10} {'JW Class':<10}")
    print("-" * 88)

    for case in all_cases:
        category = case.get("category", "Unknown")
        case_id = case.get("case_id", "")
        input_data = case.get("input", {})
        
        search_names = []
        resolved_status = "OK"

        # Handle different input structures across Categories A, B, C, D
        if "name" in input_data:
            search_names.append(input_data["name"])
        elif "npi" in input_data:
            npi_val = str(input_data["npi"]).strip()
            primary_name, aliases = resolve_npi_identity(npi_val)
            if primary_name:
                search_names.append(primary_name)
                search_names.extend(aliases)
            else:
                resolved_status = "UNVERIFIED"

        display_name = search_names[0] if search_names else f"[{resolved_status}]"

        if not search_names:
            # Unverified or invalid cases (e.g., Category D) return unverified/clear state
            tsr_score, tsr_match = 0, None
            jw_score, jw_match = 0, None
            tsr_result = "unverified" if category == "D" or resolved_status == "UNVERIFIED" else "clear"
            jw_result = "unverified" if category == "D" or resolved_status == "UNVERIFIED" else "clear"
        else:
            tsr_score, tsr_match = token_sort_match(search_names, oig_list)
            jw_score, jw_match = jaro_winkler_match(search_names, oig_list)
            tsr_result = classify(tsr_score)
            jw_result = classify(jw_score)

        print(f"{case_id:<8} {category:<5} {display_name[:28]:<30} {tsr_score:<10} {tsr_result:<10} {jw_score:<10} {jw_result:<10}")

        results.append({
            "case_id": case_id,
            "category": category,
            "input": input_data,
            "resolved_names": search_names,
            "status": resolved_status,
            "token_sort_ratio": {
                "score": tsr_score,
                "classification": tsr_result,
                "best_match": tsr_match
            },
            "jaro_winkler": {
                "score": jw_score,
                "classification": jw_result,
                "best_match": jw_match
            },
            "agreement": tsr_result == jw_result
        })

    # Summary Metrics across categories
    cat_summary = {}
    for cat in ["A", "B", "C", "D"]:
        cat_results = [r for r in results if r["category"] == cat]
        if not cat_results:
            continue
        tsr_non_clear = sum(1 for r in cat_results if r["token_sort_ratio"]["classification"] in ["flagged", "review"])
        jw_non_clear = sum(1 for r in cat_results if r["jaro_winkler"]["classification"] in ["flagged", "review"])
        cat_summary[cat] = {
            "total_cases": len(cat_results),
            "tsr_flagged_or_review": tsr_non_clear,
            "jw_flagged_or_review": jw_non_clear
        }

    print("\n--- CATEGORY EVALUATION SUMMARY ---")
    for cat, metrics in cat_summary.items():
        print(f"Category {cat}: Total={metrics['total_cases']} | TSR Flagged/Review={metrics['tsr_flagged_or_review']} | JW Flagged/Review={metrics['jw_flagged_or_review']}")

    output = {
        "metadata": {
            "description": "Full suite evaluation comparing Token Sort Ratio vs Jaro-Winkler across all categories",
            "total_cases_evaluated": len(results),
            "flagged_threshold": 98,
            "review_threshold": 80,
            "oig_records_searched": len(oig_list)
        },
        "category_summary": cat_summary,
        "results": results
    }

    with open("tests/results/jaro_winkler_comparison.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults successfully written to tests/results/jaro_winkler_comparison.json")

if __name__ == "__main__":
    run_comparison()