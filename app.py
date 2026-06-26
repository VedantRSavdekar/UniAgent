from PIL import GifImagePlugin
from PIL import GifImagePlugin
from PIL import GifImagePlugin
from PIL import GifImagePlugin
from PIL import GifImagePlugin
from PIL import GifImagePlugin
from PIL import GifImagePlugin
from PIL import GifImagePlugin
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
from src.database import init_db, save_resume, save_job_match, get_all_resumes, save_interview_session, get_interview_sessions, get_interview_stats

init_db()
load_dotenv()

st.set_page_config(
    page_title="UniAgent - Job Search Assistant",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #EEEDFE !important;
    border-right: 0.5px solid #CECBF6 !important;
}

/* Buttons */
.stButton > button {
    background-color: #534AB7 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    background-color: #3C3489 !important;
    color: white !important;
}

/* Input fields */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border: 0.5px solid #CECBF6 !important;
    border-radius: 8px !important;
}

/* Expanders */
[data-testid="stExpander"] {
    border: 0.5px solid #CECBF6 !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 UniAgent - Job Search Assistant")
st.subheader("Your AI-powered job search companion")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "🏠  Home",
    "📄  Resume Parser", 
    "💼  Job Matcher",
    "💬  Chat",
    "🎯  Interview Prep",
    "💾  History"
])

