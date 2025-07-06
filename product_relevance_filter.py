import re
import statistics

KEYWORDS = [
    "case",
    "cover",
    "screen protector",
    "charger",
    "cable",
    "stand",
    "mount",
    "holder",
    "wallet",
    "pouch",
    "skin",
    "sticker",
    "ring",
    "strap",
    "band",
    "dock",
    "box only",
    "empty box",
    "packaging",
    "manual",
    "parts only",
    "cracked",
    "broken",
    "damaged",
    "defective",
    "not working",
    "for parts",
    "repair",
    "scratched",
    "water damage",
    "cracked screen",
    "broken screen",
    "refurbished",
    "renewed",
    "open box",
    "used",
    "pre-owned",
    "second hand",
]


def extract_key_terms(query: str) -> list:
    ignore_words = [
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
    ]

    query_lower = query.lower()
    words = re.sub(r"[^\w\s]", " ", query_lower).split()
    key_terms = []
    for word in words:
        if word not in ignore_words and len(word) > 1:
            key_terms.append(word)

    return key_terms


def matches_query_keywords(title: str, query: str) -> bool:
    key_terms = extract_key_terms(query)
    if not key_terms:
        return True

    title_lower = title.lower()
    matched_terms = 0
    for term in key_terms:
        if term in title_lower:
            matched_terms += 1

    match_ratio = matched_terms / len(key_terms)
    return match_ratio >= 0.7


def is_relevant_product(title: str, query: str = "") -> bool:
    if not title:
        return False

    title_lower = title.lower()

    for keyword in KEYWORDS:
        if keyword in title_lower:
            return False

    if query and not matches_query_keywords(title, query):
        return False

    return True


def filter_relevant_products(
    products: list,
    query: str = "",
    max_results: int = 10,
    price_threshold: float = 0.5,
) -> list:
    relevant_products = []

    for product in products:
        title = product.get("productName", "")
        if is_relevant_product(title, query):
            relevant_products.append(product)

    relevant_products.sort(key=lambda x: x.get("price", float("inf")))

    if len(relevant_products) >= 3:
        prices = [p.get("price", 0) for p in relevant_products if p.get("price", 0) > 0]

        if len(prices) >= 3:
            median_price = statistics.median(prices)
            min_price = median_price * price_threshold

            relevant_products = [
                product
                for product in relevant_products
                if product.get("price", 0) >= min_price
            ]

    return relevant_products[:max_results]
