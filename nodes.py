from model.state import State
from model.subquery import SubQuery
from model.aggregated_results import AggregatedResults
from langchain_core.prompts import ChatPromptTemplate
import re
from utils import search_duckduck_go, extract_content

def rectify_query(llm, state: State)-> State:
    query_rectify_template = """
            You are an assistant specialized in rewriting and correcting the input queries by user.
            You review the query for spelling, grammar and reconstruct it, ensuring it is correct and the original message is preserved.
            However, you let the query remain unchanged if nothing is to be corrected.

            User Query: "{query}"
            """

    rectify_prompt = ChatPromptTemplate.from_template(query_rectify_template)

    out = llm.invoke(rectify_prompt.format(query=state["original_query"]))
    original_query = out
    return {"original_query": original_query}


def parse_query(llm,  state: State) -> State:
    query_parsing_template = """
            You are an assistant specialized in breaking user queries into smaller, logical subqueries.
            Decompose the following query into distinct, manageable subqueries:

            User Query: "{query}"

            Provide the subqueries as a numbered list, one per line.
            Example input: What is X and how does it affect Y?
            Example output:
            1. What is X?
            2. How does X affect Y?"""

    parsing_prompt = ChatPromptTemplate.from_template(query_parsing_template)
    out = llm.invoke(parsing_prompt.format(query=state["original_query"]))
    subqueries = []
    for subquery in out.split("\n"):
        if subquery.strip():
            s = SubQuery()
            s["query"] = re.sub(r"^\d+\.\s+", "", subquery)
            s["attempts"] = 0
            s["status"] = "pending"
            subqueries.append(s)
    return {"subqueries": subqueries}


def retrieve_content(llm, state: State) -> State:
    summarize_template = """
    You are an AI assistant tasked with summarizing lengthy articles.
    Summarize the following article content in a concise and clear way:

    Article Content:
    {content}
    """

    summarize_prompt = ChatPromptTemplate.from_template(summarize_template)

    for subquery in state["subqueries"]:
        if subquery.get("status") == "completed":
            continue
        subquery["status"] = "in_progress"
        subquery["attempts"] += 1

        try:
            print(f"🔍 Searching for subquery: '{subquery['query']}' (Attempt {subquery['attempts']})")
            search_results = search_duckduck_go(subquery['query'])

            result = dict()
            for search in search_results:
                if "content" not in result:
                    if "content" not in result:
                        result["content"] = extract_content(search["href"])
                    if result.get("content"):
                        print(f"result->{result.get("content")}")
                        out = llm.invoke(summarize_prompt.format(content=result["content"]))
                        result["summary"] = out
                        result["reference"] = search["href"]
                        break
                    else:
                        result["summary"] = "Content extraction failed."

            subquery["result"] = result
            subquery["status"] = "completed"

        except Exception as e:
            subquery["status"] = "failed"
            print(f"❌ Failed to retrieve results for subquery: '{subquery['query']}' | Error: {e}")
    return state


def aggregate_results(llm, state: State) -> State:
    aggregate_template = """
    You are an AI assistant tasked with aggregating and summarizing multiple content pieces into a single, concise, and coherent summary.
    Ensure that the summary maintains clarity and relevance.

    Individual Summaries:
    {summaries}

    Generate a final cohesive summary:
    """

    aggregate_prompt = ChatPromptTemplate.from_template(aggregate_template)

    summaries = []
    references = []
    result = AggregatedResults()

    for subquery in state["subqueries"]:
        if subquery["status"] == "completed" and "result" in subquery:
            summary = subquery["result"].get("summary", "")
            reference = subquery["result"].get("reference", "")

            if summary:
                summaries.append(f"- {summary}")
            if reference:
                references.append(reference)

    try:
        if summaries:
            combined_summaries = "\n".join(summaries)
            out = llm.invoke(aggregate_prompt.format(summaries=combined_summaries))
            result["summary"] = out
        else:
            result["summary"] = "No valid summaries were generated from the subqueries."

        result["references"] = ";".join(references)

    except Exception as e:
        state["final_summary"] = f"❌ Failed to generate final summary: {e}"
        print(f"❌ Error during final summarization: {e}")

    return {"aggregated_results": result}


def generate_final_output(llm, state: State) -> State:
    final_output_template = """
    You are an expert AI assistant tasked with presenting a final, polished answer based on aggregated summaries from multiple reliable sources.

    ### Original Query:  
    "{query}"

    ### Aggregated Summaries:  
    {aggregated_summaries}

    ### Task:  
    1. Craft a **clear, concise, and informative response** directly addressing the original query.  
    2. Ensure the response is **well-structured**, **coherent**, and captures the **key insights** from the aggregated summaries.  
    3. Provide a **list of references** for further reading, formatted as hyperlinks.

    ### Format:  
    **Answer:**  
    [Your response here]

    **References:**  
    1. [Reference 1](Link 1)  
    2. [Reference 2](Link 2)  
    3. [Reference 3](Link 3)
    """

    final_output_prompt = ChatPromptTemplate.from_template(final_output_template)
    output = ""
    try:
        out = llm.invoke(final_output_prompt.format(
            query=state["original_query"],
            aggregated_summaries=state["aggregated_results"]
        ))

        output = out

    except Exception as e:
        state["final_output"] = f"❌ Failed to generate final output: {e}"
        print(f"❌ Error during final output generation: {e}")

    return {"output": output}
