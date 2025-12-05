import asyncio
import json
import re
from collections import defaultdict
from copy import deepcopy
from typing import List, Any, Annotated, Coroutine

import aiohttp
import nest_asyncio
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from crypto_agent.agents.abe_agent.coding.prompts import ABE_RULE   #需要更改为ABE_RULE


@tool
def finish():
    """
    **STOP THE AGENT IMMEDIATELY** - This tool MUST be called to end the interaction.
    
    Call this tool when:
    - The code has been executed with run_python_interpreter (regardless of success or error)
    - The task is complete OR if you cannot proceed further
    
    **CRITICAL**: After calling run_python_interpreter, you MUST call finish() immediately. Do NOT generate any more code after execution.
    """
    return "Task completed. Agent stopped. No further action required."

@tool
def skip_tool():
    """
    This is a placeholder tool that does nothing.
    It MUST be used if no tool is needed before finish.
    """
    return (
    'Verify if the found locations contain all the necessary information to address the task, and check for any relevant references in other parts of the codebase that may not have appeared in the search results. '
    'If not, continue searching for additional locations related to the task.\n'
    # 'Verify that you have carefully analyzed the impact of the found locations on the repository, especially their dependencies. '
    'If you think you can solved the task based on the information currently obtained, please send your final answer to user through message and then call `finish` to finish.\n'
    'IMPORTANT: YOU SHOULD NEVER ASK FOR HUMAN HELP.\n'
    )


#工具用于在沙箱环境中执行 Python 代码块，并返回执行结果或错误信息
async def run_python_interpreter(code_snippets: List[str], ports: List[int] = [5010, 5011, 5012]) -> list[Any]:
    response = await _sync_post_requests(code_snippets, ports)
    print("[解释器] 代码执行结果:", response)
    if len(response)==0:
        return ["There is no code implementation in the recent context. Please call the interpreter after providing the code."]
    # if len(response)==1:
    #     return ["Please provide the implementation code for Attribute-Based Encryption"]
    # 明确提示 agent 必须调用 finish()
    return [response, ABE_RULE, "**IMPORTANT: Code execution completed. You MUST call finish() tool immediately. Do NOT generate any more code.**"]




async def _sync_post_requests(code_snippets: List[str], ports: List[int]) -> List[Any]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, code in enumerate(code_snippets):
            url = f'http://localhost:{ports[i]}/exec'
            # url = f'http://10.147.20.102:{ports[i]}/exec'
            tasks.append(session.post(url, data=code))

        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]

@tool("run_python_interpreter", parse_docstring=True)
def sync_run_python_interpreter(state: Annotated[dict, InjectedState], ports: List[int] = [5010, 5011, 5012]):
    """
    Executes complete Python file codes in a sandboxed environment and returns the results or error information.
    This tool can run complete Python programs and provide output, including successful execution results or detailed error traces.
    要使用这个工具，确保你当前输出的回答中**已经**包含多个用```python ```包裹的代码块，且不要包含不需要执行的多余代码块。对于多个代码块，此工具只需调用一次。


    **Output Format:**
    Each Python program execution returns a JSON response with the following structure:
    ```json
    {
        "output": "Standard output content from the program",
        "error": "Error message if execution failed, empty string if successful",
        "stack_trace": "Complete stack trace if error occurred, empty string if successful"
    }
    ```

    Args:
        ports (List[int]): List of ports for the interpreter servers, default is [5010, 5011, 5012].
    """
    def code_block_extraction(answer: str) -> List[str]:
        return re.findall(r"```python\n(.*?)\n```", answer, re.DOTALL)
    codes=code_block_extraction(state["messages"][-1].content)

    # 使用 nest_asyncio 允许在已有事件循环中运行异步代码
    nest_asyncio.apply()

    # 获取或创建事件循环
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(run_python_interpreter(codes, ports))

# code_snippets (list): "A list of complete Python file codes to execute. Each element in the list represents
# a complete Python program/file that will be executed independently.
# Each code snippet should be a full, self-contained Python program with all necessary
# imports, class definitions, function definitions, and execution logic.
# Multi-line code should be properly formatted with newline characters.