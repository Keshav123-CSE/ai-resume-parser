import streamlit as st
import re
import pdfplumber
import pandas as pd

st.set_page_config(page_title="AI Resume Parser", page_icon="📄", layout="wide")

SKILLS = [
    "C", "C++", "Java", "Python", "JavaScript", "HTML", "CSS",
    "React", "Node.js", "Express", "MongoDB", "MySQL", "SQL",
    "Git", "GitHub", "Machine Learning", "Data Structures",
    "Algorithms", "OOP", "DBMS", "OS", "Pandas", "NumPy"
]

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    match = re.search(r"(\+91[\-\s]?)?[6-9]\d{9}", text)
    return match.group(0) if match else "Not Found"

def extract_name(text):
    lines = text.split("\n")
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
            return line
    return "Not Found"

def extract_skills(text):
    found = []
    lower_text = text.lower()
    for skill in SKILLS:
        if skill.lower() in lower_text:
            found.append(skill)
    return list(set(found))

def ats_score(skills, text):
    score = 0

    if len(skills) >= 3:
        score += 30
    if len(skills) >= 6:
        score += 25
    if "project" in text.lower() or "projects" in text.lower():
        score += 15
    if "education" in text.lower():
        score += 10
    if "email" in text.lower() or extract_email(text) != "Not Found":
        score += 10
    if extract_phone(text) != "Not Found":
        score += 10

    return min(score, 100)

st.title("📄 AI Resume Parser & ATS Analyzer")
st.write("Upload a PDF resume to extract candidate details, skills, and a basic ATS score.")

uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Analyzing resume..."):
        text = extract_text_from_pdf(uploaded_file)

        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)
        score = ats_score(skills, text)

    st.success("Resume parsed successfully!")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Candidate Details")
        st.write("**Name:**", name)
        st.write("**Email:**", email)
        st.write("**Phone:**", phone)

    with col2:
        st.subheader("ATS Score")
        st.metric("Resume Score", f"{score}/100")

    st.subheader("Extracted Skills")

    if skills:
        df = pd.DataFrame(skills, columns=["Detected Skills"])
        st.table(df)
    else:
        st.warning("No technical skills detected.")

    st.subheader("Resume Improvement Suggestions")

    if score < 70:
        st.write("- Add more relevant technical skills.")
        st.write("- Mention projects clearly.")
        st.write("- Add measurable points in project descriptions.")
        st.write("- Keep resume ATS-friendly with simple formatting.")
    else:
        st.write("- Resume looks decent based on basic ATS checks.")
        st.write("- Improve project bullets with stronger action words.")

    with st.expander("Show Extracted Resume Text"):
        st.write(text)
