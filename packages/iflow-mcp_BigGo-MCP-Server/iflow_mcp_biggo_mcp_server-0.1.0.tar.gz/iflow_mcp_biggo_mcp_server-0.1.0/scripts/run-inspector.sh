#!/bin/bash

set -a
source ./.env.test
set +a

npx @modelcontextprotocol/inspector uv run BigGo-MCP-Server
