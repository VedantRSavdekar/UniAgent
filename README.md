# UniAgent — AI Career Assistant

UniAgent is a multi-agent AI system that evaluates a candidate's resume and
automatically searches for matching live job postings — built as part of the
Agentic AI Saksham Internship project.

## Architecture

Two specialized agents connected via a LangGraph workflow:

    1. **Career Assessment Agent** — retrieves resume data using a RAG pipeline
        (Chroma + Gemini embeddings) and produces a structured career evaluation report.
    2. **Job Search Agent** — takes the evaluation report, extracts a target role,
        and searches live job postings via the JSearch API (LinkedIn, Indeed,
        Glassdoor, Naukri aggregated).

Resume PDF → RAG (Chroma + Gemini embeddings)
→ Career Assessment Agent → Career Report
→ Job Search Agent → Live Job Matches

## Tech Stack

- **Orchestration:** LangGraph
- **LLM:** Groq (openai/gpt-oss-120b)
- **Embeddings:** Google Generative AI (gemini-embedding-001)
- **Vector DB:** Chroma
- **Job Search API:** JSearch (via RapidAPI)
- **Language:** Python

## Project Structure
    UniAgent/
        ├── App/
        │   ├── agents/
        │   │   ├── career_assessment_agent.py
        │   │   └── job_search_agent.py
        │   ├── services/
        │   │   └── rag_service.py
        │   └── workflow/
        │       └── workflow.py
        ├── Assets/
        │   └── (resume PDF — not committed)
        ├── resume_vector_db/ (generated locally — not committed)
        ├── .gitignore
        ├── requirements.txt
        └── README.md

## How It Works

    1. The user's resume is loaded, chunked, and embedded into a local Chroma
        vector database.
    2. The **Career Assessment Agent** queries this vector store via a
        `get_resume_data` tool to ground its output in the candidate's actual
        resume content, then produces a `CANDIDATE CAREER EVALUATION REPORT`
        covering profile summary, strengths, and career fit.
    3. This report is handed off to the **Job Search Agent**, which extracts a
        concise target role and calls a `search_jobs` tool that queries the
        JSearch API for live postings matching that role in India.
    4. The final output combines the career assessment with real, currently
        open job postings and tailored recommendations.

## Setup

    1. Clone the repo and create a virtual environment:
        python -m venv venv
        venv\Scripts\activate
        pip install -r requirements.txt

    2. Create a `.env` file in the project root:
        GROQ_API_KEY=your_groq_key
        GEMINI_API_KEY=your_gemini_key
        RAPIDAPI_KEY=your_rapidapi_key

    3. Place your resume PDF in `Assets/` and update the file path in
        `rag_service.py` if needed.

    4. Generate resume embeddings (one-time step, run whenever the resume changes):
        python -m App.services.rag_service

    5. Run the full workflow:
        python -m App.workflow.workflow

## Example Output

Running the workflow produces:
- A structured career evaluation report (education, skills, strengths, career fit)
- A list of live, matching job postings with company, location, and apply links
- Personalized recommendations (resume improvements, target job titles, next steps)

## Current Status

- ✅ RAG-based resume parsing (Chroma + Gemini embeddings)
- ✅ Career evaluation report generation
- ✅ Live job search integration (JSearch API)
- ✅ Multi-agent handoff via LangGraph
- 🔲 Streamlit UI (in progress)
- 🔲 Deployment

## Roadmap

- Streamlit UI for resume upload and interactive reports
- Deployment to Streamlit Cloud
- ATS Score & Resume Optimization tool
- Skill Gap Roadmap generator
- Cover Letter Generator
- Export reports as PDF

## Author

Vedant Ravindra Savdekar