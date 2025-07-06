from domain_map import DOMAINS


def get_google_domain(country_code: str) -> str | None:
    return DOMAINS.get(country_code.lower())
