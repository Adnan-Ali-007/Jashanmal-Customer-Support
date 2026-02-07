"""Test status query routing"""
import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from agents.agents import agent
from dotenv import load_dotenv

load_dotenv()

queries = [
    "status ORD-12348",
    "check status ORD-12348",
    "what's the status of ORD-12348",
    "track order ORD-12348",
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)
    
    config = {"configurable": {"thread_id": "test"}}
    result = agent.invoke({"query": query}, config=config)
    
    print(f"Route: {result['route']}")
    print(f"\nAnswer:\n{result['answer'][:200]}...")
