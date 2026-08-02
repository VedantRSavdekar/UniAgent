import os
import json
import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage

from App.services.rag_service import RAGService
from App.services.validation import validate_uploaded_file, validate_pdf_has_text, ValidationError

st.set_page_config(page_title="UniAgent — AI Career Assistant", page_icon="🎯", layout="wide")


# ---------- Cached resources ----------

@st.cache_resource
def get_workflow():
    from App.workflow.workflow import workflow
    return workflow


@st.cache_resource
def get_rag_service():
    return RAGService()


# ---------- Local session save/restore ----------

SAVE_DIR = "./local_sessions"
SAVE_FILE = os.path.join(SAVE_DIR, "last_session.json")


def save_session_data():
    os.makedirs(SAVE_DIR, exist_ok=True)
    data = {
        "career_report": st.session_state.career_report,
        "job_results": st.session_state.job_results,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_session_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# ---------- Session state defaults ----------

defaults = {
    "resume_ready": os.path.exists("./resume_vector_db"),
    "processed_file_name": None,
    "career_report": None,
    "job_results": None,
    "raw_job_listings": None,
    "ats_result": None,
    "cover_letter": None,
    "pdf_bytes": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Sidebar Navigation ----------

with st.sidebar:
    st.title("🎯 UniAgent")
    st.caption("AI Career Assistant")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📄 Upload Resume",
            "🧠 Career Assessment & Job Search",
            "📊 ATS Score & Cover Letter",
            "📥 Export Report",
            "🗂️ History",
        ],
        label_visibility="collapsed",
    )


# ==================================================================
# PAGE 1: Upload Resume
# ==================================================================

if page == "📄 Upload Resume":
    st.header("📄 Upload Resume")
    st.write("Upload your resume PDF to get started. Processing happens automatically.")

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
        else:
            st.success("✅ Resume already processed.")

    if st.session_state.resume_ready:
        st.info("✅ A resume is ready. Head to 'Career Assessment & Job Search' next.")


# ==================================================================
# PAGE 2: Career Assessment & Job Search
# ==================================================================

elif page == "🧠 Career Assessment & Job Search":
    st.header("🧠 Career Assessment & Job Search")

    if st.session_state.career_report is None:
        saved = load_session_data()
        if saved and saved.get("career_report"):
            st.info("A previously saved report is available.")
            if st.button("♻️ Restore last saved report (no API calls)"):
                st.session_state.career_report = saved.get("career_report")
                st.session_state.job_results = saved.get("job_results")
                st.rerun()

    if not st.session_state.resume_ready:
        st.warning("Upload and process a resume first (see 'Upload Resume' page).")

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

                save_session_data()

            except Exception as e:
                status.update(label="❌ Something went wrong", state="error")
                st.error(f"Pipeline error: {e}")

    if st.session_state.career_report:
        st.subheader("📋 Career Evaluation Report")
        st.markdown(st.session_state.career_report)

    if st.session_state.job_results:
        st.subheader("💼 Job Search Results")
        st.markdown(st.session_state.job_results)


# ==================================================================
# PAGE 3: ATS Score & Cover Letter
# ==================================================================

elif page == "📊 ATS Score & Cover Letter":
    st.header("📊 ATS Score & Cover Letter")

    if not st.session_state.career_report:
        st.warning("Run Career Assessment first (see 'Career Assessment & Job Search' page).")

    col1, col2 = st.columns(2)

    # --- ATS Score ---
    with col1:
        st.subheader("ATS Score Check")
        ats_disabled = not st.session_state.career_report

        job_description_input = st.text_input("Paste a job description (optional — used for ATS keyword match and cover letter tailoring)")

        if st.button("📊 Check ATS Score", disabled=ats_disabled):
            from App.services.ats_service import get_ats_score

            with st.spinner("Analyzing ATS compatibility..."):
                try:
                    ats_result = get_ats_score(st.session_state.career_report, job_description_input)
                    st.session_state.ats_result = ats_result
                except Exception as e:
                    st.session_state.ats_result = None
                    st.error(f"ATS check failed: {e}")

        if st.session_state.ats_result:
            ats_result = st.session_state.ats_result
            st.metric("Overall Score", f"{ats_result.overall_score}/100")
            st.progress(ats_result.overall_score / 100)
            st.metric("Format Score", f"{ats_result.format_score}/100")
            if ats_result.keyword_match_score is not None:
                st.metric("Keyword Match", f"{ats_result.keyword_match_score}/100")

            if ats_result.format_issues:
                st.markdown("**⚠️ Format Issues**")
                for issue in ats_result.format_issues:
                    st.write(f"- {issue}")

            if ats_result.matched_keywords:
                st.markdown("**✅ Matched Keywords**")
                st.write(", ".join(ats_result.matched_keywords))

            if ats_result.missing_keywords:
                st.markdown("**❌ Missing Keywords**")
                st.write(", ".join(ats_result.missing_keywords))

            st.markdown("**💡 Recommendations**")
            for rec in ats_result.recommendations:
                st.write(f"- {rec}")

    # --- Cover Letter ---
    with col2:
        st.subheader("Cover Letter Generator")
        company_name_input = st.text_input("Company name (optional)")

        cover_letter_disabled = not st.session_state.career_report

        if st.button("✉️ Generate Cover Letter", disabled=cover_letter_disabled):
            from App.services.cover_letter_service import generate_cover_letter

            with st.spinner("Writing your cover letter..."):
                try:
                    cover_letter = generate_cover_letter(
                        career_report=st.session_state.career_report,
                        job_description=job_description_input,
                        company_name=company_name_input,
                    )
                    st.session_state.cover_letter = cover_letter
                except Exception as e:
                    st.session_state.cover_letter = None
                    st.error(f"Cover letter generation failed: {e}")

        if st.session_state.cover_letter:
            st.text_area("Your Cover Letter", value=st.session_state.cover_letter, height=400)


# ==================================================================
# PAGE 4: Export Report
# ==================================================================

elif page == "📥 Export Report":
    st.header("📥 Export Report")

    can_export = bool(st.session_state.career_report or st.session_state.job_results)

    if not can_export:
        st.warning("Run Career Assessment first to generate a downloadable report.")

    if can_export:
        from App.services.pdf_export_service import generate_report_pdf

        st.write("This will combine everything generated so far into a single PDF:")
        st.write("- Career Evaluation Report")
        st.write("- Job Search Results")
        if st.session_state.ats_result:
            st.write("- ATS Score Check")
        if st.session_state.cover_letter:
            st.write("- Cover Letter")

        if st.button("📥 Generate PDF Report", type="primary"):
            with st.spinner("Building your PDF..."):
                pdf_bytes = generate_report_pdf(
                    career_report=st.session_state.career_report,
                    job_results=st.session_state.job_results,
                    ats_result=st.session_state.ats_result,
                    cover_letter=st.session_state.cover_letter,
                )
                st.session_state.pdf_bytes = pdf_bytes

        if st.session_state.get("pdf_bytes"):
            st.download_button(
                label="⬇️ Download PDF",
                data=st.session_state.pdf_bytes,
                file_name="UniAgent_Career_Report.pdf",
                mime="application/pdf",
            )


# ==================================================================
# PAGE 5: History (Placeholder)
# ==================================================================

elif page == "🗂️ History":
    st.header("🗂️ History")
    st.info(
        "🚧 Coming soon — this page will let you browse and revisit every past "
        "resume assessment, job search, and generated report, backed by persistent storage."
    )