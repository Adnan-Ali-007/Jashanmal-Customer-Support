import json
from pathlib import Path
import numpy as np
import faiss
import google.generativeai as genai
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

load_dotenv()


INPUT_FILE = Path("data/processed/faqs.json")
INDEX_DIR = Path("data/processed/faiss_index")


genai.configure()
EMBED_MODEL = "models/embedding-001"

def embed_texts(texts: list[str]) -> np.ndarray:
    vectors = []
    for text in texts:
        res = genai.embed_content(
            model=EMBED_MODEL,
            content=text,
            task_type="retrieval_document",
        )
        vectors.append(res["embedding"])
    return np.array(vectors, dtype="float32")


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


print("Generating embeddings using Gemini...")
vectors = embed_texts(texts)


print("Building FAISS index...")

dim = vectors.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(vectors)

docstore = InMemoryDocstore(
    {str(i): documents[i] for i in range(len(documents))}
)

index_to_docstore_id = {i: str(i) for i in range(len(documents))}

vectorstore = FAISS(
    embedding_function=None,  # embeddings already computed
    index=index,
    docstore=docstore,
    index_to_docstore_id=index_to_docstore_id,
)

vectorstore.save_local(INDEX_DIR)

print(f"FAISS index saved at: {INDEX_DIR.resolve()}")
