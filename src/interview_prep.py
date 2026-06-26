from src.chat import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

def generate_interview_questions(resume_text, job_role, provider="groq"):
    llm = get_llm(provider)
    messages = [
        SystemMessage(content="""You are an expert technical interviewer. 
        Generate exactly 5 interview questions based on the resume and job role provided.
        Format your response as a numbered list (1. 2. 3. 4. 5.)
        Mix technical and behavioral questions relevant to the role."""),
        HumanMessage(content=f"""
        Job Role: {job_role}
        
        Resume:
        {resume_text}
        
        Generate 5 interview questions for this candidate.
        """)
    ]
    response = llm.invoke(messages)
    print(response.content)
    return response.content

def evaluate_answer(question, user_answer, job_role, provider="groq"):
    llm = get_llm(provider)
    messages = [
        SystemMessage(content="""You are an experienced interviewer giving constructive feedback.
        Evaluate the candidate's answer and provide:
        1. Score (out of 10)
        2. What was good
        3. What could be improved
        4. A sample strong answer
        Keep feedback concise and encouraging."""),
        HumanMessage(content=f"""
        Job Role: {job_role}
        Question: {question}
        Candidate's Answer: {user_answer}
        
        Evaluate this answer.
        """)
    ]
    response = llm.invoke(messages)
    return response.content