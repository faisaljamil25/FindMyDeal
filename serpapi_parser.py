import os
import json
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("SERPAPI_API_KEY")

# temporary return value coz None gives error in the code
dummy_product = {
    "link": "",
    "price": 0.0,
    "currency": "USD",
    "productName": "",
}


def is_total_price(price_str: str, extracted_price: float) -> bool:
    if not price_str or not extracted_price:
        return False
    price_value = price_str.replace("$", "").strip()
    return price_value == str(extracted_price)


def remove_dollar(price: str) -> float:
    return float(price.replace("$", "").replace(",", "").strip())


def fetch_sellers(serpapi_url: str, title: str) -> dict:
    sellers = []
    try:
        if "api_key=" not in serpapi_url:
            serpapi_url += f"&api_key={API_KEY}"
        resp = requests.get(serpapi_url)
        data = resp.json()
        sellers = data.get("sellers_results", {}).get("online_sellers", [])
    except Exception as e:
        print(f"Error: {e}")
        return dummy_product

    for seller in sellers:
        total_price = seller.get("total_price")
        if total_price:
            final_price = remove_dollar(total_price)
            return {
                "link": seller.get("direct_link", ""),
                "price": final_price,
                "currency": "USD",
                "productName": title,
            }

    return dummy_product


def fetch_sellers_from_id(product_id: str, location: str, title: str) -> dict:
    url = (
        f"https://serpapi.com/search.json"
        f"?engine=google_product&product_id={product_id}&location={location}&api_key={API_KEY}"
    )
    return fetch_sellers(url, title)


def fetch(query: str, location: str):
    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "api_key": API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    shopping_results = results.get("shopping_results", [])

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

        elif is_total_price(price_str, extracted_price):
            parsed_results.append(
                {
                    "link": product_link,
                    "price": extracted_price,
                    "currency": "USD",
                    "productName": title,
                }
            )

    sorted_results = sorted(parsed_results, key=lambda x: x["price"])
    with open("result.json", "w") as f:
        json.dump(sorted_results, f, indent=2)
    return
