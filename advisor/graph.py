import os
from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM
from langgraph.prebuilt import create_react_agent

from crypto_agent.agents.abe_agent.advisor.prompts import prompt_advisor
from crypto_agent.agents.abe_agent.advisor.tools import transfer_to_planning_agent

# Load environment variables (e.g., API keys)
load_dotenv()

# Create the advisor agent using a React agent pattern
advisor_agent = create_react_agent(
    model=ChatLiteLLM(
        model="openai/qwen3-coder-plus",
        api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
        api_key=os.getenv("QWEN_API_KEY"),
        streaming=True,
    ),
    tools=[transfer_to_planning_agent],
    prompt=prompt_advisor,
)
