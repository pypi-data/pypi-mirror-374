from logging import getLogger
from typing import Any

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from .api_ret.price_history import PriceHistoryAPIRet
from .api_ret.product_search import ProductSearchAPIRet

logger = getLogger(__name__)


class BaseToolResponse(BaseModel):
    def slim_dump(self) -> str:
        return self.model_dump_json(exclude_none=True, exclude_defaults=True)


class ProductSearchToolResponse(BaseToolResponse):
    product_search_result: ProductSearchAPIRet
    reason: str | None = None
    display_rules: str | None = None

    @model_validator(mode="after")
    def post_init(self) -> Self:
        if len(self.product_search_result.list) == 0:
            self.reason = """
No results found. Possible reasons:
1. This search is much more complex than a simple product search.
2. The user is asking things related to product specifications.

If the problems might be related to the points listed above,
please use the 'spec_search' tool and try again.
            """
            return self

        # add display rules if result is not empty
        else:
            self.display_rules = """
As a product researcher, you need to find the most relavent product and present them in utmost detail.
Without following the rules listed bellow, the output will become useless, you must follow the rules before responding to the user.
All rules must be followed strictly.

Here are a list of rules you must follow:
Rule 1: Product image must be included when available, url is located in each object inside 'specs.images' field.
Rule 2: If no avaliable image exist, ignore the image field completely, don't even write anything image related for that single product.
Rule 3: Product urls must be included so that the user can by the product with a simple click if possible.
Rule 4: Display more then one relavent product if possible, having multiple choices is a good thing.
            """

        return self


class PriceHisotryGraphToolResponse(BaseToolResponse):
    price_history_graph: str
    display_rules: str = """
This is a markdown image link, it must be included in the final output. 
    """


class PriceHistoryToolResponse(BaseToolResponse):
    price_history_description: PriceHistoryAPIRet
    price_history_graph: str
    display_rules: str = """
Field explanation:
'price_history_description': includes detailed price history info.
'price_history_graph': includes a markdown image link used for visualizing price history.

Here are a list of rules you must follow:
Rule 1: Both 'price_history_description' and the link provided at 'price_history_graph' field must be included in the output.
Rule 2: Product url must be included, it can be found in 'price_history_description'
    """


class SpecIndexesToolResponse(BaseToolResponse):
    indexes: list[str]


class SpecMappingToolResponse(BaseToolResponse):
    mappings: dict[str, dict[str, Any]]
    example_document: dict[str, dict[str, Any]]
    note: str = """
Specifications are under the 'specs' field
Example fields paths:
- specs.physical_specs.weight
- specs.technical_specs.water_resistance.depth
- specs.sensors.gyroscope
"""


class SpecSearchToolResponse(BaseToolResponse):
    hits: list[dict[str, Any]]
    reason: str | None = None
    display_rules: str | None = None

    @model_validator(mode="after")
    def post_init(self) -> Self:
        # remove documents with status == deleted
        cleaned_hits: list[dict[str, Any]] = []
        for hit in self.hits:
            if hit["_source"].get("status", None) == "deleted":
                continue
            else:
                cleaned_hits.append(hit)

        logger.debug(
            "original hits: %s, cleaned_hits: %s", len(self.hits), len(cleaned_hits)
        )

        self.hits = cleaned_hits

        if len(self.hits) == 0:
            self.reason = """
No results found. Try:
1. For complex product searches → Use 'spec_search' tool
2. For specification-related queries → Use 'spec_search' tool
            """

        else:
            self.display_rules = """
Display product images (from 'specs.images.url' field) when available; omit image mentions if unavailable
            """

        return self
