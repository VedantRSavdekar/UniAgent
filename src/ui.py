# ============================================================
# ui.py - Reusable UI components for UniAgent
# All HTML/CSS rendering functions are stored here to keep
# app.py clean and readable
# ============================================================

import streamlit as st

def render_upload_zone():
    """Renders a styled drag-and-drop upload zone above the file uploader"""
    st.markdown("""
        <div style="border: 1.5px solid #CECBF6; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: 0.5rem; background: #EEEDFE;">
            <span style="font-size: 24px;">📄</span>
            <p style="color: #534AB7; font-size: 13px; margin: 4px 0 0;">Drag and drop or click below to upload your resume</p>
            <p style="color: #AFA9EC; font-size: 11px; margin: 2px 0 0;">Supported formats: PDF, DOCX</p>
        </div>
    """, unsafe_allow_html=True)

def render_welcome_card():
    """Renders the purple welcome banner on the Home page"""
    st.markdown("""
        <div style="background:#EEEDFE; border-radius:16px; padding:2rem; margin-bottom:1.5rem;">
            <h2 style="color:#534AB7; margin-bottom:0.5rem;">👋 Welcome to UniAgent!</h2>
            <p style="color:#3C3489; font-size:15px; margin:0;">Your AI-powered job search companion. Upload your resume and let AI do the heavy lifting.</p>
        </div>
    """, unsafe_allow_html=True)

def render_feature_cards():
    """Renders the 3 feature cards (Resume Parser, Job Matcher, Interview Prep)"""
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

def render_stat_cards(stats):
    """Renders the 3 stat cards on the Interview Prep page"""
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

def render_progress_bar(idx, total):
    """Renders a custom purple progress bar for Interview Prep"""
    st.markdown(f"""
        <div style="background:#EEEDFE; border-radius:8px; height:8px; margin-bottom:12px;">
            <div style="background:#534AB7; width:{int((idx/total)*100)}%; height:8px; border-radius:8px; transition: width 0.3s ease;"></div>
        </div>
        <p style="font-size:12px; color:#534AB7; margin-bottom:8px;">{idx} of {total} questions completed</p>
    """, unsafe_allow_html=True)

def render_question_card(question):
    """Renders a styled question card with purple left border"""
    st.markdown(f"""
        <div style="border:1px solid #CECBF6; border-left:4px solid #534AB7; border-radius:12px; padding:16px 20px; margin-bottom:12px; background:linear-gradient(90deg, #EEEDFE 0%, #FFFFFF 100%);">
            <p style="font-size:16px; color:#3C3489; margin:0; font-weight:500;">{question}</p>
        </div>
    """, unsafe_allow_html=True)

def render_resume_card(resume):
    """Renders a styled card for a single resume in History page
    resume tuple: (id, name, email, skills, parsed_data, created_at)
    """
    st.markdown(f"""
        <div style="border:0.5px solid #CECBF6; border-radius:12px; padding:1rem 1.25rem; margin-bottom:1rem;">
            <div style="font-size:15px; font-weight:500; color:#534AB7;">👤 {resume[1]}</div>
            <div style="font-size:12px; color:#888780; margin-top:4px;">📧 {resume[2]}</div>
            <div style="font-size:12px; color:#888780; margin-top:2px;">🛠️ {resume[3]}</div>
            <div style="font-size:11px; color:#AFA9EC; margin-top:4px;">🕒 {resume[5]}</div>
        </div>
    """, unsafe_allow_html=True)

def render_session_card(session):
    """Renders a styled card for a single interview session in History page
    session tuple: (id, resume_id, job_role, questions, user_answer, ai_feedback, created_at)
    """
    st.markdown(f"""
        <div style="border:0.5px solid #CECBF6; border-left: 3px solid #534AB7; border-radius:12px; padding:1rem 1.25rem; margin-bottom:1rem;">
            <div style="font-size:15px; font-weight:500; color:#534AB7;">🎯 {session[2]}</div>
            <div style="font-size:12px; color:#444441; margin-top:6px;"><b>Q:</b> {session[3]}</div>
            <div style="font-size:12px; color:#444441; margin-top:4px;"><b>Your answer:</b> {session[4]}</div>
            <div style="font-size:11px; color:#AFA9EC; margin-top:4px;">🕒 {session[6]}</div>
        </div>
    """, unsafe_allow_html=True)