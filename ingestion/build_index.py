import json
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from gemini_embeddings import GeminiEmbeddings

load_dotenv()

# -----------------------------
# PATHS
# -----------------------------
INPUT_FILE = Path("data/processed/faqs.json")
INDEX_DIR = Path("data/processed/faiss_index")

# -----------------------------
# LOAD DATA
# -----------------------------
with open(INPUT_FILE, encoding="utf-8") as f:
    raw_docs = json.load(f)

documents = []
texts = []

for item in raw_docs:
    if "question" in item:
        content = f"Question: {item['question']}\nAnswer: {item['answer']}"
    else:
        content = item["text"]

    texts.append(content)
    documents.append(
        Document(
            page_content=content,
            metadata={
                "category": item["category"],
                "source": item["source"],
            },
        )
    )

print(f"Loaded {len(documents)} documents")

# -----------------------------
# BUILD FAISS INDEX WITH GEMINI EMBEDDINGS
# -----------------------------
print("Building FAISS index with Gemini embeddings...")

embeddings = GeminiEmbeddings(model="models/embedding-001")

vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embeddings
)

vectorstore.save_local(INDEX_DIR)

print(f"✓ FAISS index saved at: {INDEX_DIR.resolve()}")
