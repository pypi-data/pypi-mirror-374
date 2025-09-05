from logging import getLogger
from typing import Annotated

from mcp.server.fastmcp import Context
from pydantic import Field

from ..lib.utils import get_setting
from ..services.price_history import PriceHistoryService
from ..types.responses import PriceHisotryGraphToolResponse, PriceHistoryToolResponse

logger = getLogger(__name__)


def price_history_graph(
    ctx: Context,
    history_id: Annotated[
        str,
        Field(
            description="""
              Product History ID - Get from 'history_id' field in product_search results
              """,
            examples=["tw_pmall_rakuten-nwdsl_6MONJRBOO", "tw_pec_senao-1363332"],
        ),
    ],
) -> str:
    """Link That Visualizes Product Price History"""

    logger.info("price history graph, history_id: %s", history_id)

    setting = get_setting(ctx)
    service = PriceHistoryService(setting)
    url = service.graph_link(history_id)

    return PriceHisotryGraphToolResponse(
        price_history_graph=f"![Price History Graph]({url})"
    ).slim_dump()


async def price_history_with_history_id(
    ctx: Context,
    history_id: Annotated[
        str,
        Field(
            description="""
              Product History ID - Get from 'history_id' field in product_search results
              """,
            examples=["tw_pmall_rakuten-nwdsl_6MONJRBOO", "tw_pec_senao-1363332"],
        ),
    ],
) -> str:
    """Product Price History With History ID"""

    logger.info("price history with history id, history_id: %s", history_id)

    setting = get_setting(ctx)
    service = PriceHistoryService(setting)
    ret = await service.history_with_history_id(history_id=history_id, days="180")
    if ret is None:
        return "No price history found"

    return PriceHistoryToolResponse(
        price_history_description=ret.description,
        price_history_graph=f"![Price History Graph]({ret.graph_link})",
    ).slim_dump()


async def price_history_with_url(
    ctx: Context,
    url: Annotated[str, Field(description="Product URL")],
) -> str:
    """Product Price History With URL"""

    logger.info("price history with url, url: %s", url)

    setting = get_setting(ctx)
    service = PriceHistoryService(setting)
    ret = await service.history_with_url(url=url, days="180")
    if ret is None:
        return "No price history found"

    return PriceHistoryToolResponse(
        price_history_description=ret.description,
        price_history_graph=f"![Price History Graph]({ret.graph_link})",
    ).slim_dump()
