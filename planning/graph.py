import os
from dotenv import load_dotenv
from crypto_agent.agents.abe_agent.planning.prompts import prompt_common
from crypto_agent.agents.abe_agent.planning.tools import recall, transfer_to_coding_agent

from langgraph.prebuilt import create_react_agent
from langchain_litellm import ChatLiteLLM

load_dotenv()
planning_agent = create_react_agent(
        model=ChatLiteLLM(
            model="openai/qwen3-coder-plus",
            api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
            api_key=os.getenv("QWEN_API_KEY"),
            # api_base='https://open.bigmodel.cn/api/paas/v4',
            # api_key=os.getenv("GLM_API_KEY"),
            # model="openai/glm-4.5",
            streaming=True
        ),
        tools=[recall, transfer_to_coding_agent],
        prompt=prompt_common
    )