import asyncio
from logging import getLogger
from .types.setting import BigGoMCPSetting
from .lib.server_setup import create_server

logger = getLogger(__name__)


async def start():
    logger.info("Starting BigGo MCP Server")

    setting = BigGoMCPSetting()
    server = await create_server(setting)
    await server.start()
    await server.wait_finish()


def main():
    asyncio.run(start())
