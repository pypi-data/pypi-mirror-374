from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field

from ..setting import Domains


class Multiple(BaseModel):
    min_price: float = 0
    max_price: float = 0
    model_id: str = ""
    title: str = ""
    current_price: float = 0


class Store(BaseModel):
    # image: str
    # link: str
    name: str = ""
    discount_info: str = ""
    # rate_desc: str | None = None
    # is_cashback: bool


class Shop(BaseModel):
    name: str = ""
    username: str = ""
    uid: str = ""
    location: str = ""
    # seller_credit: int | None = None


class ListItem(BaseModel):
    nindex: str = ""
    oid: str = ""
    # subscribe_id: Any
    history_id: str = ""
    item_id: str = ""
    # is_ad: bool
    # is_group: bool
    # is_offline: bool
    # is_notfound: bool
    # is_expired: bool
    # is_adult: bool
    # is_multiple_product: bool
    # is_subscribe: bool
    title: str = ""

    # purl: str | None = None
    affurl: str | None = ""
    url: str = ""

    image: str = ""
    # gallery_count: int
    # origin_image: str
    cata: List[Any] = Field(default_factory=list)
    symbol: str = ""
    currency: str = ""
    multiple: Multiple = Field(default_factory=Multiple)
    price: float = 0
    price_range_min: Any | None = None
    price_range_max: Any | None = None
    count_result_store: Any | None = None
    count_result_product: Any | None = None
    store: Store = Field(default_factory=Store)
    has_shop: bool | None = None
    shop: Shop = Field(default_factory=Shop)
    price_diff_real: float = 0
    product_nindex_price: List[Any] = Field(default_factory=list)
    # subscribe_tags: List
    # subscribe_time: Any


class BiggoCItem(BaseModel):
    key: str = ""
    value: str = ""
    time: int | None = None


class ProductSearchAPIRet(BaseModel):
    # result: bool
    # total: int
    # total_page: int
    # pure_total: int
    # ec_count: int
    # mall_count: int
    # bid_count: int
    # size: int
    # took: int
    # is_shop: bool
    # is_suggest_query: bool
    # is_ypa: bool
    # is_adsense: bool
    # q_suggest: str
    # arr_suggest: List[str]
    # offline_count: int
    # spam_count: int
    # promo: List
    # filter: Dict[str, Any]
    # top_ad_count: int
    # group: Any
    # recommend_group: List
    list: List[ListItem] = Field(default_factory=list)
    # biggo_c: List[BiggoCItem]
    low_price: float = 0
    high_price: float = 0

    def generate_r_link(self, domain: Domains):
        for product in self.list:
            product.url = f"https://{domain.value}{product.affurl}"
            product.affurl = None

    def get_all_urls(self) -> set[str]:
        product_urls = {product.url for product in self.list}
        image_urls = {product.image for product in self.list}
        return product_urls | image_urls

    def replace_urls(self, url_map: dict[str, str]):
        """Replace urls in the list with the new urls

        Args:
            url_map (dict[str, str]): The map of old urls to new urls
        """
        for product in self.list:
            if product.url in url_map:
                product.url = url_map[product.url]
            if product.image in url_map:
                product.image = url_map[product.image]
