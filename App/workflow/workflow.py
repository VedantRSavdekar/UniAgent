from typing import TypedDict, Annotated, Literal

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages

from App.agents.career_assessment_agent import CareerAssessmentAgent
from App.agents.job_search_agent import JobSearchAgent


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    career_report: str


def route_assessment(state: AgentState) -> Literal["assessment_tools", "handoff_to_job_search"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "assessment_tools"
    state["career_report"] = last_message.content
    return "handoff_to_job_search"


def route_job_search(state: AgentState) -> Literal["job_search_tools", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "job_search_tools"
    return "__end__"


def handoff_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    return {
        "messages": [],
        "career_report": last_message.content,
    }


assessment_agent = CareerAssessmentAgent()
job_search_agent = JobSearchAgent()

workflow_builder = StateGraph(AgentState)

workflow_builder.add_node("career_assessment", assessment_agent.agent_node)
workflow_builder.add_node("assessment_tools", assessment_agent.tool_node)
workflow_builder.add_node("handoff_to_job_search", handoff_node)
workflow_builder.add_node("job_search", job_search_agent.agent_node)
workflow_builder.add_node("job_search_tools", job_search_agent.tool_node)

workflow_builder.add_edge(START, "career_assessment")
workflow_builder.add_conditional_edges(
    "career_assessment",
    route_assessment,
    {
        "assessment_tools": "assessment_tools",
        "handoff_to_job_search": "handoff_to_job_search",
    }
)
workflow_builder.add_edge("assessment_tools", "career_assessment")
workflow_builder.add_edge("handoff_to_job_search", "job_search")

workflow_builder.add_conditional_edges(
    "job_search",
    route_job_search,
    {
        "job_search_tools": "job_search_tools",
        "__end__": END,
    }
)
workflow_builder.add_edge("job_search_tools", "job_search")

workflow = workflow_builder.compile()


if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    input_state = {
        "messages": [HumanMessage(content="Assess my profile and find matching jobs")],
        "career_report": "",
    }

    print("\n----- OUTPUT -----\n")
    output = workflow.invoke(input_state)

    print("----- CAREER REPORT -----")
    print(output.get("career_report"))

    print("\n----- ALL MESSAGES -----")
    for m in output["messages"]:
        print(type(m).__name__, "-->", repr(m.content)[:300])

    print("\n----- LAST MESSAGE -----")
    print(repr(output["messages"][-1].content))