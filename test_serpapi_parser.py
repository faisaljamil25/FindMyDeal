from unittest.mock import patch, MagicMock
import json
from serpapi_parser import fetch

mock_shopping_response = {
    "shopping_results": [
        {
            "title": "Apple iPhone 16 Pro",
            "price": "$999.00",
            "extracted_price": 999.00,
            "product_id": "123456789",
            "product_link": "https://www.bestbuy.com/product/iphone16pro",
        },
        {
            "title": "Apple iPhone 16 Pro - Monthly",
            "price": "$38.57/mo",
            "extracted_price": 38.57,
            "product_id": "987654321",
            "product_link": "https://www.apple.com/iphone/16-pro-monthly",
        },
        {
            "title": "iPhone 16 Pro from ItsWorthMore",
            "product_id": "111222333",
            "product_link": "https://www.google.com/shopping/product/abc",
            "serpapi_product_api": "https://serpapi.com/search.json?engine=google_product&product_id=111222333",
        },
    ]
}

mock_product_detail_response = {
    "sellers_results": {
        "online_sellers": [
            {
                "name": "ItsWorthMore",
                "direct_link": "https://buy.itsworthmore.com/product/iphone-16",
                "total_price": "$1,050.00",
            }
        ]
    }
}


@patch("serpapi.GoogleSearch.get_dict", return_value=mock_shopping_response)
@patch("requests.get")
def test_fetch(mock_requests_get, mock_get_dict):
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_product_detail_response
    mock_requests_get.return_value = mock_resp

    results = fetch("iPhone 16 Pro", "US")

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    test_fetch()
