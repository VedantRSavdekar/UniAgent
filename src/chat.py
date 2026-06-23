import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

def get_llm(provider="groq"):
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
    llm = get_llm(provider)
    messages = [
        SystemMessage(content=f"""You are a helpful job search assistant. 
        You have access to the user's resume below. Answer questions about it 
        and give career advice based on it.
        
        Resume:
        {resume_text}"""),
    ]
    for msg in chat_history:
        messages.append(msg)
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    return response.content