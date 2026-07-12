import os
import requests
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
JSEARCH_HOST = "jsearch.p.rapidapi.com"


@tool
def search_jobs(query: str, location: str = "India"):
    """
    Searches live job postings using the JSearch API (aggregates LinkedIn,
    Indeed, Glassdoor, Naukri, etc). Pass a role/skills query and optionally
    a location. Returns a list of matching job postings.
    """
    if not RAPIDAPI_KEY:
        return "Error: RAPIDAPI_KEY not set in .env"

    # Safety net: keep query short even if the LLM sends something long/stacked
    query = " ".join(query.split()[:4])

    url = "https://jsearch.p.rapidapi.com/search-v2"
    params = {
        "query": f"{query} in {location}",
        "num_pages": "1",
        "country": "in",       # India
        "date_posted": "all",
    }
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
    except requests.RequestException as e:
        return f"Error: request failed - {e}"

    if response.status_code == 403:
        return "Error: API key invalid or not subscribed to JSearch. Do not retry."
    if response.status_code == 429:
        return "Error: Rate limit reached. Do not retry."
    if response.status_code != 200:
        return f"Error: JSearch API returned status {response.status_code}. Do not retry."

    raw = response.json()
    jobs = raw.get("data", {}).get("jobs", [])
    jobs = jobs[:5] if isinstance(jobs, list) else []

    if not jobs:
        return "No job postings found for this query."

    return [
        f"**{job.get('job_title')}** at {job.get('employer_name')} "
        f"({job.get('job_city') or job.get('job_country')}) — "
        f"[Apply here]({job.get('job_apply_link')})"
        for job in jobs
    ]


class JobSearchAgent:
    def __init__(self):
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = [search_jobs]
        self.tools_by_names = {t.name: t for t in self.tools}

        self.llm_with_tools = llm.bind_tools(self.tools)
        self.llm_forced_tool = llm.bind_tools(self.tools, tool_choice="search_jobs")

    def agent_node(self, state: dict) -> dict:
        career_report = state.get("career_report", "")
        messages = state["messages"]

        already_searched = any(
            isinstance(m, ToolMessage) and m.name == "search_jobs"
            for m in messages
        )

        system_prompt = SystemMessage(content=(
            "You are a job search agent. Use the candidate's career evaluation report "
            "below ONLY as internal context to decide the search query — do NOT repeat, "
            "restate, or summarize the report itself in your response.\n"
            "Your final output should start DIRECTLY with the job listings — do not "
            "reprint the candidate's profile, strengths, or skills section.\n"
            "IMPORTANT: The `query` argument must be SHORT — just ONE job title, "
            "e.g. 'AI Engineer' or 'Machine Learning Engineer fresher'. "
            "Do NOT stack multiple roles or skills into the query.\n"
            "Do NOT include a location in the query text — use the `location` parameter instead.\n"
            "DO NOT ask for clarification. If search_jobs returns an error, report it "
            "clearly instead of retrying.\n\n"
            "CRITICAL FORMATTING RULE: Each job listing MUST include its apply link "
            "directly within that same row/bullet — e.g. "
            "'**Job Title** at Company (Location) — [Apply here](url)'. "
            "Do NOT list apply links separately in a different section.\n\n"
            f"CANDIDATE CAREER EVALUATION REPORT (context only, do not repeat this):\n{career_report}"
        ))

        full_messages = [system_prompt] + messages
        llm_to_use = self.llm_with_tools if already_searched else self.llm_forced_tool
        response = llm_to_use.invoke(full_messages)
        return {"messages": [response]}

    def tool_node(self, state: dict) -> dict:
        messages = state["messages"]
        last_message = messages[-1]
        tool_outputs = []

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                tool_function = self.tools_by_names.get(tool_name)
                tool_result = (
                    tool_function.invoke(tool_args) if tool_function
                    else f"Error: Tool `{tool_name}` not found"
                )

                tool_outputs.append(
                    ToolMessage(content=str(tool_result), tool_call_id=tool_id, name=tool_name)
                )

        return {"messages": tool_outputs}