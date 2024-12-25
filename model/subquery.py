from typing import TypedDict

class SubQuery(TypedDict):
    query: str
    status: str
    reference: str
    attempts: int
    result: dict