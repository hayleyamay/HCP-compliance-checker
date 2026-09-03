import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkers.npi_checker import check_npi
from checkers.oig_checker import download_oig_list, check_oig
from checkers.sam_checker import download_sam_list, check_sam

def verify_hcp(npi=None, name=None):
    print(f"\nStarting compliance verification")
    print("=" * 50)

    if not npi and not name:
        return {
            "overall_status": "ERROR",
            "message": "Either NPI number or provider name must be provided"
        }

    # Step 1 — NPI Check
    if npi:
        print(f"Step 1: Verifying identity via NPI registry (NPI: {npi})...")
        npi_result = check_npi(npi_number=npi)
    else:
        print(f"Step 1: Verifying identity via NPI registry (Name: {name})...")
        npi_result = check_npi(name=name)

    if npi_result["status"] != "verified":
        return {
            "npi": npi,
            "name_searched": name,
            "overall_status": "UNVERIFIED",
            "message": "Provider could not be verified in NPI registry",
            "npi_check": npi_result,
            "oig_check": None,
            "sam_check": None
        }

    verified_name = npi_result["name"]
    aliases = npi_result.get("aliases", [])
    print(f"✅ Identity verified: {verified_name} ({npi_result['credential']})")

    # Step 2 — OIG Check
    print("Step 2: Checking OIG exclusion list...")
    oig_list = download_oig_list()
    oig_result = check_oig(verified_name, oig_list, aliases=aliases)

    if oig_result["status"] == "clear":
        print(f"✅ OIG: Clear")
    elif oig_result["status"] == "flagged":
        print(f"❌ OIG: Flagged")
    else:
        print(f"⚠️  OIG: Needs review")

    # Step 3 — SAM Check
    print("Step 3: Checking SAM.gov exclusion list...")
    sam_list = download_sam_list()
    sam_result = check_sam(verified_name, sam_list, aliases=aliases)

    if sam_result["status"] == "clear":
        print(f"✅ SAM: Clear")
    elif sam_result["status"] == "flagged":
        print(f"❌ SAM: Flagged")
    else:
        print(f"⚠️  SAM: Needs review")

    # Step 4 — Overall status
    statuses = [oig_result["status"], sam_result["status"]]

    if "flagged" in statuses:
        overall = "DO NOT ENGAGE"
    elif "review" in statuses:
        overall = "REQUIRES REVIEW"
    elif "error" in statuses:
        overall = "INCOMPLETE — CHECK MANUALLY"
    else:
        overall = "CLEARED FOR ENGAGEMENT"

    print("=" * 50)
    print(f"Overall Status: {overall}")

    return {
        "npi": npi_result.get("npi", npi),
        "name_searched": verified_name,
        "overall_status": overall,
        "provider": {
            "name": npi_result["name"],
            "credential": npi_result["credential"],
            "specialty": npi_result["specialty"],
            "license_number": npi_result["license_number"],
            "license_state": npi_result["license_state"],
            "practice_address": npi_result["practice_address"],
            "last_updated": npi_result["last_updated"]
        },
        "npi_check": npi_result,
        "oig_check": oig_result,
        "sam_check": sam_result
    }

if __name__ == "__main__":
    import json

    print("\n--- TEST 1: By NPI ---")
    result = verify_hcp(npi="1003000126")
    print(json.dumps(result, indent=2))

    print("\n--- TEST 2: By Name ---")
    result = verify_hcp(name="ARDALAN ENKESHAFI")
    print(json.dumps(result, indent=2))