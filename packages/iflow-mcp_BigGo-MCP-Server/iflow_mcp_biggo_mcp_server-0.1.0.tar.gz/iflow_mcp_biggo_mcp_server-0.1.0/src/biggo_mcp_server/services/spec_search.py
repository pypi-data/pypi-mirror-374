from contextlib import asynccontextmanager
from dataclasses import dataclass
from logging import getLogger
from typing import Any

from elasticsearch8 import AsyncElasticsearch

from ..lib.access_token import get_access_token
from ..types.api_ret.spec import SpecIndexesAPIRet, SpecMappingAPIRet, SpecSearchAPIRet
from ..types.setting import BigGoMCPSetting

logger = getLogger(__name__)


@dataclass(slots=True)
class SpecMappingRet:
    mappings: dict[str, Any]
    example_document: dict[str, Any]


class SpecSearchService:
    def __init__(self, setting: BigGoMCPSetting):
        self._setting = setting

    @asynccontextmanager
    async def session(self):
        access_token = await self._get_access_token()
        self._es_conn = AsyncElasticsearch(
            hosts=self._setting.es_proxy_url,
            verify_certs=self._setting.es_verify_certs,
            bearer_auth=access_token,
        )
        try:
            yield
        finally:
            await self._es_conn.close()

    async def _get_access_token(self) -> str:
        if self._setting.client_id is None or self._setting.client_secret is None:
            err_msg = "Client ID or Client Secret is not set"
            logger.error(err_msg)
            raise ValueError(err_msg)

        return await get_access_token(
            client_id=self._setting.client_id,
            client_secret=self._setting.client_secret,
            endpoint=self._setting.auth_token_url,
            ssl=self._setting.auth_verify_certs,
        )

    async def spec_indexes(self) -> list[str]:
        resp = await self._es_conn.cat.indices(index="spec*", format="json", h="index")
        data = SpecIndexesAPIRet.model_validate(resp.body)
        return [item.index for item in data.root]

    async def spec_mapping(self, index: str) -> SpecMappingRet:
        resp = await self._es_conn.indices.get_mapping(index=index)
        data = SpecMappingAPIRet.model_validate(resp.body)
        mappings = data.root[index]["mappings"]

        resp = await self._es_conn.search(index=index, size=1)
        example_document = resp.body["hits"]["hits"][0]["_source"]

        return SpecMappingRet(mappings=mappings, example_document=example_document)

    async def search(self, index: str, query: dict[str, Any]) -> list[dict[str, Any]]:
        size = query.get("size", None)
        if size is None:
            query["size"] = 10
        elif size > 10:
            raise ValueError("Size must be less than or equal to 10")

        logger.debug("Actual search args, index: %s, query: %s", index, query)

        resp = await self._es_conn.search(index=index, body=query)
        data = SpecSearchAPIRet.model_validate(resp.body["hits"]["hits"])
        return data.root
