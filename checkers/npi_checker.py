import requests

def check_npi(npi_number):
    url = f"https://npiregistry.cms.hhs.gov/api/?number={npi_number}&version=2.1"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Could not reach NPI registry: {e}"
        }
    
    if data.get("result_count", 0) == 0:
        return {
            "status": "not_found",
            "message": f"No provider found with NPI {npi_number}"
        }
    
    provider = data["results"][0]
    
    basic = provider.get("basic", {})
    taxonomies = provider.get("taxonomies", [{}])
    addresses = provider.get("addresses", [{}])
    
    primary_taxonomy = next((t for t in taxonomies if t.get("primary")), taxonomies[0])
    primary_address = next((a for a in addresses if a.get("address_purpose") == "LOCATION"), addresses[0])
    
    other_names = provider.get("other_names", [])
    aliases = [
        f"{n.get('first_name', '')} {n.get('last_name', '')}".strip()
        for n in other_names
    ]
    
    return {
        "status": "verified",
        "npi": npi_number,
        "name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
        "aliases": aliases,
        "credential": basic.get("credential", ""),
        "specialty": primary_taxonomy.get("desc", ""),
        "license_number": primary_taxonomy.get("license", ""),
        "license_state": primary_taxonomy.get("state", ""),
        "practice_address": f"{primary_address.get('address_1', '')}, {primary_address.get('city', '')}, {primary_address.get('state', '')} {primary_address.get('postal_code', '')}",
        "enumeration_date": basic.get("enumeration_date", ""),
        "last_updated": basic.get("last_updated", "")
    }

if __name__ == "__main__":
    result = check_npi("1003000126")
    print(result)