from typing import TypedDict
from model.aggregated_results import AggregatedResults
from model.subquery import SubQuery

class State(TypedDict):
    original_query: str
    subqueries: list[SubQuery]
    aggregated_results: AggregatedResults
    output: str