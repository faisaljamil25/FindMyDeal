from serpapi import GoogleSearch
import os
import json
from dotenv import load_dotenv

load_dotenv()


def test_serpapi(query: str, location: str):
    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "api_key": os.getenv("SERP_API_KEY"),
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    with open("serpapi_raw_response.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Response saved to serpapi_raw_response.json")

    shopping_results = results.get("shopping_results", [])
    for item in shopping_results:
        print(f"{item['title']} - {item['price']} - {item['source']}")


test_serpapi("iPhone 16 Pro 128GB", "United States")
