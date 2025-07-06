from country_map import CURRENCY_SYMBOL_MAP, DOMAINS


def get_google_domain(country_code: str) -> str | None:
    return DOMAINS.get(country_code.lower())


def get_currency_from_symbol(sym: str) -> str | None:
    return CURRENCY_SYMBOL_MAP.get(sym)


def parse_price(price: str) -> tuple[str, float] | None:
    try:
        price = price.strip()
        if not price:
            return None
        symbol = price[0]
        currency = get_currency_from_symbol(symbol)
        if currency is None:
            return None
        numeric = float(price.replace(symbol, "").replace(",", "").strip())
        return (currency, numeric)
    except Exception:
        return None
