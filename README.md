# HCP Compliance Checker 🏥

A free, open-source tool that verifies Healthcare Professional (HCP) 
compliance in real time — checking NPI registry, OIG exclusion list, 
and SAM.gov in one unified pipeline instead of three separate manual steps.

## The Problem

Before a pharma rep can engage a doctor — as a speaker, consultant, 
or prescriber — compliance teams need to verify:

- Is this person who they say they are? (NPI registry)
- Are they excluded from federal healthcare programs? (OIG LEIE)
- Are they on any federal exclusion lists? (SAM.gov)

Right now this is a manual, multi-step process. Each check is done 
separately, results are compiled by hand, and adding new countries 
or data sources means building entirely new pipelines from scratch.

## The Solution

Type in an NPI number, get back a unified compliance report in seconds:

- ✅ Identity verified against the NPPES NPI registry
- ✅ OIG exclusion list checked
- ✅ SAM.gov exclusion list checked
- ✅ Fuzzy matching to compbine into one portfolio
- ⚠️ Ambiguous matches flagged for human review
- 📋 Full audit trail with confidence scoring

## Architecture

The pipeline is modular by design — each data source is a 
self-contained checker module. Adding a new country or data source 
means adding one module, not rebuilding everything.

NPI Input
↓
┌─────────────────────────────┐
│         Pipeline            │
│  ┌──────────┐ ┌──────────┐ │
│  │   NPI    │ │   OIG    │ │
│  │ Checker  │ │ Checker  │ │
│  └──────────┘ └──────────┘ │
│  ┌──────────┐              │
│  │  SAM.gov │              │
│  │ Checker  │              │
│  └──────────┘              │
└─────────────────────────────┘
↓
Unified Compliance Report

## Data Sources

All data sources are official US government public records:

- **NPPES NPI Registry** — National Plan and Provider Enumeration System
- **OIG LEIE** — Office of Inspector General List of Excluded 
  Individuals/Entities
- **SAM.gov** — System for Award Management exclusions

## Status

🚧 Currently in development

## About

Built by Hayley, an MS Computer Science student focused on AI safety, 
ethics, and governance — exploring how automated verification pipelines 
can reduce compliance burden while maintaining accuracy and auditability.