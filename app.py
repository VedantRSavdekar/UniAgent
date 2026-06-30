# ============================================================
# UniAgent - AI-Powered Job Search Assistant
# Built with Streamlit, LangChain, Groq, Gemini, and SQLite
# ============================================================

import streamlit as st
from dotenv import load_dotenv
import os
import sys
import sqlite3
from langchain_core.messages import HumanMessage, SystemMessage

# Add project root to path so we can import from src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from src.resume_parser import extract_text_from_pdf, extract_text_from_docx, parse_resume
from src.chat import chat_with_resume
from src.job_matcher import match_job
from src.database import init_db, save_resume, save_job_match, get_all_resumes, save_interview_session, get_interview_sessions, get_interview_stats
from src.ui import render_upload_zone, render_welcome_card, render_feature_cards, render_stat_cards, render_progress_bar, render_question_card, render_resume_card, render_session_card

# Initialize database (creates tables if they don't exist)
init_db()

# Load environment variables from .env file (API keys)
load_dotenv()

# ── Page Configuration ──────────────────────────────────────
st.set_page_config(
    page_title="UniAgent - Job Search Assistant",
    page_icon="🤖",
    layout="wide"
)

# Load custom CSS from static/style.css for purple theme styling
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── App Title ────────────────────────────────────────────────
st.title("🤖 UniAgent - Job Search Assistant")
st.subheader("Your AI-powered job search companion")

# ── Sidebar Navigation ───────────────────────────────────────
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "🏠  Home",
    "📄  Resume Parser",
    "💼  Job Matcher",
    "💬  Chat",
    "🎯  Interview Prep",
    "💾  History"
])

# ============================================================
# PAGE: HOME
# Shows welcome card and feature overview
# ============================================================
if page == "🏠  Home":
    render_welcome_card()
    render_feature_cards()
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Use the sidebar to navigate between features!")

# ============================================================
# PAGE: RESUME PARSER
# Uploads resume (PDF/DOCX), extracts text, parses with AI,
# and saves result to SQLite database
# ============================================================
elif page == "📄  Resume Parser":
    st.header("📄 Resume Parser")

    # Styled upload zone (decorative, actual upload below)
    render_upload_zone()

    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])

    if uploaded_file is not None:
        with st.spinner("Parsing your resume..."):
            # Extract raw text based on file type
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            else:
                text = extract_text_from_docx(uploaded_file)

            # Send text to LLM for structured parsing
            result = parse_resume(text)
            st.success("Resume parsed successfully!")
            st.write(result)

            # Save parsed resume to database
            save_resume(
                name="Vedant",
                email="vedant@email.com",
                skills="extracted from resume",
                parsed_data=result
            )
            st.success("Resume saved to database!")

# ============================================================
# PAGE: JOB MATCHER
# Compares resume against a job description using AI
# and returns a match analysis
# ============================================================
elif page == "💼  Job Matcher":
    st.header("💼 Job Matcher")

    # AI provider selection in sidebar (Groq = fast, Gemini = accurate)
    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])

    # Styled upload zone (decorative, actual upload below)
    render_upload_zone()

    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    job_desc = st.text_area("Paste Job Description here", height=200)

    if st.button("Match Job"):
        if uploaded_file and job_desc:
            with st.spinner("Analysing match..."):
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)

                # Run AI match analysis
                result = match_job(resume_text, job_desc, provider)
                st.success("Match Complete!")
                st.write(result)
        else:
            st.warning("Please upload resume and paste job description!")

