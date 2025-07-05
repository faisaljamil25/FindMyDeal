import os
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")


def remove_dollar(price: str) -> Optional[float]:
    try:
        return float(price.replace("$", "").replace(",", "").strip())
    except Exception:
        return None


def fetch_sellers(serpapi_url: str, title: str) -> Optional[dict]:
    sellers = []
    try:
        if "api_key=" not in serpapi_url:
            serpapi_url += f"&api_key={API_KEY}"
        resp = requests.get(serpapi_url, timeout=10)
        data = resp.json()
        sellers = data.get("sellers_results", {}).get("online_sellers", [])
    except Exception as e:
        print(f"Error: {e}")
        return None

    for seller in sellers:
        total_price = seller.get("total_price")
        if total_price and not total_price.endswith("/mo"):
            final_price = remove_dollar(total_price)
            if final_price:
                return {
                    "link": seller.get("direct_link", ""),
                    "price": final_price,
                    "currency": "USD",
                    "productName": title,
                }

    return None


def fetch_sellers_from_id(product_id: str, location: str, title: str) -> Optional[dict]:
    url = (
        f"https://serpapi.com/search.json"
        f"?engine=google_product&product_id={product_id}&location={location}&api_key={API_KEY}"
    )
    return fetch_sellers(url, title)


def fetch(query: str, location: str) -> list:
    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "api_key": API_KEY,
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"Error: {e}")
        return []

    shopping_results = sorted(
        results.get("shopping_results", []), key=lambda x: x.get("position", 999)
    )[:15]

    parsed_results = []

    for item in shopping_results:
        title = item.get("title")
        price_str = item.get("price")
        extracted_price = item.get("extracted_price")
        product_link = item.get("product_link")
        serpapi_product_api = item.get("serpapi_product_api")
        product_id = item.get("product_id")

        if product_link and product_link.startswith(
            "https://www.google.com/shopping/product"
        ):
            result = None
            if serpapi_product_api:
                result = fetch_sellers(serpapi_product_api, title)
            elif product_id:
                result = fetch_sellers_from_id(product_id, location, title)

            if result:
                parsed_results.append(result)

        elif not price_str.endswith("/mo"):
            parsed_results.append(
                {
                    "link": product_link,
                    "price": extracted_price,
                    "currency": "USD",
                    "productName": title,
                }
            )

    sorted_results = sorted(parsed_results, key=lambda x: x["price"])
    return sorted_results
