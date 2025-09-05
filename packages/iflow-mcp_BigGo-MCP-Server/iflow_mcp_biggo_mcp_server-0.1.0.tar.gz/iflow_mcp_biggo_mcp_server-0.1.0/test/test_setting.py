from pydantic import ValidationError
import pytest
from biggo_mcp_server.types.setting import BigGoMCPSetting
from .helper import *


def test_setting_region_case_insensitive():
    env_key = "BIGGO_MCP_SERVER_REGION"

    # upper case
    with set_temp_env({env_key: "TW"}):
        BigGoMCPSetting()

    # lower case
    with set_temp_env({env_key: "tw"}):
        BigGoMCPSetting()

    # random stuff
    with set_temp_env({env_key: "not-a-region"}):
        with pytest.raises(ValidationError):
            BigGoMCPSetting()
