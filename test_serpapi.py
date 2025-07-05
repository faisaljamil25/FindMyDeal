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


# test_serpapi("iPhone 16 Pro 128GB", "United States")


def parse_and_sort_results():
    with open("serpapi_raw_response.json", "r") as f:
        raw_results = json.load(f)

    shopping_results = raw_results.get("shopping_results", [])
    parsed_results = []

    for item in shopping_results:
        price = item.get("price")
        extracted_price = item.get("extracted_price")

        if is_installment(price, extracted_price):
            continue

        title = item.get("title")
        link = item.get("product_link")

        if not extracted_price or not title:
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


def is_installment(price_str: str, extracted_price: float) -> bool:
    if not price_str or not extracted_price:
        return False
    price_value = price_str.replace("$", "").strip()
    return price_value != str(extracted_price)


parse_and_sort_results()
