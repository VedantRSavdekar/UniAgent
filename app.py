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
from src.database import init_db, save_resume, save_job_match, get_all_resumes, save_interview_session, get_interview_sessions

init_db()
load_dotenv()

st.set_page_config(
    page_title="UniAgent - Job Search Assistant",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #222124;
    border-right: 0.5px solid #CECBF6;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 14px;
    color: #444441;
    padding: 6px 10px;
    border-radius: 8px;
    display: block;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #EEEDFE;
    color: #534AB7;
}

/* Main background */
.stApp {
    background-color: #222124;
}

/* Buttons */
.stButton > button {
    background-color: #534AB7;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
}
.stButton > button:hover {
    background-color: #3C3489;
    color: white;
}

/* Cards / expanders */
[data-testid="stExpander"] {
    border: 0.5px solid #CECBF6;
    border-radius: 12px;
}

/* Input fields */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border: 0.5px solid #CECBF6;
    border-radius: 8px;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #534AB7;
    box-shadow: 0 0 0 2px #EEEDFE;
}

/* Success messages */
.stSuccess {
    background-color: #E1F5EE;
    color: #0F6E56;
    border-radius: 8px;
}

/* Info messages */
.stInfo {
    background-color: #EEEDFE;
    color: #534AB7;
    border-radius: 8px;
}

/* Divider */
hr {
    border-color: #CECBF6;
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
    st.header("🏠 Home")
    st.write("Welcome to UniAgent! Upload your resume to get started.")
    st.info("👈 Use the sidebar to navigate")

elif page == "📄  Resume Parser":
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

elif page == "💼  Job Matcher":
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

elif page == "💬  Chat":
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

elif page == "💾 History":
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

elif page == "🎯 Interview Prep":
    st.header("🎯 Interview Prep")

    provider = st.sidebar.selectbox("Choose AI Provider", ["groq", "gemini"])

    from src.interview_prep import generate_interview_questions, evaluate_answer

    if "interview_questions" not in st.session_state:
        st.session_state.interview_questions = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "interview_resume_text" not in st.session_state:
        st.session_state.interview_resume_text = ""

    # Step 1: Upload resume + enter job role
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

        st.progress((idx) / total)
        st.markdown(f"**Question {idx + 1} of {total}**")
        current_q = st.session_state.interview_questions[idx]
        st.info(current_q)

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
    