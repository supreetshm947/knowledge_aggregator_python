from langgraph.graph import StateGraph, START, END
from model.state import State
from functools import partial
from nodes import rectify_query, parse_query, retrieve_content, aggregate_results, generate_final_output
# from load_dotenv import load_dotenv
#
# load_dotenv()

def get_graph(llm):
    rectify_query_node = partial(rectify_query, llm)
    parse_query_node = partial(parse_query, llm)
    retrieve_content_node = partial(retrieve_content, llm)
    aggregate_results_node = partial(aggregate_results, llm)
    generate_final_node = partial(generate_final_output, llm)

    graph_builder = StateGraph(State)

    graph_builder.add_node("rectify", rectify_query_node)
    graph_builder.add_node("parse", parse_query_node)
    graph_builder.add_node("retrieve", retrieve_content_node)
    graph_builder.add_node("aggregate", aggregate_results_node)
    graph_builder.add_node("final_output", generate_final_node)

    graph_builder.add_edge(START, "rectify")
    graph_builder.add_edge("rectify", "parse")
    graph_builder.add_edge("parse", "retrieve")
    graph_builder.add_edge("retrieve", "aggregate")
    graph_builder.add_edge("aggregate", "final_output")
    graph_builder.add_edge("final_output", END)

    graph = graph_builder.compile()
    
    return graph


from langchain_google_genai import GoogleGenerativeAI
LLM = GoogleGenerativeAI(model="gemini-1.5-flash-latest")
GRAPH = get_graph(LLM)

# state = GRAPH.invoke({"original_query": "What are the laest breakthroughs in AI and what are there ethical implications?"})
# # print(state["output"])
# state = GRAPH.invoke({"original_query": "What is ANYCSP?"})
# print(state["output"])