# Clinical Referral Completeness Tool

## Problem
Unstructured medical referrals frequently lack essential clinical information, requiring receiving specialists to chase down missing details before a consultation can proceed safely and efficiently.

## Proposed Solution
A lightweight, Python-based clinical workflow tool that structures referral data and checks for specialty-specific completeness gaps *before* submission.

## Key Features
- **Structured Intake:** Captures patient demographics, symptoms, duration, red flags, and previous investigations.
- **Completeness Engine:** Dynamically calculates a completeness score and highlights missing critical data points (e.g., missing lipid profile for cardiology, or imaging for neurology).
- **Specialty-Specific Rules:** Tailored checklists for Cardiology, Neurology, Dermatology, and Orthopedics.
- **FHIR Representation:** Maps the structured referral into interoperable healthcare data formats.

## Tech Stack
- **Language:** Python
- **Interface:** Streamlit
- **Data Handling:** Pandas
- **Interoperability:** HL7 FHIR (Concepts)

## Current Limitations & Disclaimer
* Prototype software built for educational and portfolio demonstration purposes only.
* Not validated for clinical use. 
* Uses strictly synthetic/de-identified data. No protected health information (PHI) is processed or stored.

## Future Roadmap
- [ ] Database persistence using SQLite
- [ ] Direct EHR integration via SMART on FHIR APIs
- [ ] NLP layer to extract structured fields from clinician free-text notes
- [ ] Comprehensive usability testing with clinical colleagues
