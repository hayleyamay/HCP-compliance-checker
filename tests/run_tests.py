import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.verify import verify_hcp

def run_tests():
    print("Loading test cases...")
    with open("tests/test_cases.json", "r") as f:
        test_suite = json.load(f)
    
    test_cases = test_suite["test_cases"]
    print(f"Found {len(test_cases)} test cases\n")
    
    results = []
    
    for case in test_cases:
        case_id = case["id"]
        category = case["category"]
        description = case["description"]
        inputs = case["input"]
        
        print(f"Running {case_id} ({category}) — {description}")
        
        try:
            if "npi" in inputs and inputs["npi"]:
                result = verify_hcp(npi=inputs["npi"])
            elif "name" in inputs and inputs["name"]:
                result = verify_hcp(name=inputs["name"])
            else:
                result = {
                    "overall_status": "INVALID INPUT",
                    "message": "No valid NPI or name provided"
                }
        except Exception as e:
            result = {
                "overall_status": "ERROR",
                "message": str(e)
            }
        
        results.append({
            "case_id": case_id,
            "category": category,
            "description": description,
            "input": inputs,
            "output": {
                "overall_status": result.get("overall_status"),
                "npi_status": result.get("npi_check", {}).get("status") if result.get("npi_check") else None,
                "oig_status": result.get("oig_check", {}).get("status") if result.get("oig_check") else None,
                "sam_status": result.get("sam_check", {}).get("status") if result.get("sam_check") else None,
                "oig_score": result.get("oig_check", {}).get("match_score") if result.get("oig_check") else None,
                "sam_score": result.get("sam_check", {}).get("match_score") if result.get("sam_check") else None,
                "provider_name": result.get("provider", {}).get("name"),
                "full_result": result
            }
        })
        
        print(f"  → {result.get('overall_status')}\n")
    
    output = {
        "metadata": {
            "run_at": datetime.now().isoformat(),
            "total_cases": len(results),
            "categories": {
                "A": len([r for r in results if r["category"] == "A"]),
                "B": len([r for r in results if r["category"] == "B"]),
                "C": len([r for r in results if r["category"] == "C"]),
                "D": len([r for r in results if r["category"] == "D"])
            }
        },
        "results": results
    }
    
    output_path = "tests/results/test_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print("=" * 50)
    print(f"Done — {len(results)} cases run")
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    run_tests()