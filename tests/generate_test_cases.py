import requests
import json
import random
import time
import csv
import io

SPECIALTIES = [
    "Internal Medicine",        # largest primary care specialty
    "Family Medicine",          # second largest primary care
    "Pediatrics",               # third largest primary care
    "Emergency Medicine",       # largest specialty group
    "Psychiatry",               # second largest specialty
    "Surgery",                  # third largest specialty
    "Anesthesiology",           # top 5 specialty
    "Obstetrics & Gynecology",  # top primary care
    "Cardiology",               # high pharma engagement
    "Oncology"                  # high pharma engagement
]

STATES = [
    "CA",  # most physicians nationally
    "NY",  # second most
    "TX",  # third most
    "FL",  # fourth most
    "PA",  # fifth most
    "IL",  # sixth most
    "OH",  # seventh most
    "MA",  # northeast density
    "NC",  # growing market
    "WA"   # west coast representation
]

OIG_URL = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"

def fetch_npis(specialty, state, limit=20):
    url = f"https://npiregistry.cms.hhs.gov/api/?taxonomy_description={specialty}&state={state}&version=2.1&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        results = data.get("results", [])
        providers = []
        for r in results:
            first = r["basic"].get("first_name", "").strip()
            last = r["basic"].get("last_name", "").strip()
            full_name = f"{first} {last}".strip()
    
            if r.get("number") and full_name:
                providers.append({
                    "npi": r["number"],
                    "name": full_name,
                    "specialty": specialty,
                    "state": state
                })

        return providers
    except Exception as e:
        print(f"Error fetching {specialty} in {state}: {e}")
        return []

def generate_category_a(count=20):
    print("Fetching Category A — random NPI pool from NPPES...")
    all_providers = []
    
    for specialty in random.sample(SPECIALTIES, 5):
        for state in random.sample(STATES, 3):
            providers = fetch_npis(specialty, state)
            all_providers.extend(providers)
            print(f"  Fetched {len(providers)} from {specialty} in {state}")
            time.sleep(0.5)
    
    random.shuffle(all_providers)
    selected = all_providers[:count]
    
    cases = []
    for i, provider in enumerate(selected, 1):
        cases.append({
            "id": f"A{str(i).zfill(3)}",
            "category": "A",
            "description": f"Randomly sampled — {provider['specialty']} in {provider['state']}",
            "provider_name": provider["name"],
            "input": {"npi": provider["npi"]}
        })
    
    print(f"Generated {len(cases)} Category A cases")
    return cases

def fetch_oig_list():
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

def generate_category_b(oig_list, count=10):
    print("Generating Category B — random sample from OIG exclusion list...")
    
    individual_exclusions = [
        entry for entry in oig_list
        if entry.get("FIRSTNAME", "").strip()
        and entry.get("LASTNAME", "").strip()
    ]
    
    selected = random.sample(individual_exclusions, min(count, len(individual_exclusions)))
    
    cases = []
    for i, entry in enumerate(selected, 1):
        first = entry.get("FIRSTNAME", "").strip()
        last = entry.get("LASTNAME", "").strip()
        cases.append({
            "id": f"B{str(i).zfill(3)}",
            "category": "B",
            "description": f"Randomly sampled OIG excluded individual",
            "excluded_name": f"{first} {last}",
            "exclusion_type": entry.get("EXCLTYPE", ""),
            "exclusion_date": entry.get("EXCLDATE", ""),
            "state": entry.get("STATE", ""),
            "input": {"name": f"{first} {last}"}
        })
    
    print(f"Generated {len(cases)} Category B cases")
    return cases

if __name__ == "__main__":
    random.seed(42)
    
    category_a = generate_category_a(count=20)
    
    oig_list = fetch_oig_list()
    category_b = generate_category_b(oig_list, count=10)
    
    test_suite = {
        "metadata": {
            "version": "1.0",
            "created": "2026-09-01",
            "description": "HCP compliance checker test set — randomly sampled inputs, no expected outcomes",
            "note": "Expected outcomes to be added after manual verification of pipeline results",
            "sampling": {
                "method": "random",
                "seed": 42,
                "specialties_pool": SPECIALTIES,
                "states_pool": STATES,
                "oig_source": OIG_URL
            }
        },
        "test_cases": category_a + category_b
    }
    
    with open("tests/test_cases.json", "w") as f:
        json.dump(test_suite, f, indent=2)
    
    print(f"\nDone — {len(test_suite['test_cases'])} total cases saved to tests/test_cases.json")
    print(f"  Category A: {len(category_a)} cases")
    print(f"  Category B: {len(category_b)} cases")
    print("\nNext steps:")
    print("  1. Run pipeline against Category A cases")
    print("  2. Manually verify Category B names against OIG list")
    print("  3. Add Category C and D cases manually")
    #CATEGORIES C & D WERE CREATED MANUALLY WITHIN .JSON FILE