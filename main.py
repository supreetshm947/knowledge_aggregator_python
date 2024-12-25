import requests
import os
from dotenv import load_dotenv

load_dotenv()

def google_search(query, limit=1, sort="date"):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_API_KEY"),
        "cx": os.getenv("SEARCH_ENGINE_ID"),
        "q": query,
        "num": limit,
        "sort": sort
    }

    response = requests.get(url, params)

    if response.status_code==200:
        data = response.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            })
        return results
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

print(google_search("Breakthroughs in AI"))