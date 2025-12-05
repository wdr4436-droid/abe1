import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain_text_splitters import MarkdownHeaderTextSplitter

from sentence_transformers import SentenceTransformer   # 鐩存帴鎷垮簳灞傛帴鍙?from accelerate import Accelerator
import torch
import gc
from dotenv import load_dotenv

load_dotenv()
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com/'
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "Qwen/Qwen3-Embedding-0.6B")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-code-v1",
    #model_name=EMBEDDING_MODEL_PATH,
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": False}
)

md_folder_path = "/media/xidiannss/nbagent/src/crypto_agent/agents/abe_agent/planning/RAG/doc/deepwiki"

# 定义如何分割Markdown文档
headers_to_split_on = [
    ("#", "Header1"),
    ("##", "Header2"),
]
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False
)

all_docs = []

for root, _, files in os.walk(md_folder_path):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)

            with open(file_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            docs = markdown_splitter.split_text(markdown_content)

            for doc in docs:
                doc.metadata["source"] = file_path
                
                doc.metadata.setdefault("Header1", "")
                doc.metadata.setdefault("Header2", "")

            all_docs.extend(docs)

URI = "./milvus_0.6b.db"

if all_docs:
    vector_store = Milvus.from_documents(
        documents=all_docs,
        embedding=embeddings,
        collection_name="markdown_collection",
        connection_args={"uri": URI},
    )
    print(f"成功将 {len(all_docs)} 个文档块从 {len(files)} 个文件存入Milvus")
else:
    print("未找到任何Markdown文件")