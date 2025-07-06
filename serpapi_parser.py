import os
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
from product_relevance_filter import filter_relevant_products, is_relevant_product

from utils import (
    get_currency_from_symbol,
    get_google_domain,
    parse_price,
    get_price,
)


load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")
MAX_ITEMS = int(os.getenv("MAX_SHOPPING_RESULTS", 30))


def fetch_sellers(serpapi_url: str, title: str) -> dict | None:
    sellers = []
    try:
        if "api_key=" not in serpapi_url:
            serpapi_url += f"&api_key={API_KEY}"
        resp = requests.get(serpapi_url, timeout=10)
        data = resp.json()
        sellers = data.get("sellers_results", {}).get("online_sellers", [])
        title = data.get("product_results", {}).get("title", title)
    except Exception as e:
        print(f"[SerpAPI Seller Fetch] Error: {e}")
        return None

    for seller in sellers:
        base_price = seller.get("base_price")
        if (
            base_price
            and not base_price.endswith("/mo")
            and "/month" not in base_price.lower()
        ):
            price_currency = parse_price(base_price)
            if price_currency:
                currency, final_price = price_currency
                if final_price and final_price != 0.0:
                    return {
                        "link": seller.get("direct_link", ""),
                        "price": final_price,
                        "currency": currency,
                        "productName": title,
                    }

        additional_price = seller.get("additional_price", {})
        taxes_str = additional_price.get("taxes", "")
        shipping_str = additional_price.get("shipping", "")
        total_taxes = get_price(taxes_str)
        total_shipping = get_price(shipping_str)
        total_price = seller.get("total_price", "")
        if (
            total_price
            and not total_price.endswith("/mo")
            and "/month" not in total_price.lower()
        ):
            price_currency = parse_price(total_price)
            if price_currency:
                currency, final_price = price_currency
                if final_price and final_price != 0.0:
                    return {
                        "link": seller.get("direct_link", ""),
                        "price": final_price - (total_taxes + total_shipping),
                        "currency": currency,
                        "productName": title,
                    }

    return None


def fetch_sellers_from_id(
    product_id: str, country_code: str, google_domain: str, title: str
) -> dict | None:
    url = (
        f"https://serpapi.com/search.json"
        f"?engine=google_product&product_id={product_id}&gl={country_code}&google_domain={google_domain}&hl=en&api_key={API_KEY}"
    )
    return fetch_sellers(url, title)


def fetch(query: str, country_code: str) -> list:
    if not API_KEY:
        print(
            "API key is not set. Please set the SERPAPI_API_KEY environment variable."
        )
        return []

    if not query or not country_code:
        print("Query and country code must be provided.")
        return []

    google_domain = get_google_domain(country_code)
    if not google_domain:
        print(f"No domain found for country code: {country_code}")
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "gl": country_code.lower(),
        "hl": "en",
        "google_domain": google_domain,
        "api_key": API_KEY,
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"[SerpAPI Main Search] Error: {e}")
        return []

    shopping_results = sorted(
        results.get("shopping_results", []), key=lambda x: x.get("position", 999)
    )[:MAX_ITEMS]

    parsed_results = []

    for item in shopping_results:
        title = item.get("title")
        price_str = item.get("price")
        extracted_price = item.get("extracted_price")
        product_link = item.get("product_link")
        serpapi_product_api = item.get("serpapi_product_api")
        product_id = item.get("product_id")

        if not title or not is_relevant_product(title, query):
            continue

        if product_link and product_link.startswith(
            f"https://www.{google_domain}/shopping/product"
        ):
            result = None
            if serpapi_product_api:
                result = fetch_sellers(serpapi_product_api, title)
            elif product_id:
                result = fetch_sellers_from_id(
                    product_id, country_code, google_domain, title
                )

            if result:
                parsed_results.append(result)

        elif (
            price_str
            and not price_str.endswith("/mo")
            and "/month" not in price_str.lower()
        ):
            currency = get_currency_from_symbol(price_str.strip()[0])
            parsed_results.append(
                {
                    "link": product_link,
                    "price": float(extracted_price),
                    "currency": currency,
                    "productName": title,
                }
            )

    sorted_results = sorted(parsed_results, key=lambda x: x["price"])

    final_results = filter_relevant_products(
        sorted_results, query, max_results=10, price_threshold=0.5
    )

    return final_results
