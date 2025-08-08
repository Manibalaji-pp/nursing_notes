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

def build_prompt(doctor_notes, nursing_observations):
    """Build the AI prompt text for display and editing."""
    return f"""
Prompt for AI Model: Nursing Follow-Up Note Generation

Role and Goal: You are an expert Intensive Care Unit (ICU) nurse. Your task is to generate a comprehensive nursing follow-up note based on a given doctor's order note and the provided medical protocols. Your note should be insightful, detailed, and directly relevant to the patient's care plan as outlined in the protocols.

Input:
• Doctor's Order Note: {doctor_notes}
- Nurse's Observations of the patient condition (optional): {nursing_observations}

Output Format: Generate a nursing follow-up note with the following sections, using bullet points for clarity where appropriate:
• Patient Status (Overall Assessment):
    ◦ General appearance and mentation (e.g., awake, alert, agitated, sedated, GCS, RASS scale, any changes).
    ◦ Pain assessment and current pain level (using BPS/CPOT scale if non-verbal/intubated, or self-report).
    ◦ Current level of activity and mobility.
    - Keep the patient status inference to a sentence.
- Nursing Diagnoses:
    - If there are any acute changes in the patient's condition, then highlight them in the nursing diagnoses.
    - Use bullet points, and medical conventions.
• Follow up on To-do
    - Doctor's note may end with a to-do list. If yes, your goal is to convert them into simple and actionable items.
    - At max give 3 actionable items for each of the to-do list items. Keep the language simple and concise. 
    - All instructions are to be based on NANDA-I (North American Nursing Diagnosis Association International) protocols (https://www.ncbi.nlm.nih.gov/books/NBK591814/)
    - Be very precise in the instructions.
    - Use bullet points, and medical conventions.
    - If there are any indications of invasive lines, propose the relevant infection care bundles - CLABSI, CAUTI, VAP and SSI.
    - If any medicines are suggested, explain how it can be administered in simple steps.
- Infection Bundles (optional)
    - If invasive lines are suggested in the doctor's notes, then Infection Bundle Care is mandatory. Following bundles cares are present - CLABSI, CAUTI, VAP, SSI

Instructions for the AI Model:
1. Prioritize: Focus on critical parameters, ordered interventions, and patient responses directly relevant to the doctor's orders and the patient's primary diagnoses as implied by the protocols.
2. Detail & Contextualize: Do not just list data. Explain the significance of the findings (e.g., "Blood glucose decreasing by 65 mg/dL/hr, indicating good response to insulin infusion").
3. Cross-Reference Protocols: Synthesize information from relevant protocols (e.g., if a DKA patient is also on mechanical ventilation, incorporate elements from both DKA and ARDS/Ventilation protocols).
4. Citing (Self-Reference): Do not directly cite within the nursing note. However, ensure the content is directly supported by the information within the provided sources.
5. Be Comprehensive but Concise: Include all pertinent details without unnecessary verbosity. 
6. Do not include any information that is not relevant or directly related to the doctor's orders.
7. Standard Protocols: NANDA-I (North American Nursing Diagnosis Association International) to be adhered to, especially for the follow ups.
8. Format: Give appropirate spacing between the sections. If any doctor's to-list has spelling or formatting errors, then correct them. Use bullet points.
9. Salutations: Directly jump into the note without any salutations or messaging before AI output.
"""

def generate_nursing_note(prompt, model):
    """Send prompt to Gemini and get nursing note."""
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
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Doctor's Notes Input")
        doctor_notes = st.text_area(
            "Enter the doctor's notes, orders, and treatment plans:",
            height=200
        )

        st.header("📝 Nursing Observations")
        nursing_observations = st.text_area(
            "Enter your observations of the patient since the doctor's note, if any:",
            height=200
        )

    with col2:
        st.header("📋 Generated Nursing Notes")
        
        if st.button("🔄 Generate Nursing Notes", type="primary", use_container_width=True):
            if not doctor_notes.strip():
                st.warning("⚠️ Please enter doctor's notes to generate nursing documentation.")
            else:
                # Build and show prompt
                default_prompt = build_prompt(doctor_notes, nursing_observations)
                with st.expander("🔍 Review & Edit Prompt Before Sending to AI"):
                    edited_prompt = st.text_area("Edit Prompt", value=default_prompt, height=400)
                
                with st.spinner("Generating comprehensive nursing notes..."):
                    model = initialize_gemini()
                    nursing_notes = generate_nursing_note(edited_prompt, model)
                    
                    if nursing_notes:
                        st.markdown("### Generated Nursing Notes")
                        st.markdown(nursing_notes)
                        
                        # Download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"nursing_notes_{timestamp}.txt"
                        
                        download_content = f"""NURSING NOTES
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DOCTOR'S NOTES:
{doctor_notes}

NURSING OBSERVATIONS:
{nursing_observations}

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
    
    with st.expander("ℹ️ How to Use This Tool"):
        st.markdown("""
        ### Instructions:
        1. Enter doctor's notes and optional nursing observations
        2. Review & edit the generated prompt in the expander if needed
        3. Click "Generate Nursing Notes"
        4. Download the generated notes
        """)

    st.markdown("---")
    st.markdown("This tool assists with nursing documentation but does not replace clinical judgment.")

if __name__ == "__main__":
    main()
