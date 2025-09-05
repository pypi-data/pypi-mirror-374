from pydantic import BaseModel, Field

"""
Example:

{
"biggo": [
    {
    "id": "tw_pec_momoshop",
    "region": "tw"
    }
],
"honey": []
}
"""


class NindexFromUrlItem(BaseModel):
    id: str
    region: str


class NindexFromUrlAPIRet(BaseModel):
    biggo: list[NindexFromUrlItem] = Field(default_factory=list)

    @property
    def nindex(self) -> str | None:
        if len(self.biggo) == 0:
            return

        return self.biggo[0].id
