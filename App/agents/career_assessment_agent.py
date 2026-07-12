import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage

from App.services.rag_service import RAGService

load_dotenv()

# Create the RAG service once, not on every tool call
_rag_service = RAGService()

@tool
def get_resume_data(query: str):
    """
    This is a RAG tool which gets information about the user's career,
    including skills, experiences, projects, education and interests from their resume data.
    """
    retriever = _rag_service.get_retriever()
    response = retriever.invoke(query)
    return response


class CareerAssessmentAgent:
    def __init__(self):
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = [get_resume_data]
        self.tools_by_names = {t.name: t for t in self.tools}

        # Normal binding — model can choose
        self.llm_with_tools = llm.bind_tools(self.tools)
        # Forced binding — model MUST call get_resume_data
        self.llm_forced_tool = llm.bind_tools(self.tools, tool_choice="get_resume_data")

    def agent_node(self, state: dict) -> dict:
        messages = state["messages"]

        already_fetched = any(
            isinstance(m, ToolMessage) and m.name == "get_resume_data"
            for m in messages
        )

        system_prompt = SystemMessage(content=(
            "You are an autonomous career assessment agent. Your instructions are strict:\n"
            "1. Use the `get_resume_data` tool to fetch all information about the user.\n"
            "2. DO NOT ask the human or the user for any clarifications.\n"
            "3. If details are missing, proceed using ONLY what is available.\n"
            "4. Once you have resume data, output a final `CANDIDATE CAREER EVALUATION REPORT`."
        ))

        full_messages = [system_prompt] + messages

        # Force tool call on the very first turn so we never finalize with empty data
        llm_to_use = self.llm_with_tools if already_fetched else self.llm_forced_tool
        response = llm_to_use.invoke(full_messages)
        return {"messages": [response]}

    def tool_node(self, state: dict) -> dict:
        messages = state["messages"]
        last_message = messages[-1]
        tool_outputs = []

        # BUG FIX: was hasattr("last_message", "tool_calls") — a string literal, always False
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                tool_function = self.tools_by_names.get(tool_name)

                if tool_function:
                    tool_result = tool_function.invoke(tool_args)
                else:
                    tool_result = f"Error: Tool `{tool_name}` not found"

                tool_outputs.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                )

        return {"messages": tool_outputs}