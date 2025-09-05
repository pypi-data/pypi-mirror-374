from biggo_mcp_server.types.api_ret.product_search import ListItem, ProductSearchAPIRet
from biggo_mcp_server.types.setting import Domains


def test_product_search_api_ret():
    data = ProductSearchAPIRet(
        list=[
            ListItem(
                oid="123",
                title="test",
                price=100,
                affurl="/r/some-link",
            )
        ]
    )

    assert data.list[0].url == ""
    data.generate_r_link(Domains.TW)

    assert data.list[0].url == "https://biggo.com.tw/r/some-link"
