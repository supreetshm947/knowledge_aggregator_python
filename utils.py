from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
import re

def search_duckduck_go(query):
    result = DDGS().text(
        keywords=query,
        region="wt-wt",
        safesearch="off",
        timelimit="7d",
        max_results=10
    )

    return result


def extract_content(url: str):
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {url}, status code: {response.status_code}")
        return ""

    soup = BeautifulSoup(response.content, 'html.parser')

    for script in soup(["script", "style", "footer", "nav", "aside"]):
        script.extract()

    text = soup.get_text(separator='\n')
    text = re.sub(r'\n+', '\n', text).strip()

    return text[:5000]