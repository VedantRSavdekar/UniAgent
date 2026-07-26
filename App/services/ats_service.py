import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq

load_dotenv()


class ATSScoreResult(BaseModel):
    overall_score: int = Field(description="Overall ATS-readiness score, 0-100")
    format_score: int = Field(description="Format/structure parsing health score, 0-100")
    format_issues: list[str] = Field(description="Specific formatting problems found")
    keyword_match_score: Optional[int] = Field(default=None)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(description="Specific, actionable improvements")


def get_ats_score(resume_text: str, job_description: str = "", max_retries: int = 2) -> ATSScoreResult:
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

    base_prompt = (
        "You are an ATS compatibility analyzer. Evaluate on: "
        "1) FORMAT/STRUCTURE (always) 2) KEYWORD/CONTENT MATCH (only if JD given).\n"
        "CRITICAL: overall_score, format_score, keyword_match_score MUST be plain JSON "
        "integers (30, 45, 78) — NEVER words like 'thirty'.\n\n"
        f"RESUME TEXT:\n{resume_text}"
        f"{jd_section}\n\n"
        "Provide overall_score (0-100) and specific, actionable recommendations."
    )

    last_error = None
    for attempt in range(max_retries + 1):
        prompt = base_prompt
        if attempt > 0:
            prompt += (
                f"\n\nIMPORTANT: Your previous attempt failed because a score field "
                f"contained a word instead of a number. Error was: {last_error}. "
                f"Double-check every score is a plain integer digit before responding."
            )
        try:
            result: ATSScoreResult = llm.invoke(prompt)
            return result
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(f"ATS scoring failed after {max_retries + 1} attempts: {last_error}")