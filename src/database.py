import sqlite3
import os

DB_PATH = "data/uniagent.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()

def save_resume(name, email, skills, parsed_data):
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_matches (resume_id, job_description, match_result)
        VALUES (?, ?, ?)
    """, (resume_id, job_description, match_result))
    conn.commit()
    conn.close()

def get_all_resumes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC")
    resumes = cursor.fetchall()
    conn.close()
    return resumes

def get_job_matches(resume_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_matches WHERE resume_id=? ORDER BY created_at DESC", (resume_id,))
    matches = cursor.fetchall()
    conn.close()
    return matches