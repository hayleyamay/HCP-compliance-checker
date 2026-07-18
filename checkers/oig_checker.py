import requests
import csv
import io
from thefuzz import fuzz

OIG_URL = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"

def download_oig_list():
    try:
        response = requests.get(OIG_URL, timeout=30)
        response.raise_for_status()
        content = response.content.decode("latin-1")
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading OIG list: {e}")
        return []

def check_oig(name, oig_list):
    if not oig_list:
        return {
            "status": "error",
            "message": "OIG list unavailable"
        }
    
    name_parts = name.upper().split()
    if len(name_parts) < 2:
        return {
            "status": "error",
            "message": "Invalid name provided"
        }
    
    first_name = name_parts[0]
    last_name = name_parts[-1]
    
    best_match = None
    best_score = 0
    
    for entry in oig_list:
        entry_first = entry.get("FIRSTNAME", "").upper()
        entry_last = entry.get("LASTNAME", "").upper()
        entry_full = f"{entry_first} {entry_last}"
        
        score = fuzz.token_sort_ratio(name.upper(), entry_full)
        
        if score > best_score:
            best_score = score
            best_match = entry
    
    if best_score >= 95:
        return {
            "status": "flagged",
            "message": f"High confidence match found on OIG exclusion list",
            "match_score": best_score,
            "matched_entry": {
                "name": f"{best_match.get('FIRSTNAME', '')} {best_match.get('LASTNAME', '')}",
                "exclusion_type": best_match.get("EXCLTYPE", ""),
                "exclusion_date": best_match.get("EXCLDATE", ""),
                "state": best_match.get("STATE", "")
            }
        }
    elif best_score >= 80:
        return {
            "status": "review",
            "message": f"Possible match found on OIG exclusion list — human review required",
            "match_score": best_score,
            "matched_entry": {
                "name": f"{best_match.get('FIRSTNAME', '')} {best_match.get('LASTNAME', '')}",
                "exclusion_type": best_match.get("EXCLTYPE", ""),
                "exclusion_date": best_match.get("EXCLDATE", ""),
                "state": best_match.get("STATE", "")
            }
        }
    else:
        return {
            "status": "clear",
            "message": "No match found on OIG exclusion list",
            "match_score": best_score
        }

if __name__ == "__main__":
    print("Downloading OIG exclusion list...")
    oig_list = download_oig_list()
    print(f"Loaded {len(oig_list)} entries")
    
    result = check_oig("ARDALAN ENKESHAFI", oig_list)
    print(result)