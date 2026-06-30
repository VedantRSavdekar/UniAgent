# ============================================================
# job_matcher.py - AI-powered resume vs job description matcher
# Compares a resume to a job description and returns a match
# score, skill gaps, and improvement suggestions
# ============================================================

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

def get_llm(provider="groq"):
    """Returns an LLM instance based on chosen provider (Groq or Gemini)"""
    if provider == "groq":
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-8b-instant"
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GEMINI_API_KEY"),
            model="gemini-1.5-flash"
        )

def match_job(resume_text, job_description, provider="groq"):
    """
    Sends resume + job description to the LLM and asks it to
    return a match score, matching/missing skills, and tips
    """
    llm = get_llm(provider)
    message = HumanMessage(content=f"""Compare this resume with the job description and provide:
    1. Match Score (out of 100)
    2. Matching Skills
    3. Missing Skills
    4. Overall Assessment
    5. Tips to improve chances
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}""")
    response = llm.invoke([message])
    return response.content