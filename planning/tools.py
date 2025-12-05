import os
import json
import re
from typing import Annotated, Literal

from langchain.tools import tool
from langchain_core.messages import RemoveMessage
from langchain_core.runnables import RunnableConfig
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from crypto_agent.agents.abe_agent.coding.utils.utils import get_task_instruction
from crypto_agent.agents.abe_agent.planning.prompts import prompt_recall, prompt_parse
from crypto_agent.models.embedding import qwen3_embedding_0___6b
from crypto_agent.models.rerank import qwen3_reranker_0___6b
from crypto_agent.toolkits.code_search.plugins.location_tools.repo_ops.repo_ops import set_current_issue

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com/'

MILVUS_URI = "./src/crypto_agent/agents/abe_agent/planning/RAG/milvus_0.6b.db"
COLLECTION_NAME = "markdown_collection"
vector_db = Milvus(
    embedding_function=qwen3_embedding_0___6b.model,
    collection_name=COLLECTION_NAME,
    connection_args={"uri": MILVUS_URI},
)


# ----------------- 查询函数 -----------------
@tool
def recall(keywords: str):
    """
    Search for relevant documents in the vector database and return the top k results.
    Args:
        keywords: The keywords to search for.
    Returns:
        A list of documents that are relevant to the query.
    """
    try:
        # 第一步：向量检索（减少检索数量，因为重排序很慢）
        retrieved_docs = vector_db.similarity_search(keywords, k=10)  # 从 20 减少到 10
        if not retrieved_docs:
            return []

        # 过滤空文档
        valid_docs = [doc for doc in retrieved_docs if doc.page_content.strip()]
        if not valid_docs:
            return []

        # 第二步：批量重排序（优化性能）
        # 限制文档长度，避免处理过长的文档
        max_doc_length = 2000  # 限制每个文档的最大长度
        truncated_docs = []
        for doc in valid_docs:
            content = doc.page_content
            if len(content) > max_doc_length:
                # 截取文档的前面部分（通常重要信息在前面）
                content = content[:max_doc_length] + "..."
            truncated_docs.append((doc, content))

        # 批量 tokenize 和推理（优化性能的关键）
        # 将查询和文档组成对
        pairs = [(keywords, content) for _, content in truncated_docs]
        
        # 批量 tokenize（一次性处理所有文档对）
        inputs = qwen3_reranker_0___6b.tokenizer(
            pairs,
            truncation='only_second',
            max_length=1024,  # 减少 max_length 以加快处理速度（从 4096 降到 1024）
            padding=True,
            return_tensors="pt"
        ).to(qwen3_reranker_0___6b.model.device)

        # 批量推理（一次性处理所有文档，而不是循环）
        scored_docs = []
        with torch.no_grad():
            outputs = qwen3_reranker_0___6b.model(**inputs)
            # 获取每个文档的分数（批量处理，维度应该是 [batch_size, seq_len, vocab_size]）
            # 对于 reranker，通常取最后一个 token 的 logits
            if len(outputs.logits.shape) == 3:
                # [batch_size, seq_len, vocab_size] -> 取最后一个 token 的第一个 logit
                scores = outputs.logits[:, -1, 0].cpu().numpy()
            elif len(outputs.logits.shape) == 2:
                # [batch_size, vocab_size] -> 取第一个 logit
                scores = outputs.logits[:, 0].cpu().numpy()
            else:
                # 降级到单个处理（不应该发生）
                scores = outputs.logits.cpu().numpy().flatten()[:len(truncated_docs)]
            
            for i, (doc, _) in enumerate(truncated_docs):
                if i < len(scores):
                    scored_docs.append((float(scores[i]), doc))

        # 按分数排序并返回前k个结果
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # 只返回前 8 个结果（减少输出量）
        top_docs = [doc for (score, doc) in scored_docs[:8]]

        return str(top_docs) + prompt_recall

    except Exception as e:
        print(f"检索过程中出错: {str(e)}")
        # 如果重排序失败，尽量仍然给出一些文档，再附上严格的后续指令
        if 'retrieved_docs' in locals() and retrieved_docs:
            return str(retrieved_docs[:8]) + prompt_recall
        # 即使完全没有检索结果，也必须返回 prompt_recall，
        # 这样 planning agent 仍会按照提示：先输出规划结果，然后**必须**调用 transfer_to_coding_agent
        return "[WARNING] 向量检索失败或未找到相关文档，但你仍需根据已有的用户需求给出规划结果。" + prompt_recall


