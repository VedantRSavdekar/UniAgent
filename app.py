import os
import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage

from App.services.rag_service import RAGService
from App.services.validation import validate_uploaded_file, validate_pdf_has_text, ValidationError

st.set_page_config(page_title="UniAgent — AI Career Assistant", page_icon="🎯", layout="centered")


# ---------- Cached resources (avoid re-init on every rerun) ----------

@st.cache_resource
def get_workflow():
    from App.workflow.workflow import workflow
    return workflow


@st.cache_resource
def get_rag_service():
    return RAGService()


# ---------- Session state defaults ----------

if "resume_ready" not in st.session_state:
    st.session_state.resume_ready = os.path.exists("./resume_vector_db")
if "processed_file_name" not in st.session_state:
    st.session_state.processed_file_name = None
if "career_report" not in st.session_state:
    st.session_state.career_report = None
if "job_results" not in st.session_state:
    st.session_state.job_results = None
if "raw_job_listings" not in st.session_state:
    st.session_state.raw_job_listings = None
if "ats_result" not in st.session_state:
    st.session_state.ats_result = None


# ---------- UI ----------

st.title("🎯 UniAgent")
st.caption("Multi-agent AI career assistant — resume evaluation + live job search")

with st.sidebar:
    st.header("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        try:
            validate_uploaded_file(uploaded_file)
        except ValidationError as ve:
            st.error(str(ve))
            st.stop()

        if st.session_state.processed_file_name != uploaded_file.name:
            os.makedirs("./Assets", exist_ok=True)
            save_path = f"./Assets/{uploaded_file.name}"
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.status("Processing your resume...", expanded=True) as status:
                try:
                    status.update(label="📄 Validating PDF content...")
                    validate_pdf_has_text(save_path)

                    status.update(label="✂️ Splitting into chunks...")
                    status.update(label="🧬 Generating embeddings...")

                    rag_service = get_rag_service()
                    rag_service.process_and_create_embeddings(file_path=save_path)

                    status.update(label="✅ Resume ready!", state="complete")
                    st.session_state.resume_ready = True
                    st.session_state.processed_file_name = uploaded_file.name

                except ValidationError as ve:
                    status.update(label="❌ Invalid PDF", state="error")
                    st.error(str(ve))

                except Exception as e:
                    status.update(label="❌ Failed to process resume", state="error")
                    st.error(f"Error processing resume: {e}")


# ---------- Section 2: Career Assessment + Job Search ----------

st.header("2. Run Assessment & Job Search")

if not st.session_state.resume_ready:
    st.info("Upload and process a resume first (see sidebar).")

run_disabled = not st.session_state.resume_ready

if st.button("🚀 Run Career Assessment + Job Search", disabled=run_disabled, type="primary"):
    workflow = get_workflow()

    input_state = {
        "messages": [HumanMessage(content="Assess my profile and find matching jobs")],
        "career_report": "",
    }

    st.session_state.career_report = None
    st.session_state.job_results = None
    st.session_state.raw_job_listings = None

    accumulated_state = dict(input_state)
    raw_job_listings = None

    with st.status("Running UniAgent pipeline...", expanded=True) as status:
        try:
            for step_output in workflow.stream(input_state):
                node_name = list(step_output.keys())[0]
                node_result = step_output[node_name]

                if node_name == "career_assessment":
                    status.update(label="🧠 Analyzing your resume...")
                elif node_name == "assessment_tools":
                    status.update(label="📄 Retrieving resume data...")
                elif node_name == "handoff_to_job_search":
                    status.update(label="🔄 Handing off to job search agent...")
                elif node_name == "job_search":
                    status.update(label="🔍 Searching live job postings...")
                elif node_name == "job_search_tools":
                    status.update(label="🌐 Querying job listings API...")

                if "career_report" in node_result:
                    accumulated_state["career_report"] = node_result["career_report"]

                if "messages" in node_result:
                    accumulated_state.setdefault("messages", [])
                    accumulated_state["messages"].extend(node_result["messages"])

                    for m in node_result["messages"]:
                        if isinstance(m, ToolMessage) and m.name == "search_jobs":
                            raw_job_listings = m.content

            status.update(label="✅ Done!", state="complete")

            st.session_state.career_report = accumulated_state.get("career_report")
            messages = accumulated_state.get("messages", [])
            if messages:
                st.session_state.job_results = messages[-1].content
            st.session_state.raw_job_listings = raw_job_listings

        except Exception as e:
            status.update(label="❌ Something went wrong", state="error")
            st.error(f"Pipeline error: {e}")


# ---------- Section 2 Results (shown right after its own button) ----------

if st.session_state.career_report:
    st.subheader("📋 Career Evaluation Report")
    st.markdown(st.session_state.career_report)

if st.session_state.job_results:
    st.subheader("💼 Job Search Results")
    st.markdown(st.session_state.job_results)


# ---------- Section 3: ATS Score Check ----------

st.divider()
st.header("3. ATS Score Check (Optional)")

ats_disabled = not st.session_state.career_report

if ats_disabled:
    st.info("Run Career Assessment first (Section 2) before checking ATS score.")

if st.button("📊 Check ATS Score", disabled=ats_disabled):
    from App.services.ats_service import get_ats_score

    with st.spinner("Analyzing ATS compatibility..."):
        try:
            ats_result = get_ats_score(st.session_state.career_report)
            st.session_state.ats_result = ats_result
        except Exception as e:
            st.session_state.ats_result = None
            st.error(f"ATS check failed: {e}")


# ---------- Section 3 Results (persists across reruns) ----------

if st.session_state.ats_result:
    ats_result = st.session_state.ats_result

    st.subheader(f"Overall Score: {ats_result.overall_score}/100")
    st.progress(ats_result.overall_score / 100)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Format Score", f"{ats_result.format_score}/100")
    with col2:
        if ats_result.keyword_match_score is not None:
            st.metric("Keyword Match", f"{ats_result.keyword_match_score}/100")
        else:
            st.metric("Keyword Match", "N/A (no JD)")

    if ats_result.format_issues:
        st.subheader("⚠️ Format Issues")
        for issue in ats_result.format_issues:
            st.write(f"- {issue}")

    if ats_result.matched_keywords:
        st.subheader("✅ Matched Keywords")
        st.write(", ".join(ats_result.matched_keywords))

    if ats_result.missing_keywords:
        st.subheader("❌ Missing Keywords")
        st.write(", ".join(ats_result.missing_keywords))

    st.subheader("💡 Recommendations")
    for rec in ats_result.recommendations:
        st.write(f"- {rec}")