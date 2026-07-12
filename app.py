import os
import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage

from App.services.rag_service import RAGService

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


# ---------- UI ----------

st.title("🎯 UniAgent")
st.caption("Multi-agent AI career assistant — resume evaluation + live job search")

with st.sidebar:
    st.header("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        if st.session_state.processed_file_name != uploaded_file.name:
            os.makedirs("./Assets", exist_ok=True)
            save_path = f"./Assets/{uploaded_file.name}"
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.status("Processing your resume...", expanded=True) as status:
                try:
                    status.update(label="📄 Reading PDF...")
                    rag_service = get_rag_service()

                    status.update(label="✂️ Splitting into chunks...")
                    status.update(label="🧬 Generating embeddings...")

                    rag_service.process_and_create_embeddings(file_path=save_path)

                    status.update(label="✅ Resume ready!", state="complete")
                    st.session_state.resume_ready = True
                    st.session_state.processed_file_name = uploaded_file.name

                except Exception as e:
                    status.update(label="❌ Failed to process resume", state="error")
                    st.error(f"Error processing resume: {e}")
        else:
            st.success("✅ Resume already processed.")


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


# ---------- Results ----------

if st.session_state.career_report:
    st.subheader("📋 Career Evaluation Report")
    st.markdown(st.session_state.career_report)

if st.session_state.job_results:
    st.subheader("💼 Job Search Results")
    st.markdown(st.session_state.job_results)