# # ----------------- 示例查询 -----------------
# if __name__ == "__main__":
#     query = "用户需求\n实现两方半诚实CS模型下的神经网络推理"
#     results = recall(query)
#
#     print(f"查询: '{query}'")
#     for i, doc in enumerate(results):
#         print(f"\n结果 {i + 1}:")
#         print(f"来源文件: {doc.metadata.get('source', '未知')}")
#         print(f"内容: {doc.page_content[:200]}...")  # 只打印前200字符避免输出过长


@tool
def transfer_to_coding_agent(state: Annotated[dict, InjectedState], config: RunnableConfig) -> Command[
    Literal["coding_agent"]]:
    """Transfer to coding_agent."""
    INDEX_PATH = os.environ.get("INDEX_PATH")
    repo_name = config.get("configurable", {}).get("repo_name", "charm-dev")
    os.environ['GRAPH_INDEX_DIR'] = f'{INDEX_PATH}/index/graph_index_v2.3'
    os.environ['BM25_INDEX_DIR'] = f'{INDEX_PATH}/index/BM25_index'

    # Try to include a structured policy JSON if present in the latest message
    latest_content = state["messages"][-1].content if state and state.get("messages") else ""
    # Also check previous messages to detect user's choice of "1" or "2"
    all_messages = state.get("messages", []) if state else []
    all_content = " ".join([msg.content for msg in all_messages[-5:]]) if all_messages else ""
    policy_json = None
    revocation_requested = False
    
    # Extract user requirement from message history
    # Look for "## 用户需求" section in planning output, or use the first user message
    problem_statement = latest_content
    user_requirement = ""
    detected_model = None  # Track detected model type
    
    # Try to extract user requirement from planning output
    if "## 用户需求" in latest_content:
        # Extract the user requirement section
        lines = latest_content.split('\n')
        in_user_requirement = False
        requirement_lines = []
        for line in lines:
            if "## 用户需求" in line:
                in_user_requirement = True
                continue
            elif in_user_requirement and line.startswith("##"):
                break
            elif in_user_requirement:
                requirement_lines.append(line)
                # Check for explicit model declaration in user requirement
                if "加密模型：KP-ABE" in line or "加密模型: KP-ABE" in line:
                    detected_model = "KP-ABE"
                elif "加密模型：CP-ABE" in line or "加密模型: CP-ABE" in line:
                    detected_model = "CP-ABE"
                elif "加密模型：Multi-Authority" in line or "加密模型: Multi-Authority" in line or "加密模型：多权威" in line:
                    detected_model = "Multi-Authority"
                elif "可撤销" in line or "Revocable" in line:
                    detected_model = "Revocable CP-ABE"
        if requirement_lines:
            user_requirement = '\n'.join(requirement_lines).strip()
    
    # If no user requirement found in latest message, look for the first user message
    if not user_requirement:
        for msg in all_messages:
            if hasattr(msg, 'type') and msg.type == 'human':
                user_requirement = msg.content
                break
            elif isinstance(msg, dict) and msg.get('role') == 'user':
                user_requirement = msg.get('content', '')
                break
    
    # Combine user requirement with planning output if available
    if user_requirement and latest_content:
        # If latest_content is just "(KP-ABE)" or similar short text, use user_requirement
        if len(latest_content.strip()) < 50 and ("(KP-ABE)" in latest_content or "(CP-ABE)" in latest_content):
            problem_statement = user_requirement + "\n\n" + latest_content
        elif "## 用户需求" in latest_content:
            problem_statement = latest_content
        else:
            problem_statement = user_requirement + "\n\n规划结果:\n" + latest_content
    elif user_requirement:
        problem_statement = user_requirement
    
    revocation_keywords = ["撤销", "吊销", "可撤销", "失效", "过期", "revocation", "revocable", "revoke", "epoch"]
    revocation_requested = latest_content.strip() == "4" or any(
        kw in latest_content or kw in user_requirement or kw in all_content for kw in revocation_keywords
    )
    revocation_default = {
        "enabled": True,
        "method": "epoch",
        "epoch": 1,
        "requires_ciphertext_update": False,
        "update_functions": ["update_epoch", "update_user_key"],
        "notes": "Embed an epoch attribute into policy and keys; rotate epoch to revoke old keys.",
    }
    
    # Check if user wants to generate ABE directly
    # Priority: detected_model from user requirement > explicit user input > content analysis
    
    # First, check if we detected model from user requirement section
    if detected_model == "KP-ABE":
        policy_json = json.dumps({
            "model": "KP-ABE",
            "logic": "属性A AND (属性B OR 属性C)",
            "attributes": ["属性A", "属性B", "属性C"],
            "functional_requirements": "实现KP-ABE数据加密和解密功能",
            "input_format": "JSON格式，包含密文属性集合和明文数据",
            "output_format": "JSON格式，包含密文数据和密文属性集合"
        }, ensure_ascii=False)
    elif detected_model == "Revocable CP-ABE":
        policy_json = json.dumps({
            "model": "Revocable CP-ABE",
            "logic": "属性A AND (属性B OR 属性C) AND epoch=1",
            "attributes": ["属性A", "属性B", "属性C", "epoch"],
            "functional_requirements": "实现可撤销（时间片）CP-ABE，提供密钥更新与撤销示例",
            "input_format": "JSON格式，包含属性和明文数据",
            "output_format": "JSON格式，包含密文数据和访问策略",
            "revocation": revocation_default,
        }, ensure_ascii=False)
    elif detected_model == "CP-ABE":
        policy_json = json.dumps({
            "model": "CP-ABE",
            "logic": "属性A AND (属性B OR 属性C)",
            "attributes": ["属性A", "属性B", "属性C"],
            "functional_requirements": "实现数据加密和解密功能",
            "input_format": "JSON格式，包含属性和明文数据",
            "output_format": "JSON格式，包含密文数据和访问策略"
        }, ensure_ascii=False)
    # Check for explicit user input (more reliable than content analysis)
    elif (latest_content.strip() == "2" or 
          "生成KP-ABE" in user_requirement or 
          latest_content.strip() == "1" or
          "生成CP-ABE" in user_requirement or
          latest_content.strip() == "3" or
          "生成Multi-Authority" in user_requirement or "生成多权威" in user_requirement or
          latest_content.strip() == "4" or "可撤销" in user_requirement or "Revocable" in user_requirement):
        if latest_content.strip() == "2" or "生成KP-ABE" in user_requirement:
            policy_json = json.dumps({
                "model": "KP-ABE",
                "logic": "属性A AND (属性B OR 属性C)",
                "attributes": ["属性A", "属性B", "属性C"],
                "functional_requirements": "实现KP-ABE数据加密和解密功能",
                "input_format": "JSON格式，包含密文属性集合和明文数据",
                "output_format": "JSON格式，包含密文数据和密文属性集合"
            }, ensure_ascii=False)
        elif latest_content.strip() == "4" or "可撤销" in user_requirement or "Revocable" in user_requirement or revocation_requested:
            policy_json = json.dumps({
                "model": "Revocable CP-ABE",
                "logic": "属性A AND (属性B OR 属性C) AND epoch=1",
                "attributes": ["属性A", "属性B", "属性C", "epoch"],
                "functional_requirements": "实现可撤销（时间片）CP-ABE，提供密钥更新与撤销示例",
                "input_format": "JSON格式，包含属性和明文数据",
                "output_format": "JSON格式，包含密文数据和访问策略",
                "revocation": revocation_default,
            }, ensure_ascii=False)
        elif latest_content.strip() == "1" or "生成CP-ABE" in user_requirement:
            policy_json = json.dumps({
                "model": "CP-ABE",
                "logic": "属性A AND (属性B OR 属性C)",
                "attributes": ["属性A", "属性B", "属性C"],
                "functional_requirements": "实现数据加密和解密功能",
                "input_format": "JSON格式，包含属性和明文数据",
                "output_format": "JSON格式，包含密文数据和访问策略"
            }, ensure_ascii=False)
        elif latest_content.strip() == "3" or "生成Multi-Authority" in user_requirement or "生成多权威" in user_requirement:
            policy_json = json.dumps({
                "model": "Multi-Authority",
                "logic": "属性A@AuthorityA AND (属性B@AuthorityB OR 属性C@AuthorityC)",
                "attributes": ["属性A@AuthorityA", "属性B@AuthorityB", "属性C@AuthorityC"],
                "functional_requirements": "实现多权威属性加密和解密功能",
                "authority_list": ["AuthorityA", "AuthorityB", "AuthorityC"],
                "input_format": "JSON格式，包含属性@权威和明文数据",
                "output_format": "JSON格式，包含密文数据、访问策略和属性@权威信息"
            }, ensure_ascii=False)
        else:
            policy_json = json.dumps({
                "model": "CP-ABE",
                "logic": "属性A AND (属性B OR 属性C)",
                "attributes": ["属性A", "属性B", "属性C"],
                "functional_requirements": "实现数据加密和解密功能",
                "input_format": "JSON格式，包含属性和明文数据",
                "output_format": "JSON格式，包含密文数据和访问策略"
            }, ensure_ascii=False)
    # Last resort: check for model mentions in user requirement (not in all_content to avoid false positives)
    elif "加密模型：KP-ABE" in user_requirement or "加密模型: KP-ABE" in user_requirement:
        policy_json = json.dumps({
            "model": "KP-ABE",
            "logic": "属性A AND (属性B OR 属性C)",
            "attributes": ["属性A", "属性B", "属性C"],
            "functional_requirements": "实现KP-ABE数据加密和解密功能",
            "input_format": "JSON格式，包含密文属性集合和明文数据",
            "output_format": "JSON格式，包含密文数据和密文属性集合"
        }, ensure_ascii=False)
    elif "加密模型：CP-ABE" in user_requirement or "加密模型: CP-ABE" in user_requirement:
        policy_json = json.dumps({
            "model": "CP-ABE",
            "logic": "属性A AND (属性B OR 属性C)",
            "attributes": ["属性A", "属性B", "属性C"],
            "functional_requirements": "实现数据加密和解密功能",
            "input_format": "JSON格式，包含属性和明文数据",
            "output_format": "JSON格式，包含密文数据和访问策略"
        }, ensure_ascii=False)
    else:
        try:
            json_candidates = re.findall(r"\{[\s\S]*\}", latest_content)
            if json_candidates:
                candidate = json_candidates[-1]
                json.loads(candidate)
                policy_json = candidate
        except Exception:
            policy_json = None

    if policy_json:
        try:
            policy_data = json.loads(policy_json) if isinstance(policy_json, str) else policy_json
        except Exception:
            policy_data = None
        if isinstance(policy_data, dict):
            needs_revocation = revocation_requested or str(policy_data.get("model", "")).lower().startswith("revocable")
            if "revocation" not in policy_data:
                if needs_revocation:
                    policy_data["revocation"] = revocation_default
                    if policy_data.get("model") in ("CP-ABE", "Revocable CP-ABE") and "epoch" not in policy_data.get("logic", ""):
                        policy_data["logic"] = (policy_data.get("logic") or "") + " AND epoch=1"
                else:
                    policy_data["revocation"] = {"enabled": False}
            policy_json = json.dumps(policy_data, ensure_ascii=False)

    custom_instance = {
        'instance_id': repo_name,
        'repo': repo_name,
        'base_commit': 'main',
        'problem_statement': problem_statement,
        'patch': ''
    }

    print(f"正在初始化仓库上下文: {repo_name}")
    set_current_issue(instance_data=custom_instance)

    messages = [
        {
            "role": "user",
            "content": get_task_instruction(custom_instance, include_pr=True, include_hint=True),
        }
    ]
    if policy_json:
        messages.append({
            "role": "user",
            "content": "POLICY_JSON:\n" + policy_json,
        })

    return Command(
        goto="coding_agent",
        update={"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *messages]},
        graph=Command.PARENT,
    )
