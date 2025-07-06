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


def is_relevant_product(title: str) -> bool:
    if not title:
        return False

    title_lower = title.lower()

    for keyword in KEYWORDS:
        if keyword in title_lower:
            return False

    return True


def filter_relevant_products(products: list, max_results: int = 10) -> list:
    relevant_products = []

    for product in products:
        title = product.get("productName", "")
        if is_relevant_product(title):
            relevant_products.append(product)

    relevant_products.sort(key=lambda x: x.get("price", float("inf")))

    return relevant_products[:max_results]
