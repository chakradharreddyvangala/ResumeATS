import streamlit as st
import os
import json
import PyPDF2 as pdf
import plotly.graph_objects as go
from dotenv import load_dotenv
from groq import Groq

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="AI Resume ATS",
    page_icon="📄",
    layout="centered"
)

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Initialize Groq Client
# --------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --------------------------------------------------
# Circular ATS Match Indicator
# --------------------------------------------------
def show_match_circle(percentage):
    if percentage >= 80:
        color = "green"
    else:
        color = "red"

    fig = go.Figure(
        go.Pie(
            values=[percentage, 100 - percentage],
            hole=0.7,
            marker=dict(colors=[color, "#E0E0E0"]),
            textinfo="none"
        )
    )

    fig.update_layout(
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>{percentage}%</b>",
                x=0.5,
                y=0.5,
                font_size=36,
                showarrow=False
            )
        ],
        margin=dict(t=10, b=10, l=10, r=10)
    )

    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Call Groq LLM
# --------------------------------------------------
def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert ATS resume evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# --------------------------------------------------
# Extract text from PDF
# --------------------------------------------------
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
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
# UI
# --------------------------------------------------
st.title("📄 AI Resume ATS Analyzer")
st.markdown(
    "Analyze your resume against a job description using an AI-powered ATS engine. "
    "Get match percentage, missing keywords, and improvement suggestions."
)

jd = st.text_area("📌 Paste Job Description")
uploaded_file = st.file_uploader(
    "📎 Upload your resume (PDF only)",
    type=["pdf"],
    help="Upload resume in PDF format"
)

submit = st.button("🚀 Evaluate Resume")

# --------------------------------------------------
# Button Action
# --------------------------------------------------
if submit:
    if uploaded_file and jd:
        with st.spinner("🔍 Analyzing resume with ATS engine... Please wait"):
            resume_text = input_pdf_text(uploaded_file)
            final_prompt = input_prompt.format(text=resume_text, jd=jd)
            response = get_llm_response(final_prompt)

        # Parse JSON
        try:
            ats_result = json.loads(response)
        except:
            st.error("❌ Failed to parse ATS response. Try again.")
            st.stop()

        # JD Match Circle
        jd_match_str = ats_result.get("JD Match", "0%")
        jd_match = int(jd_match_str.replace("%", ""))

        st.subheader("📊 ATS Match Score")
        show_match_circle(jd_match)

        st.divider()

        # Profile Summary
        st.subheader("🧑‍💼 Profile Summary")
        st.write(ats_result.get("Profile Summary", ""))

        # Missing Keywords
        st.subheader("❌ Missing Keywords")
        missing = ats_result.get("Missing Keywords", [])
        if missing:
            for k in missing:
                st.markdown(f"- {k}")
        else:
            st.write("None 🎉")

        # ATS Suggestions
        st.subheader("🛠 ATS Improvement Suggestions")
        for s in ats_result.get("ATS Improvement Suggestions", []):
            st.markdown(f"- {s}")

        # Skills to Add / Replace
        st.subheader("📌 Skills or Experience to Add or Replace")
        for skill in ats_result.get("Skills or Experience to Add or Replace", []):
            st.markdown(f"- {skill}")

        # Final Guidance
        st.subheader("🚀 How to Make This a Top ATS Resume")
        st.write(ats_result.get("How to Make This a Top ATS Resume", ""))

    else:
        st.warning("⚠️ Please upload a resume AND paste a job description.")
