import asyncio
import sys
import argparse
from mcp import ClientSession
from mcp.client.sse import sse_client


if sys.version_info >= (3, 11):
    from asyncio import timeout
else:
    from async_timeout import timeout


async def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="http://localhost:9876/sse")
    args = parser.parse_args()

    async with timeout(1):
        client = sse_client(args.url)
        async with client as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                r = await session.list_tools()
                print(r)


def main():
    asyncio.run(run())
