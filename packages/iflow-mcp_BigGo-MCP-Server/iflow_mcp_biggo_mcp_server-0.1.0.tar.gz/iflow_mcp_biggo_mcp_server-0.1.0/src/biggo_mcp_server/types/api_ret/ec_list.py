from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from .common import BigGoAPIRet


class EcListPattern(BaseModel):
    ptn: str
    bg_mark: str
    match: str | list[str] = ""
    template: str | list[str] = "%1"
    query: str = ""
    uppercase: bool = False
    lowercase: bool = False
    len: int | None = None
    pad: Any = ""


EcListRegion = (
    Literal["tw", "thai", "jp", "hk", "id", "my", "ph", "sg", "us", "vn"] | str
)
EcListAPIData = dict[EcListRegion, dict[str, EcListPattern]]


class EcListAPIRet(BigGoAPIRet[EcListAPIData]):
    pass
