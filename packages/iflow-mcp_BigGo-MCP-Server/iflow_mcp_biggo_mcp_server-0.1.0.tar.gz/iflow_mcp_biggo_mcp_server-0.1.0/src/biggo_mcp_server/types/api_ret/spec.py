from typing import Any
from pydantic import BaseModel, Field, RootModel


class SpecIndexesAPIItem(BaseModel):
    index: str


class SpecIndexesAPIRet(RootModel[list[SpecIndexesAPIItem]]):
    root: list[SpecIndexesAPIItem] = Field(default_factory=list)


class SpecMappingAPIRet(RootModel[dict[str, dict[str, Any]]]):
    """
    Example:
    {
        "spec_grouping_bidet_toilet_seat": {
            "mappings": {
                "properties": {}
            }
        }
    }
    """

    root: dict[str, dict[str, Any]] = Field(default_factory=dict)


class SpecSearchAPIRet(RootModel[list[dict[str, Any]]]):
    root: list[dict[str, Any]]
