from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, add_messages
from dotenv import load_dotenv

from crypto_agent.agents.abe_agent.coding.graph import coding_agent
from crypto_agent.agents.abe_agent.advisor.graph import advisor_agent
from crypto_agent.agents.abe_agent.planning.graph import planning_agent
from crypto_agent.types import AgentCapability

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

builder = StateGraph(State)
builder.add_node("advisor_agent", advisor_agent)
builder.add_node("planning_agent", planning_agent)
builder.add_node("coding_agent", coding_agent)
builder.set_entry_point("advisor_agent")

agent = builder.compile(name="Attribute-Based Encryption Code Implementation Expert")


capabilities: set[AgentCapability] = {"coding"}
