from dataclasses import dataclass
from logging import getLogger
from typing import Any, Literal

from aiohttp import ClientSession

from ..lib.utils import (
    expand_url,
    generate_short_url,
    get_nindex_from_url,
    get_nindex_oid,
    get_pid_from_url,
)
from ..types.api_ret.price_history import PriceHistoryAPIRet
from ..types.setting import BigGoMCPSetting

logger = getLogger(__name__)

DAYS = Literal["90", "180", "365", "730"] | Any


@dataclass(slots=True)
class PriceHistoryRet:
    description: PriceHistoryAPIRet
    graph_link: str


class PriceHistoryService:
    def __init__(self, setting: BigGoMCPSetting):
        self._setting = setting

    def _get_history_id(self, nindex: str, pid: str) -> str:
        return f"{nindex}-{pid}"

    def graph_link(self, history_id: str) -> str:
        item_info = get_nindex_oid(history_id)
        return f"https://imbot.biggo.dev/chart?nindex={item_info.nindex}&oid={item_info.oid}&lang={self._setting.graph_language.value}"

    async def _get_price_history(
        self, history_id: str, days: int
    ) -> PriceHistoryAPIRet | None:
        url = "https://extension.biggo.com/api/product_price_history.php"
        body = {"item": [history_id], "days": days}

        logger.debug("call price history, body: %s", body)

        async with ClientSession() as session:
            async with session.post(url=url, json=body) as resp:
                if resp.status >= 400:
                    err_msg = f"price history api error: {await resp.text()}"
                    logger.error(err_msg)
                    raise ValueError(err_msg)

                if (data := await resp.json()).get("result") is False:
                    return None
                else:
                    return PriceHistoryAPIRet.model_validate(data)

    async def history_with_history_id(
        self,
        history_id: str,
        days: DAYS,
    ) -> PriceHistoryRet | None:
        description = await self._get_price_history(history_id, int(days))
        if description is None:
            return None
        else:
            url = self.graph_link(history_id)

            if self._setting.short_url_endpoint is not None:
                all_urls = description.get_all_urls()
                all_urls.add(url)
                url_map = await generate_short_url(
                    list(all_urls), self._setting.short_url_endpoint
                )
                description.replace_urls(url_map)
                url = url_map.get(url, url)

            return PriceHistoryRet(description=description, graph_link=url)

    async def history_with_url(self, url: str, days: DAYS) -> PriceHistoryRet | None:
        real_url = await expand_url(url)

        if (nindex := await get_nindex_from_url(real_url)) is None:
            logger.warning("nindex not found, url: %s", real_url)
            return

        if (pid := await get_pid_from_url(nindex=nindex, url=real_url)) is None:
            logger.warning(
                "product id not found, nindex: %s, url: %s", nindex, real_url
            )
            return

        history_id = self._get_history_id(nindex=nindex, pid=pid)
        resp = await self._get_price_history(history_id=history_id, days=int(days))

        if resp is None and nindex in ["tw_mall_shopeemall", "tw_bid_shopee"]:
            nindex = (
                "tw_mall_shopeemall"
                if nindex == "tw_bid_shopee"
                else "tw_mall_shopeemall"
            )
            history_id = self._get_history_id(nindex=nindex, pid=pid)
            resp = await self._get_price_history(
                history_id=history_id,
                days=int(days),
            )

        if resp is not None:
            graph_link = self.graph_link(history_id)

            # replace urls with short urls
            if self._setting.short_url_endpoint is not None:
                all_urls = resp.get_all_urls()
                all_urls.add(graph_link)
                url_map = await generate_short_url(
                    list(all_urls), self._setting.short_url_endpoint
                )
                resp.replace_urls(url_map)
                graph_link = url_map.get(graph_link, graph_link)

            return PriceHistoryRet(description=resp, graph_link=graph_link)
        else:
            return None
