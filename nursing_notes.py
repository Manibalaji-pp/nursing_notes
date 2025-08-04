import streamlit as st
import openai

# Use Streamlit secrets for security
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("AI-Powered Nursing Notes Generator")
st.write("Follow telemedicine and nursing protocols for patient care documentation.")

# Input fields for patient information
diagnosis = st.text_input("Diagnosis")
history = st.text_area("Patient History")
condition = st.text_area("Current Patient Condition")

# Combine inputs for AI prompt
patient_data = f"""
Diagnosis: {diagnosis}
Patient History: {history}
Current Condition: {condition}
"""

if st.button("Generate Nursing Notes"):
    if patient_data.strip():
        prompt = f"""
You are a professional telemedicine nurse. Based on the following patient information,
generate nursing notes following standard nursing responsibilities and telemedicine documentation protocols.

{patient_data}

Nursing Notes:
"""
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        # Display AI-generated nursing notes
        nursing_notes = response["choices"][0]["message"]["content"]
        st.subheader("AI-Generated Nursing Notes")
        st.text_area("Nursing Notes", nursing_notes, height=300)
    else:
        st.warning("Please enter all patient details first.")
