#!/bin/bash

set -a
source ./.env.test
set +a

uv run BigGo-MCP-Server
