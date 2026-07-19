import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq

load_dotenv()


class ATSScoreResult(BaseModel):
    overall_score: int = Field(description="Overall ATS-readiness score, 0-100")
    format_score: int = Field(description="Format/structure parsing health score, 0-100")
    format_issues: list[str] = Field(description="Specific formatting problems found (e.g. tables, missing sections, images)")
    keyword_match_score: Optional[int] = Field(
        default=None, description="Keyword match score vs job description, 0-100. Null if no JD provided."
    )
    matched_keywords: list[str] = Field(default_factory=list, description="Relevant keywords found in the resume")
    missing_keywords: list[str] = Field(default_factory=list, description="Important keywords missing from the resume")
    recommendations: list[str] = Field(description="Specific, actionable improvements")


def get_ats_score(resume_text: str, job_description: str = "") -> ATSScoreResult:
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.1,
        max_tokens=2048,
        api_key=os.getenv("GROQ_API_KEY"),
    ).with_structured_output(ATSScoreResult)

    jd_section = (
        f"\n\nJOB DESCRIPTION TO MATCH AGAINST:\n{job_description}"
        if job_description.strip()
        else "\n\nNo job description provided — skip keyword_match_score, matched_keywords, and missing_keywords (leave empty/null)."
    )

    prompt = (
        "You are an ATS (Applicant Tracking System) compatibility analyzer. "
        "Evaluate the resume text below on TWO dimensions:\n\n"
        "1. FORMAT/STRUCTURE (always evaluate this):\n"
        "   - Standard section headers present (Experience, Education, Skills, etc)\n"
        "   - No evidence of tables/columns/text boxes that could break ATS parsing\n"
        "   - Consistent date formats\n"
        "   - No reliance on images/graphics for key text\n"
        "   Score this 0-100 as format_score, list specific issues in format_issues.\n\n"
        "2. KEYWORD/CONTENT MATCH (only if a job description is given below):\n"
        "   - Compare resume content against the job description's key requirements\n"
        "   - Identify matched and missing keywords/skills\n\n"
        "CRITICAL: All score fields (overall_score, format_score, keyword_match_score) "
        "MUST be plain integers written as digits (e.g. 30, 45, 78) — "
        "NEVER spell out numbers as words (e.g. do NOT write 'thirty', write 30).\n\n"
        f"RESUME TEXT:\n{resume_text}"
        f"{jd_section}\n\n"
        "Provide an overall_score (0-100) that reflects both dimensions combined "
        "(weight format more heavily if no JD is given), plus specific, actionable "
        "recommendations."
    )

    result: ATSScoreResult = llm.invoke(prompt)
    return result