from dataclasses import dataclass
from logging import getLogger
import re
from typing import Any
from urllib.parse import quote_plus, urlparse, parse_qs
from httpx import URL
from mcp.server.fastmcp import Context

from ..lib.server import BigGoMCPServer
from ..types.setting import BigGoMCPSetting
from ..types.api_ret.ec_list import EcListAPIData, EcListAPIRet, EcListPattern
from ..types.api_ret.ninde_from_url import NindexFromUrlAPIRet
from aiohttp import ClientSession
from ..types.api_ret.short_link import ShortLinkRet

logger = getLogger(__name__)


def get_setting(ctx: Context) -> BigGoMCPSetting:
    server: BigGoMCPServer = ctx.fastmcp  # type: ignore
    return server.biggo_setting


@dataclass(slots=True)
class NindexOID:
    nindex: str
    oid: str


def get_nindex_oid(inpt: str) -> NindexOID:
    """
    Arguments:
    - inpt: structure <nindex>-<oid>
    """
    temp = inpt.split("-", maxsplit=1)
    return NindexOID(nindex=temp[0], oid=temp[1])


def get_query_variable(url: str, field: str) -> str | None:
    try:
        url_obj = urlparse(url)
        query_params = parse_qs(url_obj.query)
        return query_params.get(field, [None])[0]
    except Exception:
        return None


def get_url_match(url: str, regex: str) -> re.Match[str] | None:
    return re.search(regex, url)


@dataclass(slots=True)
class GetIdWithRegexpRet:
    match: re.Match[str] | None
    pid: str | None


def get_id_with_regexp(
    url: str, regex: str, template: str = "%1", config: EcListPattern | None = None
) -> GetIdWithRegexpRet:
    match = get_url_match(url, regex)
    pid = None

    if match:
        pid = match.group(1)

    # Replace template
    if template and match:
        pid = template.replace("%1", match.group(1))
        if "%2" in template and len(match.groups()) > 1:
            pid = template.replace("%2", match.group(2))
            if "%1" in pid:
                pid = pid.replace("%1", match.group(1))

    # Padding
    if (
        config
        and config.len
        and isinstance(pid, str)
        and "%p" in pid
        and config.len > len(pid)
    ):
        padding_length = config.len - (len(pid) - 2)
        padding = config.pad * padding_length
        pid = pid.replace("%p", padding)

    return GetIdWithRegexpRet(match=match, pid=pid)


def parse_url(url: str, nindex: str, config: EcListPattern) -> str | None:
    regex = config.match
    query = config.query
    template = config.template

    # init parameter
    match = []
    pid: str | None = ""

    # check regexp
    if regex:
        if not isinstance(regex, list):
            regex = [regex]
        if not isinstance(template, list):
            template = [template]

        tmp: list[GetIdWithRegexpRet] = []
        for idx, re_pattern in enumerate(regex):
            template_to_use = template[idx] if idx < len(template) else template[0]
            result = get_id_with_regexp(url, re_pattern, template_to_use, config)
            if result.pid:
                tmp.append(result)

        if len(tmp) > 0:
            if tmp[0].match:
                match = [
                    tmp[0].match.group(i) for i in range(len(tmp[0].match.groups()) + 1)
                ]
            pid = tmp[0].pid

    # check url search query
    if query:
        query_pid = get_query_variable(url, query)
        pid = query_pid if query_pid is not None else pid

    # custom rule
    if nindex == "tw_pmall_rakuten":
        if len(match) > 2 and match[1] and match[2]:
            return f"{match[1]}_{match[2].upper()}"

    if config.uppercase and pid:
        pid = pid.upper()

    if config.lowercase and pid:
        pid = pid.lower()

    return pid


def get_product_id(
    ec_list: dict[str, EcListPattern], nindex: str, url: str
) -> str | None:
    pid: Any = ""

    if nindex in ec_list:
        current = ec_list[nindex]
        pid = parse_url(url, nindex, current)

    if isinstance(pid, dict) and "pid" in pid:
        return pid["pid"]  # type: ignore
    elif isinstance(pid, str):
        return pid
    else:
        return ""


async def get_nindex_from_url(url: str) -> str | None:
    url = f"https://extension.biggo.com/api/store.php?method=domain_lookup&domain={quote_plus(url)}"
    logger.debug("get_nindex_from_url, url: %s", url)
    async with ClientSession() as session:
        async with session.get(url) as resp:
            return NindexFromUrlAPIRet.model_validate(await resp.json()).nindex


async def get_ec_list() -> EcListAPIData | None:
    url = "https://extension.biggo.com/api/eclist.php"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            data = EcListAPIRet.model_validate(await resp.json())
            return data.data


async def get_pid_from_url(nindex: str, url: str) -> str | None:
    ec_list = await get_ec_list()
    if not ec_list:
        logger.warning("ec list is empty")
        return

    region = nindex.split("_")[0]
    if region not in ec_list:
        logger.warning("region not in ec list. region: %s, nindex: %s", region, nindex)
        return

    return get_product_id(ec_list[region], nindex, url)


async def expand_url(url: str) -> str:
    async with ClientSession() as session:
        async with session.get(url, allow_redirects=True) as resp:
            return str(resp.url)


async def generate_short_url(urls: list[str], endpoint: str) -> dict[str, str]:
    async with ClientSession() as session:
        async with session.post(endpoint, json={"urls": urls}) as resp:
            data = ShortLinkRet.model_validate(await resp.json())

    url = URL(endpoint)
    result: dict[str, str] = {}
    for original_url, short_id in data.results.items():
        result[original_url] = f"{url.scheme}://{url.host}/{short_id}"
    return result
