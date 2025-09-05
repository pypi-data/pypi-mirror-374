from pydantic import BaseModel, Field


class ShortLinkRet(BaseModel):
    results: dict[str, str] = Field(default_factory=dict)
