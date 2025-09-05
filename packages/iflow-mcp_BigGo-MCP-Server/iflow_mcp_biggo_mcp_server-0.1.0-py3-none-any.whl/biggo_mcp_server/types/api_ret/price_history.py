from __future__ import annotations


from pydantic import BaseModel, RootModel


class Days(BaseModel):
    days: int
    max_price: float
    min_price: float
    up_times: int
    down_times: int
    last_continue_times: int
    last_increase_status: bool


class Statistics(BaseModel):
    days730: Days | None = None
    days365: Days | None = None
    days180: Days | None = None
    days90: Days | None = None
    days30: Days | None = None
    days7: Days | None = None


class PriceHistoryAttributes(BaseModel):
    symbol: str
    currency: str
    nindex: str
    oid: str
    current_price: float
    # datetime_format: str
    # price_history: List[PriceHistoryItem]
    # purl: str | None = None
    url: str | None = None
    title: str
    nindex_name: str
    # icon: str
    statistics: Statistics
    state: str


class PriceHistoryAPIRet(RootModel[dict[str, PriceHistoryAttributes]]):
    root: dict[str, PriceHistoryAttributes]

    def get_all_urls(self) -> set[str]:
        return {item.url for item in self.root.values() if item.url is not None}

    def replace_urls(self, url_map: dict[str, str]):
        for item in self.root.values():
            if item.url is not None and item.url in url_map:
                item.url = url_map[item.url]
