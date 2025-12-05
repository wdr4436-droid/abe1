import os
from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent, ToolNode

from crypto_agent.agents.abe_agent.coding.tools import skip_tool, finish, \
    sync_run_python_interpreter
from crypto_agent.toolkits.code_search import explore_tree_structure, search_code_snippets, get_entity_contents

# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"

#设置代理
load_dotenv()
checkpointer = InMemorySaver()   #创建了一个内存检查点实例，用于保存代理的状态。
coding_agent = create_react_agent(   #这是一个智能体（Agent），它会与计算机交互并执行任务。
        model=ChatLiteLLM(     #这个语言模型被配置为与 OpenAI API 进行交互，用于聊天和代码生成。
            # model = "anthropic/claude-sonnet-4-20250514",
            # anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
            model="openai/qwen3-coder-plus",
            api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
            api_key=os.getenv("QWEN_API_KEY"),
            temperature=0.2,
            top_p=0.8,
            top_k=20,
            max_tokens=4096,
             # 设置超时和重试参数，防止卡住
            timeout=120.0,  # 120秒超时
            max_retries=3,  # 最多重试3次
            # api_base='https://api.moonshot.cn/v1',
            # api_key=os.getenv("MOONSHOT_API_KEY"),
            # model="openai/kimi-k2-turbo-preview",
            # temperature=0.6,
            # max_tokens=16384,
            # api_base='https://open.bigmodel.cn/api/paas/v4',
            # api_key=os.getenv("GLM_API_KEY"),
            # model="openai/glm-4.5",
            streaming=True,
        ),
        tools=ToolNode([explore_tree_structure,search_code_snippets,get_entity_contents, skip_tool, finish, sync_run_python_interpreter]), 
        checkpointer=checkpointer,
        prompt="""You are a helpful assistant that can interact with a computer to solve tasks.
<IMPORTANT>
* If user provides a path, you should NOT assume it's relative to the current working directory. Instead, you should explore the file system to find the file before working on it.
* Always follow the ABE_RULE from prompts.py when reasoning about encryption or decryption.
* You have access to a sandbox Python interpreter via the `run_python_interpreter` tool. Use it to test your code after generating it.
* After testing your code successfully, you MUST call the `finish()` tool to complete the task.
</IMPORTANT>
"""
    )