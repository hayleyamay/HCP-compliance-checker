import os
import json
from groq import Groq
from datetime import datetime

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def generate_report(verification_result):
    provider = verification_result.get("provider", {})
    overall_status = verification_result.get("overall_status", "UNKNOWN")
    oig_check = verification_result.get("oig_check", {})
    sam_check = verification_result.get("sam_check", {})
    
    prompt = f"""
You are a compliance officer writing a formal verification report.
Write a clear, professional 3-4 sentence summary of this HCP compliance check.
Only write the summary, nothing else.

Provider: {provider.get('name')} ({provider.get('credential')})
NPI: {verification_result.get('npi')}
Specialty: {provider.get('specialty')}
License: {provider.get('license_number')} ({provider.get('license_state')})
Practice Address: {provider.get('practice_address')}
Overall Status: {overall_status}
OIG Check: {oig_check.get('status')} — {oig_check.get('message')}
SAM Check: {sam_check.get('status')} — {sam_check.get('message')}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    summary = response.choices[0].message.content
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "npi": verification_result.get("npi"),
        "overall_status": overall_status,
        "provider": provider,
        "compliance_summary": summary,
        "checks": {
            "npi": verification_result.get("npi_check", {}),
            "oig": oig_check,
            "sam": sam_check
        },
        "data_sources": [
            "NPPES NPI Registry (cms.hhs.gov)",
            "OIG LEIE Exclusion List (oig.hhs.gov)",
            "SAM.gov Exclusions via OpenSanctions"
        ]
    }
    
    return report

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from pipeline.verify import verify_hcp
    
    verification_result = verify_hcp("1003000126")
    report = generate_report(verification_result)
    
    print("\n" + "=" * 50)
    print("COMPLIANCE REPORT")
    print("=" * 50)
    print(f"Generated: {report['generated_at']}")
    print(f"Provider: {report['provider']['name']} ({report['provider']['credential']})")
    print(f"NPI: {report['npi']}")
    print(f"Specialty: {report['provider']['specialty']}")
    print(f"License: {report['provider']['license_number']} ({report['provider']['license_state']})")
    print(f"Address: {report['provider']['practice_address']}")
    print(f"\nOverall Status: {report['overall_status']}")
    print(f"\nCompliance Summary:")
    print(report['compliance_summary'])
    print(f"\nData Sources: {', '.join(report['data_sources'])}")