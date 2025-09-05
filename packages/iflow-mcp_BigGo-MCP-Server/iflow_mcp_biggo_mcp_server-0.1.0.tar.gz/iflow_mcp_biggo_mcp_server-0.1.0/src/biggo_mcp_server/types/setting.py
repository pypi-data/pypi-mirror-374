from enum import Enum
from typing import Any, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class GraphLanguage(str, Enum):
    TW = "tw"
    EN = "en"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Regions(str, Enum):
    ID = "ID"
    VN = "VN"
    TH = "TH"
    PH = "PH"
    MY = "MY"
    IN = "IN"
    US = "US"
    TW = "TW"
    HK = "HK"
    JP = "JP"
    SG = "SG"


class Domains(str, Enum):
    ID = "biggo.id"
    VN = "vn.biggo.com"
    TH = "biggo.co.th"
    PH = "ph.biggo.com"
    MY = "my.biggo.com"
    IN = "biggo.co.in"
    US = "biggo.com"
    TW = "biggo.com.tw"
    HK = "biggo.hk"
    JP = "biggo.jp"
    SG = "biggo.sg"


REGION_DOMAIN_MAP: dict[Regions, Domains] = {
    Regions.ID: Domains.ID,
    Regions.VN: Domains.VN,
    Regions.TH: Domains.TH,
    Regions.PH: Domains.PH,
    Regions.MY: Domains.MY,
    Regions.IN: Domains.IN,
    Regions.US: Domains.US,
    Regions.TW: Domains.TW,
    Regions.HK: Domains.HK,
    Regions.JP: Domains.JP,
    Regions.SG: Domains.SG,
}


class BigGoMCPSetting(BaseSettings):
    """
    BigGo MCP Server settings
    """

    model_config = SettingsConfigDict(env_prefix="BIGGO_MCP_SERVER_")

    region: Regions = Regions.TW

    client_id: str | None = None
    client_secret: str | None = None

    log_level: LogLevel = LogLevel.INFO

    es_proxy_url: str = "https://api.biggo.com/api/v1/mcp-es-proxy/"
    es_verify_certs: bool = True

    auth_token_url: str = "https://api.biggo.com/auth/v1/token"
    auth_verify_certs: bool = True

    sse_port: int = 9876

    server_type: Literal["stdio", "sse"] = "stdio"

    short_url_endpoint: str | None = None

    @field_validator("region", mode="before")
    @classmethod
    def _validate_region(cls, value: Any) -> Regions:
        # Make region case insensitive
        if isinstance(value, str):
            return Regions(value.upper())
        else:
            return value

    @property
    def domain(self) -> Domains:
        return REGION_DOMAIN_MAP[self.region]

    @property
    def graph_language(self) -> GraphLanguage:
        if self.region == Regions.TW:
            return GraphLanguage.TW
        else:
            return GraphLanguage.EN
