# ============================================================
# resume_parser.py - Resume text extraction and AI parsing
# Handles reading PDF/DOCX files and using LLM to extract
# structured data (name, email, skills, experience, education)
# ============================================================

import PyPDF2
import docx
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

def extract_text_from_pdf(file):
    """Reads a PDF file and extracts all text page by page"""
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    """Reads a DOCX file and extracts all text paragraph by paragraph"""
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def parse_resume(text, provider="groq"):
    """
    Sends raw resume text to the LLM and asks it to extract
    structured fields: Name, Email, Skills, Experience, Education
    """
    llm = get_llm(provider)
    message = HumanMessage(content=f"""Extract the following from this resume and return as structured text:
    - Full Name
    - Email
    - Skills (as a list)
    - Work Experience
    - Education
    
    Resume:
    {text}""")
    response = llm.invoke([message])
    return response.content