from logging import getLogger
import base64
from aiohttp import ClientSession
from ..types.api_ret.auth_token import AuthTokenRet
from async_lru import alru_cache

logger = getLogger(__name__)


@alru_cache(maxsize=1, ttl=60)
async def get_access_token(
    client_id: str,
    client_secret: str,
    ssl: bool = True,
    endpoint: str = "https://api.biggo.com/auth/v1/token",
) -> str:
    """Get access token with client credentials"""

    params = {
        "grant_type": "client_credentials",
    }
    credentials = f"{client_id}:{client_secret}".encode()
    authorization = base64.b64encode(credentials).decode()
    headers = {
        "Authorization": f"Basic {authorization}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with ClientSession() as session:
        async with session.post(
            url=endpoint,
            headers=headers,
            params=params,
            ssl=ssl,
        ) as resp:
            if resp.status >= 400:
                err_msg = f"get access token error, {await resp.text()}"
                logger.error(err_msg)
                raise ValueError(err_msg)

            data = await resp.json()
            return AuthTokenRet.model_validate(data).access_token
