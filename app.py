import streamlit as st
from dotenv import load_dotenv
import os
import sys
import sqlite3
from langchain_core.messages import HumanMessage, SystemMessage

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.resume_parser import extract_text_from_pdf, extract_text_from_docx, parse_resume
from src.chat import chat_with_resume
from src.job_matcher import match_job
from src.database import init_db, save_resume, save_job_match, get_all_resumes

init_db()
load_dotenv()

st.set_page_config(
    page_title="UniAgent - Job Search Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 UniAgent - Job Search Assistant")
st.subheader("Your AI-powered job search companion")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Resume Parser", "Job Matcher", "Chat", "History"])

if page == "Home":
    st.write("Welcome to UniAgent! Upload your resume to get started.")
    st.info("👈 Use the sidebar to navigate")

elif page == "Resume Parser":
    st.header("📄 Resume Parser")
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        with st.spinner("Parsing your resume..."):
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_docx(uploaded_file)
            
            result = parse_resume(text)
            st.success("Resume parsed successfully!")
            st.write(result)

            save_resume(
                name="Vedant",
                email="vedant@email.com",
                skills="extracted from resume",
                parsed_data=result
            )
            st.success("Resume saved to database!")

elif page == "Job Matcher":
    st.header("💼 Job Matcher")
    
    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])
    
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    job_desc = st.text_area("Paste Job Description here", height=200)
    
    if st.button("Match Job"):
        if uploaded_file and job_desc:
            with st.spinner("Analysing match..."):
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)
                
                result = match_job(resume_text, job_desc, provider)
                st.success("Match Complete!")
                st.write(result)
        else:
            st.warning("Please upload resume and paste job description!")

elif page == "Chat":
    st.header("💬 Chat with your Resume")
    
    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    uploaded_file = st.file_uploader("Upload your resume first", type=["pdf", "docx"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
        else:
            st.session_state.resume_text = extract_text_from_docx(uploaded_file)
        st.success("Resume loaded!")

    for msg in st.session_state.chat_history:
        role = "You" if isinstance(msg, HumanMessage) else "AI"
        st.chat_message(role).write(msg.content)

    question = st.chat_input("Ask anything about your resume or job search...")
    if question and st.session_state.resume_text:
        from src.chat import chat_with_resume
        from langchain_core.messages import HumanMessage as HM
        st.chat_message("You").write(question)
        response = chat_with_resume(question, st.session_state.resume_text, st.session_state.chat_history, provider)
        st.session_state.chat_history.append(HM(content=question))
        st.chat_message("AI").write(response)

elif page == "History":
    st.header("💾 History")
    resumes = get_all_resumes()
    if not resumes:
        st.info("No resumes found. Upload a resume first!")
    else:
        st.write(f"Found {len(resumes)} resumes")
        
        # Simple display
        for resume in resumes:
            st.subheader(resume[1]) # name
            st.write(f"Email: {resume[2]}") # email
            st.write(f"Skills: {resume[3]}") # skills
            with st.expander("Parsed Data"):
                st.text(resume[4])
            st.divider()
    
    if st.button("🗑️ Clear All History"):
        conn = sqlite3.connect("data/uniagent.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resumes")
        cursor.execute("DELETE FROM job_matches")
        conn.commit()
        conn.close()
        st.success("History cleared!")
        st.rerun()