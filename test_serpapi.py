from serpapi import GoogleSearch
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("SERP_API_KEY")


def test_serpapi(query: str, location: str):
    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "api_key": API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    with open("serpapi_raw_response.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Response saved to serpapi_raw_response.json")

    shopping_results = results.get("shopping_results", [])
    for item in shopping_results:
        print(f"{item['title']} - {item['price']} - {item['source']}")


# test_serpapi("iPhone 16 Pro 128GB", "United States")


def parse_and_sort_results():
    with open("serpapi_raw_response.json", "r") as f:
        raw_results = json.load(f)

    shopping_results = raw_results.get("shopping_results", [])
    parsed_results = []

    for item in shopping_results:
        price = item.get("price")
        extracted_price = item.get("extracted_price")

        if not is_total_price(price, extracted_price):
            continue

        title = item.get("title")
        link = fetch_link(item)

        if not extracted_price or not title or not link:
            continue

        parsed_results.append(
            {
                "productName": title,
                "price": extracted_price,
                "currency": "USD",
                "link": link,
            }
        )

    result = sorted(parsed_results, key=lambda x: x["price"])

    with open("result.json", "w") as f:
        json.dump(result, f, indent=2)

    return


def is_total_price(price_str: str, extracted_price: float) -> bool:
    if not price_str or not extracted_price:
        return False
    price_value = price_str.replace("$", "").strip()
    return price_value == str(extracted_price)


def fetch_link(item: dict) -> str:
    product_link = item.get("product_link")
    if product_link and product_link.startswith(
        "https://www.google.com/shopping/product"
    ):
        serpapi_api_url = item.get("serpapi_product_api")
        if serpapi_api_url:
            serpapi_api_url += f"&api_key={API_KEY}"
            try:
                resp = requests.get(serpapi_api_url)
                data = resp.json()
                link = data["sellers_results"]["online_sellers"][0]["direct_link"]
                if link:
                    return link
            except Exception as e:
                print(f"Error resolving link: {e}")
    return product_link or ""


parse_and_sort_results()
