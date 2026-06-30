# ============================================================
# chat.py - Conversational AI assistant for resume Q&A
# Lets the user have a multi-turn chat about their resume
# and get career advice based on it
# ============================================================

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

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

def chat_with_resume(question, resume_text, chat_history=[], provider="groq"):
    """
    Handles a single chat turn: builds the message list (system
    prompt + chat history + new question) and gets an AI response.
    The resume text is injected into the system prompt so the AI
    always has context about the user's background.
    """
    llm = get_llm(provider)

    # System prompt gives the AI its role and the resume context
    messages = [
        SystemMessage(content=f"""You are a helpful job search assistant. 
        You have access to the user's resume below. Answer questions about it 
        and give career advice based on it.
        
        Resume:
        {resume_text}"""),
    ]

    # Add previous conversation turns to maintain context
    for msg in chat_history:
        messages.append(msg)

    # Add the new question
    messages.append(HumanMessage(content=question))

    response = llm.invoke(messages)
    return response.content