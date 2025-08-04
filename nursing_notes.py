import streamlit as st
from openai import OpenAI

# Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit UI
st.title("Nursing Notes Assistant")
st.write("Enter your patient details or prompts below, and the AI will help you generate nursing notes.")

# Input box for user prompt
prompt = st.text_area("Enter your patient details / prompt:", height=200)

# Button to generate nursing notes
if st.button("Generate Nursing Notes"):
    if prompt.strip() == "":
        st.warning("Please enter some patient details or a prompt.")
    else:
        try:
            # New API call
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Extract AI's response
            nursing_notes = response.choices[0].message.content
            st.subheader("Generated Nursing Notes:")
            st.write(nursing_notes)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
