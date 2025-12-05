from langchain.tools import tool
from langchain_core.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing import Literal, Annotated


@tool
def transfer_to_planning_agent(state: Annotated[dict, InjectedState]) -> Command[Literal["planning_agent"]]:
    """Transfer control to the planning agent after advisor has given suggestions.
    The advisor should collect user's confirmation and any additional details, then invoke this tool.
    """

    raw_messages = state.get("messages", []) if state else []

    # 过滤掉包含 tool_calls 的消息，避免传递给 planning_agent 不认得的工具调用
    filtered_messages = []
    for msg in raw_messages:
        # langchain_core.messages.AIMessage 等：有 .tool_calls 属性
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            continue
        # 字典形式的消息：可能有 "tool_calls" 字段
        if isinstance(msg, dict) and msg.get("tool_calls"):
            continue
        filtered_messages.append(msg)

    return Command(
        goto="planning_agent",
        update={"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *filtered_messages]},
        graph=Command.PARENT,
    )
