# HCP Compliance Checker 🏥

A free, open-source tool that verifies Healthcare Professional (HCP) 
compliance in real time — checking NPI registry, OIG exclusion list, 
and SAM.gov in one unified automated pipeline instead of three separate 
manual steps.

🔗 **Demo:** Clone the repo and run locally (see setup below)

## The Problem

Before a pharma rep can engage a doctor — as a speaker, consultant, or prescriber — compliance teams need to verify:

- Is this person who they say they are? (NPI registry)
- Are they excluded from federal healthcare programs? (OIG LEIE)
- Are they on any federal exclusion lists? (SAM.gov)

Right now this is a manual, multi-step process. Each check is done separately, results are compiled by hand, and adding new countries or data sources means building entirely new pipelines from scratch.

## The Solution

Input an NPI number, get back a unified compliance report in seconds: 
Example:
POST /verify
{"npi": "1003000126"}

Response:
```json
{
  "overall_status": "CLEARED FOR ENGAGEMENT",
  "provider": {
    "name": "ARDALAN ENKESHAFI",
    "credential": "M.D.",
    "specialty": "Hospitalist",
    "license_number": "MD600003480",
    "license_state": "DC",
    "practice_address": "6410 ROCKLEDGE DR STE 304, BETHESDA, MD"
  },
  "compliance_summary": "This HCP compliance check confirmed...",
  "checks": {
    "npi": {"status": "verified"},
    "oig": {"status": "clear"},
    "sam": {"status": "clear"}
  }
}
```

## Architecture

The pipeline is modular by design — each data source is a 
self-contained checker module. Adding a new country means adding 
one module, not rebuilding everything.

NPI Input
↓
┌─────────────────────────────────┐
│ Pipeline │
│ ┌──────────┐ ┌─────────────┐ │
│ │ NPI │ │ OIG Check │ │
│ │ Checker │ │ Module │ │
│ └──────────┘ └─────────────┘ │
│ ┌──────────┐ │
│ │ SAM.gov │ │
│ │ Module │ │
│ └──────────┘ │
└─────────────────────────────────┘
↓
Unified Compliance Report

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check if API is running |
| POST | `/verify` | Run full compliance check |

## Key Features

- **Real-time verification** — live checks against official government databases
- **Fuzzy name matching** — handles name variations and maiden names using confidence scoring
- **Tiered results** — clear / requires human review / do not engage
- **Audit trail** — every check is timestamped with data sources cited
- **Modular design** — add new countries or data sources as self-contained modules
- **AI-generated summaries** — plain English compliance report via LLaMA 3.1

## Data Sources

All data sources are official public records:

- **NPPES NPI Registry** — National Plan and Provider Enumeration System (cms.hhs.gov)
- **OIG LEIE** — Office of Inspector General List of Excluded Individuals/Entities (oig.hhs.gov)
- **SAM.gov Exclusions** — via OpenSanctions (updated daily)

## Setup

```bash
# Clone the repo
git clone https://github.com/hayleyamay/hcp-compliance-checker.git
cd hcp-compliance-checker

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set your Groq API key
export GROQ_API_KEY="your-key-here"  # Mac/Linux
$env:GROQ_API_KEY="your-key-here"   # Windows

# Run the API
python api/app.py
```

Then open `site/index.html` with Live Server in VS Code to use the demo UI,
or send POST requests to `http://127.0.0.1:5000/verify`.

## Known Limitations

- US providers only (NPI is a US system)
- Name matching may produce false positives for common names — human review is triggered for ambiguous cases
- Phone numbers not available via public NPI API
- OIG and SAM lists are downloaded fresh on each check — caching coming in a future version

## Roadmap

- [ ] Canadian provider support (CPSO module)
- [ ] UK provider support (GMC register)
- [ ] Local caching of exclusion lists for faster checks
- [ ] State medical board license verification
- [ ] Webhook support for Company/CRM integration

## About

Built by Hayley, an MS Computer Science student focused on AI safety, 
ethics, and governance — exploring how automated verification pipelines 
can reduce compliance burden while maintaining accuracy and auditability.

Feedback and contributions extrmely welcome! Especially from anyone working in 
pharma compliance or RegTech.