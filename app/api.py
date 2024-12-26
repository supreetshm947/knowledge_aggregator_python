from fastapi import FastAPI
from graph import get_graph
from langchain_google_genai import GoogleGenerativeAI

app = FastAPI()

LLM = GoogleGenerativeAI(model="gemini-1.5-flash-latest")
GRAPH = get_graph(LLM)


@app.get("/answer")
def process_query(query: str):
    state = GRAPH.invoke({"original_query": query})
    return state["output"]
