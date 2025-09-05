from contextlib import contextmanager
import pytest
import sys
from os import environ
from pathlib import Path
from dotenv import load_dotenv
from biggo_mcp_server.types.setting import BigGoMCPSetting


def load_env_files():
    """載入環境變數，相容所有 Python 3.10+ 版本"""
    test_env_paths = [
        Path(__file__).parent / ".env.test",  # test/.env.test
        Path(__file__).parent.parent / ".env.test",  # .env.test
    ]

    for env_path in test_env_paths:
        if env_path.is_file():  # 使用 is_file() 而不是 exists()
            try:
                # Python 3.10+ 相容性處理
                env_path_str = (
                    str(env_path)
                    if sys.version_info >= (3, 11)
                    else env_path.absolute().as_posix()
                )
                load_dotenv(env_path_str)
                return True
            except Exception as e:
                print(f"Warning: Failed to load {env_path}: {e}", file=sys.stderr)
    return False


# 確保環境變數被載入
load_env_files()


@pytest.fixture
def setting():
    client_id = environ.get("BIGGO_MCP_SERVER_CLIENT_ID")
    client_secret = environ.get("BIGGO_MCP_SERVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "Environment variables BIGGO_MCP_SERVER_CLIENT_ID and BIGGO_MCP_SERVER_CLIENT_SECRET must be set. "
            "Please check if .env.test exists and contains the correct values."
        )

    setting = BigGoMCPSetting(
        client_id=client_id,
        client_secret=client_secret,
    )
    return setting


@contextmanager
def set_temp_env(env_dict: dict[str, str]):
    for k, v in env_dict.items():
        environ[k] = v
    yield
    for k, _ in env_dict.items():
        environ.pop(k)
