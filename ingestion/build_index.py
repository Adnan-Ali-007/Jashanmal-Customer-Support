import json
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

load_dotenv()

INPUT_FILE = Path("data/processed/faqs.json")
INDEX_DIR = Path("data/processed/faiss_index")

# Use LangChain's GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

with open(INPUT_FILE, encoding="utf-8") as f:
    raw_docs = json.load(f)

documents = []

for item in raw_docs:
    if "question" in item:
        content = f"Question: {item['question']}\nAnswer: {item['answer']}"
    else:
        content = item["text"]

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

print("Building FAISS index with embeddings...")
vectorstore = FAISS.from_documents(documents, embeddings)

print("Saving index...")
vectorstore.save_local(INDEX_DIR)

print(f"✓ FAISS index saved at: {INDEX_DIR.resolve()}")
