import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Configure Streamlit Page Settings
st.set_page_config(
    page_title="Clinical Referral Completeness Tool",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced clinical styling & readability
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        background-color: #0284c7;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0369a1;
        color: white;
    }
    .metric-card {
        background-color: white;
        color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 5px solid #0284c7;
    }
    .warning-box {
        background-color: #fffbeb;
        color: #b45309;
        border-left: 5px solid #f59e0b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .success-box {
        background-color: #f0fdf4;
        color: #15803d;
        border-left: 5px solid #22c55e;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

SPECIALTY_REQUIREMENTS = {
    "Cardiology": {
        "required_fields": ["age", "sex", "reason_for_referral", "duration", "clinical_question", "comorbidities", "medications", "ecg_status", "lipid_profile", "smoking_status"],
        "display_names": {
            "age": "Patient Age",
            "sex": "Patient Sex",
            "reason_for_referral": "Reason for Referral",
            "duration": "Symptom Duration",
            "clinical_question": "Clinical Question",
            "comorbidities": "Comorbidities / Risk Factors",
            "medications": "Current Medications",
            "ecg_status": "ECG Result / Status",
            "lipid_profile": "Recent Lipid Profile",
            "smoking_status": "Smoking Status"
        }
    },
    "Neurology": {
        "required_fields": ["age", "sex", "reason_for_referral", "duration", "clinical_question", "comorbidities", "medications", "neurological_exam", "neuro_imaging", "onset_pattern"],
        "display_names": {
            "age": "Patient Age",
            "sex": "Patient Sex",
            "reason_for_referral": "Reason for Referral",
            "duration": "Symptom Duration",
            "clinical_question": "Clinical Question",
            "comorbidities": "Comorbidities",
            "medications": "Current Medications",
            "neurological_exam": "Focal Neurological Examination",
            "neuro_imaging": "Brain/Spine Imaging (MRI/CT)",
            "onset_pattern": "Symptom Onset Pattern (Acute/Gradual)"
        }
    },
    "Dermatology": {
        "required_fields": ["age", "sex", "reason_for_referral", "duration", "clinical_question", "medications", "lesion_morphology", "lesion_distribution", "previous_treatments"],
        "display_names": {
            "age": "Patient Age",
            "sex": "Patient Sex",
            "reason_for_referral": "Reason for Referral",
            "duration": "Lesion Duration",
            "clinical_question": "Clinical Question",
            "medications": "Current Medications",
            "lesion_morphology": "Lesion Morphology (Shape/Color)",
            "lesion_distribution": "Anatomic Distribution",
            "previous_treatments": "Previous Topical/Systemic Treatments"
        }
    },
    "Orthopedics": {
        "required_fields": ["age", "sex", "reason_for_referral", "duration", "clinical_question", "comorbidities", "mechanism_of_injury", "joint_stability_exam", "plain_radiographs"],
        "display_names": {
            "age": "Patient Age",
            "sex": "Patient Sex",
            "reason_for_referral": "Reason for Referral",
            "duration": "Symptom/Injury Duration",
            "clinical_question": "Clinical Question",
            "comorbidities": "Comorbidities",
            "mechanism_of_injury": "Mechanism of Injury / Onset",
            "joint_stability_exam": "Joint Examination & Stability",
            "plain_radiographs": "X-Ray / Imaging Reports"
        }
    }
}

st.sidebar.title("🏥 Clinical Referral Tool")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox(
    "Navigation Mode",
    ["Referral Builder & Completeness Checker", "Project Overview & Research", "FHIR Interoperability Viewer"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Portfolio MVP Note**\n\n"
    "Designed for MBBS graduates & health-tech developers. "
    "Demonstrates clinical workflow design, completeness scoring, and structured interoperability."
)

if app_mode == "Referral Builder & Completeness Checker":
    st.title("Patient Referral Handoff & Completeness Tool")
    st.markdown("Ensure your clinical referrals contain all necessary information before transmission to specialists, minimizing back-and-forth phone calls and delayed care.")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📝 Referral Input Form")
        
        with st.form("referral_form"):
            # Target Specialty selection
            specialty = st.selectbox("Target Specialty", list(SPECIALTY_REQUIREMENTS.keys()))
            
            st.markdown("#### Demographics & Presentation")
            col_a, col_b = st.columns(2)
            with col_a:
                age = st.number_input("Patient Age", min_value=0, max_value=120, value=55)
            with col_b:
                sex = st.selectbox("Patient Sex", ["Male", "Female", "Other"])
                
            reason_for_referral = st.text_input("Reason for Referral / Chief Complaint", value="Recurrent exertional chest pain")
            duration = st.text_input("Symptom Duration", value="3 months")
            clinical_question = st.text_area("Specific Clinical Question for Specialist", value="Please evaluate for possible ischemic heart disease and advise on revascularization suitability.")

            st.markdown("#### History & Medications")
            comorbidities = st.multiselect(
                "Comorbidities & Risk Factors",
                ["Hypertension", "Type 2 Diabetes", "Hyperlipidemia", "Previous Myocardial Infarction", "Smoking History", "Family History of CAD", "Chronic Kidney Disease", "None / Nil Known"],
                default=["Hypertension", "Type 2 Diabetes"]
            )
            medications = st.text_area("Current Medications & Allergies", value="Aspirin 81mg daily, Metformin 1000mg BID. No known drug allergies.")

            st.markdown("#### Specialty-Specific Clinical Data")
            
            # Dynamic inputs based on selected specialty
            spec_data = {}
            if specialty == "Cardiology":
                spec_data["ecg_status"] = st.text_input("ECG Result / Status", value="Sinus rhythm, T-wave inversion in leads V4-V6")
                spec_data["lipid_profile"] = st.text_input("Recent Lipid Profile (LDL/HDL/Triglycerides)", value="")
                spec_data["smoking_status"] = st.selectbox("Smoking Status", ["Never Smoked", "Former Smoker", "Active Smoker", "Not Documented"])
            elif specialty == "Neurology":
                spec_data["neurological_exam"] = st.text_input("Focal Neurological Examination", value="")
                spec_data["neuro_imaging"] = st.text_input("Brain/Spine Imaging (MRI/CT)", value="")
                spec_data["onset_pattern"] = st.selectbox("Symptom Onset Pattern", ["Acute (<24h)", "Subacute (Days-Weeks)", "Chronic / Progressive", "Not Documented"])
            elif specialty == "Dermatology":
                spec_data["lesion_morphology"] = st.text_input("Lesion Morphology (Shape, Color, Border)", value="")
                spec_data["lesion_distribution"] = st.text_input("Anatomic Distribution", value="")
                spec_data["previous_treatments"] = st.text_input("Previous Topical or Systemic Treatments", value="")
            elif specialty == "Orthopedics":
                spec_data["mechanism_of_injury"] = st.text_input("Mechanism of Injury / Onset", value="")
                spec_data["joint_stability_exam"] = st.text_input("Joint Examination & Stability Findings", value="")
                spec_data["plain_radiographs"] = st.text_input("X-Ray / Imaging Summary", value="")

            submitted = st.form_submit_button("Analyze Completeness & Generate Referral")

    with col2:
        st.subheader("📊 Referral Quality & Completeness Audit")
        
        if submitted:
            # Compile all form data into a dictionary
            data = {
                "age": age,
                "sex": sex,
                "reason_for_referral": reason_for_referral,
                "duration": duration,
                "clinical_question": clinical_question,
                "comorbidities": comorbidities if comorbidities and "None / Nil Known" not in comorbidities else ["None"],
                "medications": medications,
                **spec_data
            }

            # Calculate Completeness Score
            req_fields = SPECIALTY_REQUIREMENTS[specialty]["required_fields"]
            missing_fields = []
            
            for field in req_fields:
                val = data.get(field)
                if val is None or val == "" or (isinstance(val, list) and len(val) == 0) or val == "Not Documented":
                    missing_fields.append(field)

            total_req = len(req_fields)
            score = int(((total_req - len(missing_fields)) / total_req) * 100)

            # Display Score Metric
            st.markdown(f"""
                <div class="metric-card">
                    <h3>Referral Completeness Score: <span style="color: {'#22c55e' if score >= 80 else '#f59e0b' if score >= 50 else '#ef4444'};">{score}%</span></h3>
                    <p>Specialty Target: <b>{specialty}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")

            # Missing Information Feedback
            if missing_fields:
                st.markdown("#### ⚠️ Missing or Incomplete Clinical Elements")
                for mf in missing_fields:
                    display_name = SPECIALTY_REQUIREMENTS[specialty]["display_names"].get(mf, mf)
                    st.markdown(f"<div class='warning-box'><b>Missing:</b> {display_name}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='success-box'><b>🎉 Excellent!</b> All essential specialty-specific clinical criteria are present in this referral.</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 📄 Generated Structured Referral Summary")
            
            # Render formatted clinical output
            display_names = SPECIALTY_REQUIREMENTS[specialty]["display_names"]
            
            output_markdown = f"""
### {specialty.upper()} SPECIALIST CONSULTATION REQUEST
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Patient Profile:** {data['age']}-year-old {data['sex']}  

---
#### 1. Clinical Question & Purpose
> {data['clinical_question']}

#### 2. Clinical Presentation & Reason
* **Primary Concern:** {data['reason_for_referral']}
* **Duration:** {data['duration']}

#### 3. Pertinent Past History & Medications
* **Comorbidities / Risk Factors:** {', '.join(data['comorbidities']) if data['comorbidities'] else 'None reported'}
* **Current Regimen & Allergies:** {data['medications']}

#### 4. Specialty Diagnostic Findings ({specialty})
"""
            for k, v in spec_data.items():
                d_name = display_names.get(k, k)
                output_markdown += f"* **{d_name}:** {v if v else '*Not provided*'}\n"

            st.markdown(output_markdown)
            
            # Save session state for FHIR tab viewing
            st.session_state['last_referral'] = data
            st.session_state['last_specialty'] = specialty
            st.session_state['last_score'] = score
            
        else:
            st.info("👈 Fill out the referral form on the left and click **'Analyze Completeness & Generate Referral'** to run the clinical audit.")

elif app_mode == "Project Overview & Research":
    st.title("Project Background & Product Discovery")
    st.markdown("### Bridging the Gap Between Primary Care and Specialty Consultations")
    
    st.markdown("""
    Referrals are among the most critical and fragile handoffs in healthcare delivery. Unstructured or incomplete referrals 
    frequently result in delayed diagnoses, unnecessary repeat investigations, and redundant triage telephone calls between clinicians.
    """)

    col1, col2 = st.load_cols if hasattr(st, 'load_cols') else st.columns(2) # Fallback standard layout
    
    with st.container():
        st.markdown("#### 🩺 Clinical Problem Statement")
        st.success(
            "**The Handoff Failure:** Specialists frequently receive vague notes such as *"
            "'55M with chest pain, please evaluate.'* Without structured risk factors, temporal duration, "
            "prior baseline investigations, and a precise clinical question, the receiving specialist cannot properly "
            "triage urgency or pre-order appropriate workups."
        )

        st.markdown("#### 💡 Solution Architecture")
        st.markdown("""
        1. **Structured Input Form:** Captures core demographics, symptoms, history, and tailored specialty requirements.
        2. **Deterministic Completeness Engine:** Compares submitted data against established specialty triage guidelines.
        3. **Actionable Feedback:** Instantly flags missing high-value clinical items before transmission.
        4. **FHIR Interoperability:** Maps structured clinical attributes to standard HL7 FHIR resource skeletons.
        """)

        st.markdown("#### 📋 Suggested GitHub README Summary")
        st.code("""
# Clinical Referral Completeness Tool

### Problem
Unstructured medical referrals lack essential clinical context, leading to appointment delays and duplicated workups.

### Proposed Solution
A specialty-aware web application built with Python and Streamlit that evaluates referral completeness 
before handoff and exports standards-compliant HL7 FHIR resources.

### Tech Stack
* Python
* Streamlit
* Pandas
* HL7 FHIR JSON Schema
        """, language="markdown")

elif app_mode == "FHIR Interoperability Viewer":
    st.title("HL7 FHIR Interoperability Preview")
    st.markdown("Healthcare interoperability relies on structured resource mapping. Here we convert the referral into standard HL7 FHIR resource bundles (`Patient`, `Condition`, `ServiceRequest`, `Observation`).")

    if 'last_referral' in st.session_state:
        ref = st.session_state['last_referral']
        spec = st.session_state['last_specialty']
        
        # Construct FHIR Bundle representation
        fhir_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "synthetic-patient-001",
                        "gender": ref['sex'].lower(),
                        "extension": [
                            {
                                "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                                "valueInteger": ref['age']
                            }
                        ]
                    }
                },
                {
                    "resource": {
                        "resourceType": "ServiceRequest",
                        "status": "draft",
                        "intent": "order",
                        "category": [{
                            "coding": [{
                                "system": "http://snomed.info/sct",
                                "code": "103696004",
                                "display": f"Patient referral to {spec} specialist"
                            }]
                        }],
                        "code": {
                            "text": ref['clinical_question']
                        },
                        "reasonCode": [{
                            "text": ref['reason_for_referral']
                        }],
                        "note": [{
                            "text": f"Current Medications: {ref['medications']}"
                        }]
                    }
                }
            ]
        }
        
        # Add conditions
        for c in ref['comorbidities']:
            if c != "None":
                fhir_bundle["entry"].append({
                    "resource": {
                        "resourceType": "Condition",
                        "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
                        "code": {"text": c}
                    }
                })

        st.success(f"Successfully generated FHIR Bundle for {spec} referral (Completeness Score: {st.session_state['last_score']}%)")
        st.json(fhir_bundle)
        
        st.download_button(
            label="Download FHIR JSON Bundle",
            data=json.dumps(fhir_bundle, indent=2),
            file_name=f"referral_{spec.lower()}_fhir.json",
            mime="application/json"
        )
        
    else:
        st.warning("⚠️ No recent referral found. Please go to **'Referral Builder & Completeness Checker'**, fill out the form, and click generate first.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Built with Python & Streamlit for Clinical Workflow Optimization</p>", unsafe_allow_html=True)
