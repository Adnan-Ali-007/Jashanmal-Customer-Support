"""Custom Gemini Embeddings wrapper for LangChain"""
import os
from typing import List
import google.generativeai as genai
from langchain_core.embeddings import Embeddings


class GeminiEmbeddings(Embeddings):
    """Gemini embeddings using google.generativeai"""
    
    def __init__(self, model: str = "models/embedding-001"):
        self.model = model
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        genai.configure(api_key=api_key)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result["embedding"])
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query"""
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]
