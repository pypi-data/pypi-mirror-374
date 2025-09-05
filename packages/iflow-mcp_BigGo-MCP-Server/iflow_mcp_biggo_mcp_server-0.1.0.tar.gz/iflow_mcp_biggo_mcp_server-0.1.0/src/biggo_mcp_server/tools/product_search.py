from logging import getLogger
from typing import Annotated
from mcp.server.fastmcp import Context
from pydantic import Field

from ..services.product_search import ProductSearchService
from ..types.responses import ProductSearchToolResponse
from ..lib.utils import get_setting

logger = getLogger(__name__)


async def product_search(
    ctx: Context,
    query: Annotated[
        str,
        Field(
            description="""Search query""",
            examples=["iphone", "護唇膏"],
        ),
    ],
) -> str:
    """Product Search"""
    logger.info("product search, query: %s", query)

    setting = get_setting(ctx)
    service = ProductSearchService(setting)
    ret = await service.search(query)

    return ProductSearchToolResponse(product_search_result=ret).slim_dump()
