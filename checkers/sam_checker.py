import requests
import csv
import io
from thefuzz import fuzz

SAM_URL = "https://data.opensanctions.org/datasets/latest/us_sam_exclusions/targets.simple.csv"

def download_sam_list():
    try:
        response = requests.get(SAM_URL, timeout=60)
        response.raise_for_status()
        content = response.content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading SAM exclusions list: {e}")
        return []

def check_sam(name, sam_list, aliases=None):
    if not sam_list:
        return {
            "status": "error",
            "message": "SAM exclusions list unavailable"
        }

    all_names = [name]
    if aliases:
        all_names.extend(aliases)

    best_match = None
    best_score = 0
    best_name_searched = name

    for search_name in all_names:
        for entry in sam_list:
            entry_name = entry.get("name", "").upper()
            score = fuzz.token_sort_ratio(search_name.upper(), entry_name)

            if score > best_score:
                best_score = score
                best_match = entry
                best_name_searched = search_name

    if best_score >= 95:
        return {
            "status": "flagged",
            "message": "High confidence match found on SAM exclusions list",
            "name_searched": best_name_searched,
            "match_score": best_score,
            "matched_entry": {
                "name": best_match.get("name", ""),
                "country": best_match.get("country", ""),
                "topics": best_match.get("topics", "")
            }
        }
    elif best_score >= 80:
        return {
            "status": "review",
            "message": "Possible match found on SAM exclusions list — human review required",
            "name_searched": best_name_searched,
            "match_score": best_score,
            "matched_entry": {
                "name": best_match.get("name", ""),
                "country": best_match.get("country", ""),
                "topics": best_match.get("topics", "")
            }
        }
    else:
        return {
            "status": "clear",
            "message": "No match found on SAM exclusions list",
            "names_searched": all_names,
            "match_score": best_score
        }

if __name__ == "__main__":
    print("Downloading SAM exclusions list...")
    sam_list = download_sam_list()
    print(f"Loaded {len(sam_list)} entries")

    result = check_sam("ARDALAN ENKESHAFI", sam_list)
    print(result)