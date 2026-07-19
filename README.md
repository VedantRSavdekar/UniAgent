# UniAgent — AI Career Assistant

UniAgent is a multi-agent AI system that evaluates a candidate's resume, checks it 
for ATS (Applicant Tracking System) compatibility, and automatically searches for 
matching live job postings — built as part of the Agentic AI Saksham Internship 
project.

**Live App:** [Add your Streamlit Cloud URL here]

## Architecture

Two specialized agents connected via a LangGraph workflow, plus a standalone ATS 
scoring service:

1. **Career Assessment Agent** — retrieves resume data using a RAG pipeline 
   (Chroma + Gemini embeddings) and produces a structured career evaluation report.
2. **Job Search Agent** — takes the evaluation report, extracts a target role, 
   and searches live job postings via the JSearch API (LinkedIn, Indeed, 
   Glassdoor, Naukri aggregated).
3. **ATS Score Service** — analyzes the career evaluation report for ATS 
   parsing compatibility (format/structure) and, optionally, keyword match 
   against a specific job description.

Resume PDF → RAG (Chroma + Gemini embeddings)
→ Career Assessment Agent → Career Report
→ Job Search Agent → Live Job Matches
→ ATS Score Service → Compatibility Report

## Tech Stack

- **UI:** Streamlit
- **Orchestration:** LangGraph
- **LLM:** Groq (openai/gpt-oss-120b)
- **Embeddings:** Google Generative AI (gemini-embedding-001)
- **Vector DB:** Chroma
- **Job Search API:** JSearch (via RapidAPI)
- **Structured Outputs:** Pydantic
- **Language:** Python

## Project Structure
   UniAgent/
    ├── App/
    │   ├── agents/
    │   │   ├── career_assessment_agent.py
    │   │   └── job_search_agent.py
    │   ├── services/
    │   │   ├── rag_service.py
    │   │   ├── ats_service.py
    │   │   └── validation.py
    │   └── workflow/
    │       └── workflow.py
    ├── Assets/
    │   └── (uploaded resumes — not committed)
    ├── resume_vector_db/ (generated locally — not committed)
    ├── app.py
    ├── .gitignore
    ├── requirements.txt
    └── README.md

## How It Works

1. **Upload & Validate** — user uploads a resume PDF via the Streamlit sidebar. 
   The file is checked for type, size, and readable text content before processing.
2. **Embed** — the resume is chunked and embedded into a local Chroma vector 
   database. Re-uploading a resume clears old embeddings for that file first, 
   so results always reflect the most current version.
3. **Career Assessment** — the Career Assessment Agent queries the vector store 
   via a `get_resume_data` tool to ground its output in the candidate's actual 
   resume, then produces a `CANDIDATE CAREER EVALUATION REPORT` covering profile 
   summary, strengths, and career fit.
4. **Job Search Handoff** — the report is passed to the Job Search Agent, which 
   extracts a concise target role and calls a `search_jobs` tool to query the 
   JSearch API for live postings matching that role in India. Apply links are 
   embedded directly inline with each listing.
5. **ATS Score (optional)** — once a career report exists, the user can run an 
   ATS compatibility check. This analyzes the report for format/structure issues 
   (tables, missing standard headers, inconsistent dates) and provides an overall 
   score with actionable recommendations.

## Setup

1. Clone the repo and create a virtual environment:
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

2. Create a `.env` file in the project root:
    GROQ_API_KEY=your_groq_key
    GEMINI_API_KEY=your_gemini_key
    RAPIDAPI_KEY=your_rapidapi_key

3. Run the Streamlit app:
    streamlit run app.py

4. Upload a resume PDF via the sidebar — processing happens automatically.

5. Click "Run Career Assessment + Job Search" to generate the career report 
   and live job matches.

6. Optionally, click "Check ATS Score" to evaluate the report's ATS compatibility.

## Example Output

Running the workflow produces:
- A structured career evaluation report (education, skills, strengths, career fit)
- A list of live, matching job postings with company, location, and apply links
- Personalized recommendations (resume improvements, target job titles, next steps)


## Current Status

- ✅ RAG-based resume parsing (Chroma + Gemini embeddings)
- ✅ Career evaluation report generation
- ✅ Live job search integration (JSearch API) with inline apply links
- ✅ Multi-agent handoff via LangGraph
- ✅ Streamlit UI with live pipeline status updates
- ✅ Input validation (file type, size, unreadable/scanned PDFs)
- ✅ Deployed to Streamlit Cloud
- ✅ ATS Score compatibility check
- 🔲 Keyword match scoring against a specific job description
- 🔲 Cover Letter Generator
- 🔲 Skill Gap Roadmap
- 🔲 Export reports as PDF

## Roadmap

- Skill Gap Roadmap generator (building on job match data)
- Cover Letter Generator
- Export reports as PDF
- Multi-language resume support (Hindi/Marathi)

## Author

Vedant Ravindra Savdekar