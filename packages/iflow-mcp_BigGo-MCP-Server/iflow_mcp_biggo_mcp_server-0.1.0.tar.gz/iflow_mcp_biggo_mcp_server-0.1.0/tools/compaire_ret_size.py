from dataclasses import dataclass
from biggo_mcp_server.types.api_ret.product_search import ProductSearchAPIRet


@dataclass(slots=True)
class Statistics:
    original: int
    cleaned: int


def print_length_comparison(original: int, cleaned: int):
    print(f"""Original length: {original}, Cleaned length: {cleaned}. 
        Current Percentage = ({(cleaned/original) * 100})%
        Original / Cleaned = {original/cleaned}
        """)


def product_search_api_ret() -> Statistics:
    print("== product_search_api_ret ==")
    # original response
    with open("./.data/original_prod_search_ret.json", "r") as f:
        original = f.read()

    # cleaned
    clean_data = ProductSearchAPIRet.model_validate_json(original)
    clean_data = clean_data.model_dump_json(exclude_none=True)

    # compaire
    print_length_comparison(original=len(original), cleaned=len(clean_data))

    return Statistics(original=len(original), cleaned=len(clean_data))


def main():
    product_search_statistic = product_search_api_ret()

    print("== Total length comparison ==")
    original = product_search_statistic.original
    cleaned = product_search_statistic.cleaned
    print_length_comparison(original=original, cleaned=cleaned)


if __name__ == "__main__":
    main()