if page == "🏠  Home":
    st.markdown("""
        <div style="background:#EEEDFE; border-radius:16px; padding:2rem; margin-bottom:1.5rem;">
            <h2 style="color:#534AB7; margin-bottom:0.5rem;">👋 Welcome to UniAgent!</h2>
            <p style="color:#3C3489; font-size:15px; margin:0;">Your AI-powered job search companion. Upload your resume and let AI do the heavy lifting.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div style="border:0.5px solid #CECBF6; border-radius:12px; padding:1rem; text-align:center;">
                <div style="font-size:28px;">📄</div>
                <div style="font-weight:500; color:#534AB7; margin:8px 0 4px;">Resume Parser</div>
                <div style="font-size:12px; color:#888780;">Extract key info from your resume instantly</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style="border:0.5px solid #CECBF6; border-radius:12px; padding:1rem; text-align:center;">
                <div style="font-size:28px;">💼</div>
                <div style="font-weight:500; color:#534AB7; margin:8px 0 4px;">Job Matcher</div>
                <div style="font-size:12px; color:#888780;">Match your resume to any job description</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div style="border:0.5px solid #CECBF6; border-radius:12px; padding:1rem; text-align:center;">
                <div style="font-size:28px;">🎯</div>
                <div style="font-weight:500; color:#534AB7; margin:8px 0 4px;">Interview Prep</div>
                <div style="font-size:12px; color:#888780;">Practice with AI generated questions</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Use the sidebar to navigate between features!")

elif page == "📄  Resume Parser":
    st.header("📄 Resume Parser")

    st.markdown("""
        <div style="border: 1.5px dashed #AFA9EC; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 0.5rem; background: #EEEDFE;">
            <span style="font-size: 24px;">📄</span>
            <p style="color: #534AB7; font-size: 13px; margin: 4px 0 0;">Drag and drop or click below to upload your resume</p>
            <p style="color: #AFA9EC; font-size: 11px; margin: 2px 0 0;">Supported formats: PDF, DOCX</p>
        </div>
    """, unsafe_allow_html=True)
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

elif page == "💼  Job Matcher":
    st.header("💼 Job Matcher")
    
    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])
    
    st.markdown("""
        <div style="border: 1.5px dashed #AFA9EC; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 0.5rem; background: #EEEDFE;">
            <span style="font-size: 24px;">📄</span>
            <p style="color: #534AB7; font-size: 13px; margin: 4px 0 0;">Drag and drop or click below to upload your resume</p>
            <p style="color: #AFA9EC; font-size: 11px; margin: 2px 0 0;">Supported formats: PDF, DOCX</p>
        </div>
    """, unsafe_allow_html=True)

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

elif page == "💬  Chat":
    st.header("💬 Chat with your Resume")
    
    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    st.markdown("""
        <div style="border: 1.5px dashed #AFA9EC; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 0.5rem; background: #EEEDFE;">
            <span style="font-size: 24px;">📄</span>
            <p style="color: #534AB7; font-size: 13px; margin: 4px 0 0;">Drag and drop or click below to upload your resume</p>
            <p style="color: #AFA9EC; font-size: 11px; margin: 2px 0 0;">Supported formats: PDF, DOCX</p>
        </div>
    """, unsafe_allow_html=True)

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

elif page == "🎯  Interview Prep":
    st.header("🎯  Interview Prep")

    stats = get_interview_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div style="background:#EEEDFE; padding:1rem; border-radius:12px; text-align:center;">
                <div style="font-size:12px; color:#534AB7; margin-bottom:4px;">Sessions done</div>
                <div style="font-size:28px; font-weight:500; color:#534AB7;">{}</div>
            </div>
        """.format(stats["total_sessions"]), unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style="background:#E1F5EE; padding:1rem; border-radius:12px; text-align:center;">
                <div style="font-size:12px; color:#0F6E56; margin-bottom:4px;">Questions answered</div>
                <div style="font-size:28px; font-weight:500; color:#0F6E56;">{}</div>
            </div>
        """.format(stats["total_questions"]), unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div style="background:#FAECE7; padding:1rem; border-radius:12px; text-align:center;">
                <div style="font-size:12px; color:#993C1D; margin-bottom:4px;">Avg score</div>
                <div style="font-size:28px; font-weight:500; color:#993C1D;">—</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])

    from src.interview_prep import generate_interview_questions, evaluate_answer

    if "interview_questions" not in st.session_state:
        st.session_state.interview_questions = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "interview_resume_text" not in st.session_state:
        st.session_state.interview_resume_text = ""

    # Step 1: Upload resume + enter job role
    st.markdown("""
        <div style="border: 1.5px dashed #AFA9EC; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 0.5rem; background: #EEEDFE;">
            <span style="font-size: 24px;">📄</span>
            <p style="color: #534AB7; font-size: 13px; margin: 4px 0 0;">Drag and drop or click below to upload your resume</p>
            <p style="color: #AFA9EC; font-size: 11px; margin: 2px 0 0;">Supported formats: PDF, DOCX</p>
        </div>
    """, unsafe_allow_html=True)
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
                # Parse into list
                lines = questions_text.strip().split("\n")
                questions = [l.strip() for l in lines if l.strip() and l[0].isdigit()]
                st.session_state.interview_questions = questions
                st.session_state.current_question_index = 0
                st.session_state.job_role = job_role
        else:
            st.warning("Please upload resume and enter job role!")

    # Step 2: Practice Q&A
    if st.session_state.interview_questions:
        st.divider()
        total = len(st.session_state.interview_questions)
        idx = st.session_state.current_question_index

        st.markdown(f"""
        <div style="background:#EEEDFE; border-radius:8px; height:8px; margin-bottom:12px;">
            <div style="background:#534AB7; width:{int((idx/total)*100)}%; height:8px; border-radius:8px; transition: width 0.3s ease;"></div>
        </div>
        <p style="font-size:12px; color:#534AB7; margin-bottom:8px;">{idx} of {total} questions completed</p>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Question {idx + 1} of {total}**")
        current_q = st.session_state.interview_questions[idx]
        current_q = current_q.replace("*", "")
        print(current_q)

        # Custom styled question card
        st.markdown(f"""
        <div style="border:1px solid #CECBF6; border-left:4px solid #534AB7; border-radius:12px; padding:16px 20px; margin-bottom:12px; background:linear-gradient(90deg, #EEEDFE 0%, #FFFFFF 100%);">
            <p style="font-size:16px; color:#3C3489; margin:0; font-weight:500;">{current_q}</p>
        </div>
        """, unsafe_allow_html=True)

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

elif page == "💾  History":
    st.header("💾  History")

    tab1, tab2 = st.tabs(["📄 Resumes", "🎯 Interview Sessions"])

    with tab1:
        resumes = get_all_resumes()
        if not resumes:
            st.info("No resumes found. Upload a resume first!")
        else:
            st.markdown(f"<p style='color:#534AB7; font-size:13px;'>Found {len(resumes)} resume(s)</p>", unsafe_allow_html=True)
            for resume in resumes:
                st.markdown(f"""
                    <div style="border:0.5px solid #CECBF6; border-radius:12px; padding:1rem 1.25rem; margin-bottom:1rem;">
                        <div style="font-size:15px; font-weight:500; color:#534AB7;">👤 {resume[1]}</div>
                        <div style="font-size:12px; color:#888780; margin-top:4px;">📧 {resume[2]}</div>
                        <div style="font-size:12px; color:#888780; margin-top:2px;">🛠️ {resume[3]}</div>
                        <div style="font-size:11px; color:#AFA9EC; margin-top:4px;">🕒 {resume[5]}</div>
                    </div>
                """, unsafe_allow_html=True)
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
                st.markdown(f"""
                    <div style="border:0.5px solid #CECBF6; border-left: 3px solid #534AB7; border-radius:12px; padding:1rem 1.25rem; margin-bottom:1rem;">
                        <div style="font-size:15px; font-weight:500; color:#534AB7;">🎯 {session[2]}</div>
                        <div style="font-size:12px; color:#444441; margin-top:6px;"><b>Q:</b> {session[3]}</div>
                        <div style="font-size:12px; color:#444441; margin-top:4px;"><b>Your answer:</b> {session[4]}</div>
                        <div style="font-size:11px; color:#AFA9EC; margin-top:4px;">🕒 {session[6]}</div>
                    </div>
                """, unsafe_allow_html=True)
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