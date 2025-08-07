import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, date

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Nurse Note Generator",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini API
@st.cache_resource
def initialize_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

def generate_nursing_note(doctor_notes, patient_info, model):
    """Generate nursing notes based on doctor's notes and patient information."""
    
    prompt = f"""
    Prompt for AI Model: Nursing Follow-Up Note Generation
    Role and Goal: You are an expert Intensive Care Unit (ICU) nurse. Your task is to generate a comprehensive nursing follow-up note based on a given doctor's order note and the provided medical protocols. Your note should be insightful, detailed, and directly relevant to the patient's care plan as outlined in the protocols.
    Input:
    • Doctor's Order Note: {doctor_notes}
    Instructions for the Nusring Follow-Up Note based on patient condition:
    - All instructions are to be based on NANDA-I (North American Nursing Diagnosis Association International) protocols.
    - If invasive lines are present, then Infection Bundle Care is mandatory. Following bundles cares are present - CLABSI, CAUTI, VAP, SSI
    
    Output Format: Generate a nursing follow-up note with the following sections, using bullet points for clarity where appropriate:
    • Patient Status (Overall Assessment):
        ◦ General appearance and mentation (e.g., awake, alert, agitated, sedated, GCS, RASS scale, any changes).
        ◦ Pain assessment and current pain level (using BPS/CPOT scale if non-verbal/intubated, or self-report).
        ◦ Current level of activity and mobility.
        ◦ Comfort level.
        - Keep this to a sentence.
    - Nursing Diagnoses:
        - Generate the nursing diagnoses that are relevant to the doctor's orders.
        - If there are any acute changes in the patient's condition, then highlight them in the nursing diagnoses.
        - Use bullet points, and medical conventions.
        - At max give 5 nursing diagnoses and minimum 1.
    • Follow up on To-do
        - Each doctor's note has a to-do list. Your goal is to convert them into simple and actionable items.
        - For each of the to-do list items, generate the list of things that the nurse needs to check based on the Instructions for the Nusring Follow-Up Note based on patient condition
        - At max give 3 actionable items per to-do list item. Keep the language simple and concise. Use bullet points, and medical conventions.
        - Double check if infection bundle protocol is needed.
        - Administer the medications as per the doctor's orders.
    Instructions for the AI Model:
    1. Prioritize: Focus on critical parameters, ordered interventions, and patient responses directly relevant to the doctor's orders and the patient's primary diagnoses as implied by the protocols.
    2. Detail & Contextualize: Do not just list data. Explain the significance of the findings (e.g., "Blood glucose decreasing by 65 mg/dL/hr, indicating good response to insulin infusion").
    3. Cross-Reference Protocols: Synthesize information from relevant protocols (e.g., if a DKA patient is also on mechanical ventilation, incorporate elements from both DKA and ARDS/Ventilation protocols).
    4. Citing (Self-Reference): Do not directly cite within the nursing note. However, ensure the content is directly supported by the information within the provided sources.
    5. Be Comprehensive but Concise: Include all pertinent details without unnecessary verbosity. 
    6. Do not include any information that is not relevant or directly related to the doctor's orders.
    7. Standard Protocols: NANDA-I (North American Nursing Diagnosis Association International) to be adhered to, especially for the follow ups.
    8. Format: Give appropirate spacing between the sections. If any doctor's to-list has spelling or formatting errors, then correct them.
    9. Salutations: Directly jump into the note without any salutations or messaging before AI output.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating nursing notes: {str(e)}")
        return None

def main():
    # Header
    st.title("🩺 Nurse Note Generator")
    st.markdown("Streamline nursing documentation based on physician orders")
    
    # Sidebar for patient information
    st.sidebar.header("📋 Patient Information")
    
    patient_name = st.sidebar.text_input("Patient Name", placeholder="Enter patient name")
    patient_age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=None)
    patient_room = st.sidebar.text_input("Room Number", placeholder="e.g., 101A")
    admission_date = st.sidebar.date_input("Admission Date", value=date.today())
    
    patient_info = {
        'name': patient_name,
        'age': patient_age,
        'room': patient_room,
        'admission_date': admission_date.strftime("%Y-%m-%d") if admission_date else None
    }
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Doctor's Notes Input")
        doctor_notes = st.text_area(
            "Enter the doctor's notes, orders, and treatment plans:",
            height=400,
            placeholder="""Example:
            Patient presents with chest pain. EKG shows ST elevation in leads II, III, aVF.
            Orders:
            - Start heparin drip per protocol
            - Serial troponins q6h x 3
            - Continuous cardiac monitoring
            - NPO for possible cardiac cath
            - Morphine 2mg IV q4h PRN chest pain
            - Metoprolol 25mg PO BID
            - Monitor I/O strictly
            - Daily weights"""
        )
    
    with col2:
        st.header("📋 Generated Nursing Notes")
        
        if st.button("🔄 Generate Nursing Notes", type="primary", use_container_width=True):
            if not doctor_notes.strip():
                st.warning("⚠️ Please enter doctor's notes to generate nursing documentation.")
            else:
                with st.spinner("Generating comprehensive nursing notes..."):
                    # Initialize Gemini model
                    model = initialize_gemini()
                    
                    # Generate nursing notes
                    nursing_notes = generate_nursing_note(doctor_notes, patient_info, model)
                    
                    if nursing_notes:
                        st.markdown("### Generated Nursing Notes")
                        st.markdown(nursing_notes)
                        
                        # Download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"nursing_notes_{patient_name.replace(' ', '') if patient_name else 'patient'}{timestamp}.txt"
                        
                        download_content = f"""NURSING NOTES
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PATIENT INFORMATION:
Name: {patient_info.get('name', 'Not provided')}
Age: {patient_info.get('age', 'Not provided')}
Room: {patient_info.get('room', 'Not provided')}
Admission Date: {patient_info.get('admission_date', 'Not provided')}

DOCTOR'S NOTES:
{doctor_notes}

NURSING NOTES:
{nursing_notes}
"""
                        
                        st.download_button(
                            label="📥 Download Nursing Notes",
                            data=download_content,
                            file_name=filename,
                            mime="text/plain",
                            use_container_width=True
                        )
    
    # Instructions section
    with st.expander("ℹ️ How to Use This Tool"):
        st.markdown("""
        ### Instructions:
        1. **Fill in Patient Information** in the sidebar (optional but recommended)
        2. **Enter Doctor's Notes** in the left column - include all orders, diagnoses, and treatment plans
        3. **Click "Generate Nursing Notes"** to create comprehensive nursing documentation
        4. **Review and Download** the generated notes for your records
        
        ### What This Tool Generates:
        - **Assessment findings** based on medical orders
        - **Nursing diagnoses** relevant to the patient's condition
        - **Specific interventions** to implement doctor's orders
        - **Patient education** points
        - **Monitoring guidelines** for the shift
        - **Documentation reminders**
        
        ### Tips for Best Results:
        - Include specific medication orders with dosages
        - Mention any diagnostic tests ordered
        - Include monitoring requirements (vitals, I/O, etc.)
        - Note any dietary restrictions or activity orders
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("This tool assists with nursing documentation but does not replace clinical judgment. Always follow your facility's policies and procedures.")

if __name__ == "__main__":
    main()
