from aiohttp import ClientSession

from biggo_mcp_server.lib.utils import generate_short_url
from ..types.api_ret.product_search import ProductSearchAPIRet
from ..types.setting import BigGoMCPSetting
from logging import getLogger

logger = getLogger(__name__)


class ProductSearchService:
    def __init__(self, setting: BigGoMCPSetting):
        self._setting = setting

    async def search(self, query: str) -> ProductSearchAPIRet:
        url = f"https://api.biggo.com/api/v1/spa/search/{query}/product"

        headers = {
            "Content-Type": "application/json",
            "site": self._setting.domain.value,
            "region": self._setting.region.value.lower(),
        }
        logger.debug("product search, url: %s, headers: %s", url, headers)

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status >= 400:
                    err_msg = f"product search api error: {await resp.text()}"
                    logger.error(err_msg)
                    raise ValueError(err_msg)

                data = ProductSearchAPIRet.model_validate(await resp.json())

        data.generate_r_link(self._setting.domain)

        if self._setting.short_url_endpoint is not None:
            all_urls = data.get_all_urls()
            url_map = await generate_short_url(
                list(all_urls), self._setting.short_url_endpoint
            )
            data.replace_urls(url_map)

        return data
