import streamlit as st
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
from groq import Groq

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Initialize Groq Client
# --------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# Function: Call Groq LLM
# --------------------------------------------------
def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert ATS resume evaluator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# --------------------------------------------------
# Function: Extract text from uploaded PDF
# --------------------------------------------------
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
    return text

# --------------------------------------------------
# Prompt Template
# --------------------------------------------------
input_prompt = """
You are a highly experienced ATS (Applicant Tracking System) with deep expertise in:
.NET development, Full Stack development, Frontend, Backend, and Databases.

Your task is to evaluate the resume against the provided job description.
Assume the job market is extremely competitive and ATS filtering standards are high.

Analyze the resume and provide the following:

1. Overall JD match percentage
2. Missing or weak keywords
3. Professional profile summary
4. ATS optimization suggestions
5. Skills or experience to add or replace
6. Clear guidance to make this a top-tier ATS-optimized resume

Resume:
{text}

Job Description:
{jd}

Return the response strictly in the following JSON format (single string):

{{
  "JD Match": "%",
  "Missing Keywords": [],
  "Profile Summary": "",
  "ATS Improvement Suggestions": [],
  "Skills or Experience to Add or Replace": [],
  "How to Make This a Top ATS Resume": ""
}}
"""

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.title("AI Resume ATS Evaluator")
st.write("Analyze your resume against a job description using an AI-powered ATS system.")

jd = st.text_area("Paste Job Description")
uploaded_file = st.file_uploader(
    "Upload your resume (PDF only)",
    type=["pdf"],
    help="Please upload your resume in PDF format"
)

submit = st.button("Evaluate Resume")

# --------------------------------------------------
# Button Action
# --------------------------------------------------
if submit:
    if uploaded_file and jd.strip():
        resume_text = input_pdf_text(uploaded_file)

        final_prompt = input_prompt.format(
            text=resume_text,
            jd=jd
        )

        with st.spinner("Evaluating resume using AI ATS..."):
            response = get_llm_response(final_prompt)

        st.subheader("ATS Evaluation Result")
        st.write(response)

    else:
        st.warning("Please upload a resume and paste a job description.")