# ============================================================
# PAGE: CHAT
# Loads resume into context and allows user to have a
# multi-turn conversation with the AI about their resume
# ============================================================
elif page == "💬  Chat":
    st.header("💬 Chat with your Resume")

    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])

    # Session state keeps chat history and resume text across reruns
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    # Styled upload zone (decorative, actual upload below)
    render_upload_zone()

    uploaded_file = st.file_uploader("Upload your resume first", type=["pdf", "docx"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
        else:
            st.session_state.resume_text = extract_text_from_docx(uploaded_file)
        st.success("Resume loaded!")

    # Display previous messages in chat format
    for msg in st.session_state.chat_history:
        role = "You" if isinstance(msg, HumanMessage) else "AI"
        st.chat_message(role).write(msg.content)

    # Handle new user input
    question = st.chat_input("Ask anything about your resume or job search...")
    if question and st.session_state.resume_text:
        from src.chat import chat_with_resume
        from langchain_core.messages import HumanMessage as HM
        st.chat_message("You").write(question)
        response = chat_with_resume(question, st.session_state.resume_text, st.session_state.chat_history, provider)
        st.session_state.chat_history.append(HM(content=question))
        st.chat_message("AI").write(response)

# ============================================================
# PAGE: INTERVIEW PREP
# Generates interview questions based on resume + job role,
# then evaluates user answers with AI feedback
# ============================================================
elif page == "🎯  Interview Prep":
    st.header("🎯  Interview Prep")

    # Show stats from previous interview sessions
    stats = get_interview_stats()
    render_stat_cards(stats)

    st.divider()

    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])

    from src.interview_prep import generate_interview_questions, evaluate_answer

    # Session state stores questions, current index, and resume text
    if "interview_questions" not in st.session_state:
        st.session_state.interview_questions = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "interview_resume_text" not in st.session_state:
        st.session_state.interview_resume_text = ""

    # Step 1: Upload resume and enter job role
    
    with st.container(border=True):
        # Styled upload zone (decorative, actual upload below)
        render_upload_zone()
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
        job_role = st.text_input("Enter Job Role (e.g. Python Developer, Data Analyst)")

        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                st.session_state.interview_resume_text = extract_text_from_pdf(uploaded_file)
            else:
                st.session_state.interview_resume_text = extract_text_from_docx(uploaded_file)
        

        if st.button("Generate Interview Questions"):
            if st.session_state.interview_resume_text and job_role:
                with st.spinner("Generating questions..."):
                    questions_text = generate_interview_questions(
                        st.session_state.interview_resume_text, job_role, provider
                    )
                    lines = questions_text.strip().split("\n")
                    questions = [l.strip() for l in lines if l.strip() and l[0].isdigit()]
                    st.session_state.interview_questions = questions
                    st.session_state.current_question_index = 0
                    st.session_state.job_role = job_role
            else:
                st.warning("Please upload resume and enter job role!")

    # Step 2: Show questions one by one and collect answers
    if st.session_state.interview_questions:
        st.divider()
        total = len(st.session_state.interview_questions)
        idx = st.session_state.current_question_index
  
        with st.container(border=True):
            # Custom progress bar showing completion percentage
            render_progress_bar(idx, total)

            st.markdown(f"**Question {idx + 1} of {total}**")
            current_q = st.session_state.interview_questions[idx]
            current_q = current_q.replace("*", "")

            render_question_card(current_q)

            user_answer = st.text_area("Your Answer", height=150, key=f"answer_{idx}")

            if st.button("Submit Answer"):
                if user_answer.strip():
                    with st.spinner("Evaluating your answer..."):
                        feedback = evaluate_answer(
                            current_q, user_answer,
                            st.session_state.get("job_role", ""),
                            provider
                        )
                        st.success("Feedback:")
                        st.write(feedback)

                        save_interview_session(
                            resume_id=1,
                            job_role=st.session_state.get("job_role", ""),
                            questions=current_q,
                            user_answer=user_answer,
                            ai_feedback=feedback
                        )

                        if idx + 1 < total:
                            st.session_state.current_question_index += 1
                            st.rerun()
                        else:
                            st.balloons()
                            st.success("🎉 You've completed all questions!")
                            st.session_state.interview_questions = []
                else:
                    st.warning("Please type your answer before submitting!")

# ============================================================
# PAGE: HISTORY
# Shows all saved resumes and interview sessions from SQLite
# ============================================================
elif page == "💾  History":
    st.header("💾  History")

    # Two tabs - one for resumes, one for interview sessions
    tab1, tab2 = st.tabs(["📄 Resumes", "🎯 Interview Sessions"])

    with tab1:
        resumes = get_all_resumes()
        if not resumes:
            st.info("No resumes found. Upload a resume first!")
        else:
            st.markdown(f"<p style='color:#534AB7; font-size:13px;'>Found {len(resumes)} resume(s)</p>", unsafe_allow_html=True)
            for resume in resumes:
                # resume tuple: (id, name, email, skills, parsed_data, created_at)
                render_resume_card(resume)
                with st.expander("View Parsed Data"):
                    st.text(resume[4])

        if st.button("🗑️ Clear Resume History"):
            conn = sqlite3.connect("data/uniagent.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resumes")
            cursor.execute("DELETE FROM job_matches")
            conn.commit()
            conn.close()
            st.success("Resume history cleared!")
            st.rerun()

    with tab2:
        sessions = get_interview_sessions()
        if not sessions:
            st.info("No interview sessions found. Practice first!")
        else:
            st.markdown(f"<p style='color:#534AB7; font-size:13px;'>Found {len(sessions)} session(s)</p>", unsafe_allow_html=True)
            for session in sessions:
                # session tuple: (id, resume_id, job_role, questions, user_answer, ai_feedback, created_at)
                render_session_card(session)
                with st.expander("View AI Feedback"):
                    st.write(session[5])

        if st.button("🗑️ Clear Interview History"):
            conn = sqlite3.connect("data/uniagent.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM interview_sessions")
            conn.commit()
            conn.close()
            st.success("Interview history cleared!")
            st.rerun()