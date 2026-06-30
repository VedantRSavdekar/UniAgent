# ============================================================
# database.py - SQLite database layer for UniAgent
# Handles all database operations: creating tables, saving
# resumes/job matches/interview sessions, and retrieving history
# ============================================================

import sqlite3
import os

DB_PATH = "data/uniagent.db"

def init_db():
    """
    Creates the database file and all required tables if they
    don't already exist. Called once when the app starts.
    """
    os.makedirs("data", exist_ok=True)  # Ensure data/ folder exists (needed on Streamlit Cloud)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Stores parsed resume data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            skills TEXT,
            parsed_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Stores job match results, linked to a resume
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER,
            job_description TEXT,
            match_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    """)

    # Stores each interview Q&A session with AI feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        job_role TEXT,
        questions TEXT,
        user_answer TEXT,
        ai_feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def save_resume(name, email, skills, parsed_data):
    """Inserts a new resume record and returns its generated ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumes (name, email, skills, parsed_data)
        VALUES (?, ?, ?, ?)
    """, (name, email, skills, parsed_data))
    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id

def save_job_match(resume_id, job_description, match_result):
    """Inserts a new job match record linked to a resume"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_matches (resume_id, job_description, match_result)
        VALUES (?, ?, ?)
    """, (resume_id, job_description, match_result))
    conn.commit()
    conn.close()

def get_all_resumes():
    """Returns all saved resumes, most recent first"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC")
    resumes = cursor.fetchall()
    conn.close()
    return resumes

def get_job_matches(resume_id):
    """Returns all job matches for a specific resume, most recent first"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_matches WHERE resume_id=? ORDER BY created_at DESC", (resume_id,))
    matches = cursor.fetchall()
    conn.close()
    return matches

def save_interview_session(resume_id, job_role, questions, user_answer, ai_feedback):
    """Inserts a new interview Q&A session with AI feedback"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interview_sessions (resume_id, job_role, questions, user_answer, ai_feedback)
        VALUES (?, ?, ?, ?, ?)
    """, (resume_id, job_role, questions, user_answer, ai_feedback))
    conn.commit()
    conn.close()

def get_interview_sessions():
    """Returns all saved interview sessions, most recent first"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interview_sessions ORDER BY created_at DESC")
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_interview_stats():
    """
    Returns summary stats for the Interview Prep dashboard:
    - total_questions: total number of questions answered
    - total_sessions: number of distinct job roles practiced
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM interview_sessions")
    total_questions = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT job_role) FROM interview_sessions")
    total_sessions = cursor.fetchone()[0]
    conn.close()
    return {
        "total_sessions": total_sessions,
        "total_questions": total_questions,
    }