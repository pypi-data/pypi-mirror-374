import json
from logging import getLogger
from typing import Annotated, Any
from mcp.server.fastmcp import Context
from pydantic import Field

from biggo_mcp_server.types.setting import BigGoMCPSetting
from ..types.responses import (
    SpecIndexesToolResponse,
    SpecMappingToolResponse,
    SpecSearchToolResponse,
)
from ..lib.utils import get_setting
from ..services.spec_search import SpecSearchService

logger = getLogger(__name__)


async def spec_indexes(
    ctx: Context,
) -> Annotated[str, Field(description="List of Elasticsearch indexes")]:
    """Elasticsearch Indexes for Product Specification.

    It is REQUIRED to use this tool first before running any specification search.
    """
    logger.info("spec indexes")
    setting = get_setting(ctx)
    service = SpecSearchService(setting)
    async with service.session():
        indexes = await service.spec_indexes()
    return SpecIndexesToolResponse(indexes=indexes).slim_dump()


async def spec_mapping(
    ctx: Context,
    index: Annotated[
        str,
        Field(
            description="""
                          Elasticsearch index

                          Steps to obtain this argument.
                          1. Use 'spec_indexes' tool to get the list of indexes
                          2. Choose the most relevant index
                          """
        ),
    ],
) -> Annotated[
    str, Field(description="Elasticsearch mappings plus an example document")
]:
    """Elasticsearch Mapping For Product Specification.

    Use this tool after you have the index, and need to know the mapping in order to query the index.
    Available indexes can be obtained by using the 'spec_indexes' tool.
    """
    logger.info("spec mapping, index: %s", index)
    setting = get_setting(ctx)
    service = SpecSearchService(setting)
    try:
        async with service.session():
            mapping = await service.spec_mapping(index)
    except Exception as e:
        raise Exception(
            f"You must know the available indexes before using this tool. Error: {e}"
        )
    return SpecMappingToolResponse(
        mappings=mapping.mappings, example_document=mapping.example_document
    ).slim_dump()


async def spec_search(
    ctx: Context,
    index: Annotated[
        str,
        Field(
            description="""
                          Elasticsearch index

                          Steps to obtain this argument.
                          1. Use 'spec_indexes' tool to get the list of indexes
                          2. Choose the most relevant index
                          """
        ),
    ],
    elasticsearch_query: Annotated[
        str | dict[str, Any],
        Field(
            description=f"""
              Elasticsearch(ES8) query tool

              Required steps:
              1. First use 'spec_mapping' to get index mapping
              2. Result limit ≤ 10
              3. Must exclude documents with 'status'='deleted'
              4. Must include documents with 'region'='{BigGoMCPSetting().region.value.lower()}'

              When to sort:
              - For optimal performance (e.g., most energy-efficient refrigerator) → sort by power consumption
              - For specific attribute extremes (e.g., smallest refrigerator) → sort by height
              - When only querying products matching specific parameters (e.g., phones with 16GB RAM) → no sorting needed

              Note: All spec fields are under the 'spec' key, must add 'spec' prefix when querying
              Example paths: specs.physical_specs.weight, specs.technical_specs.water_resistance.depth
              """,
            examples=[
                {
                    "query": {
                        "bool": {
                            "must_not": [{"match": {"status": "deleted"}}],
                            "must": [
                                {
                                    "range": {
                                        "specs.physical_specifications.dimensions.height": {
                                            "gte": 1321,
                                            "lte": 2321,
                                        }
                                    }
                                },
                                {"match": {"region": "tw"}},
                            ],
                        }
                    },
                    "size": 5,
                    "sort": [
                        {"specs.physical_specifications.dimensions.height": "asc"}
                    ],
                }
            ],
        ),
    ],
) -> str:
    """Product Specification Search.

    Index mapping must be aquired before using this tool.
    Use 'spec_mapping' tool to get the mapping of the index.
    """
    logger.info("spec search, index: %s, query: %s", index, elasticsearch_query)

    setting = get_setting(ctx)
    service = SpecSearchService(setting)
    try:
        async with service.session():
            if isinstance(elasticsearch_query, str):
                query: dict[str, Any] = json.loads(elasticsearch_query)
            else:
                query = elasticsearch_query
            hits = await service.search(index, query)
    except Exception as e:
        raise Exception(
            f"You must know the mapping of the index before using this tool. Error: {e}"
        )
    return SpecSearchToolResponse(hits=hits).slim_dump()
