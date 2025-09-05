"""
Just check if the tools can run without errors.
"""

from unittest.mock import MagicMock

import pytest

from biggo_mcp_server.tools.price_history import (
    price_history_graph,
    price_history_with_history_id,
    price_history_with_url,
)
from biggo_mcp_server.tools.product_search import product_search
from biggo_mcp_server.types.setting import BigGoMCPSetting

from .helper import *


@pytest.mark.asyncio
async def test_get_history(setting: BigGoMCPSetting):
    ctx = MagicMock()
    ctx.fastmcp = MagicMock()
    ctx.fastmcp.biggo_setting = setting

    history = await price_history_with_history_id(
        ctx=ctx,
        history_id="tw_pmall_rakuten-nwdsl_6MONJRBOO",
    )

    assert isinstance(history, str)


@pytest.mark.asyncio
async def test_get_history_with_url(setting: BigGoMCPSetting):
    ctx = MagicMock()
    ctx.fastmcp = MagicMock()
    ctx.fastmcp.biggo_setting = setting

    history = await price_history_with_url(
        ctx=ctx,
        url="https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=13660781",
    )
    assert isinstance(history, str)


@pytest.mark.asyncio
async def test_product_search(setting: BigGoMCPSetting):
    ctx = MagicMock()
    ctx.fastmcp = MagicMock()
    ctx.fastmcp.biggo_setting = setting

    search = await product_search(
        ctx=ctx,
        query="iphone",
    )

    assert isinstance(search, str)


def test_price_history_graph(setting: BigGoMCPSetting):
    ctx = MagicMock()
    ctx.fastmcp = MagicMock()
    ctx.fastmcp.biggo_setting = setting

    search = price_history_graph(
        ctx=ctx,
        history_id="tw_pmall_rakuten-nwdsl_6MONJRBOO",
    )

    assert isinstance(search, str)
