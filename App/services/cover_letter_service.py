import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

load_dotenv()


def generate_cover_letter(
    career_report: str,
    job_description: str = "",
    company_name: str = "",
) -> str:
    """
    Generates a tailored cover letter based on the candidate's career report,
    and optionally a specific job description / company name for customization.
    """
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.4,
        max_tokens=1024,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    jd_section = (
        f"\n\nTARGET JOB DESCRIPTION:\n{job_description}"
        if job_description.strip()
        else "\n\nNo specific job description provided — write a general but professional cover letter."
    )
    company_section = f"\n\nTARGET COMPANY: {company_name}" if company_name.strip() else ""

    system_prompt = SystemMessage(content=(
        "You are a professional cover letter writer. Write a concise, professional "
        "cover letter (3-4 short paragraphs) based on the candidate's career report below. "
        "Tone: formal and professional. Do not invent facts not present in the career report. "
        "Do not include placeholder brackets like [Company Name] if a company name is given — "
        "use it directly. If no company is given, keep it generic but professional.\n\n"
        f"CANDIDATE CAREER REPORT:\n{career_report}"
        f"{jd_section}"
        f"{company_section}"
    ))

    response = llm.invoke([system_prompt])
    return response.content