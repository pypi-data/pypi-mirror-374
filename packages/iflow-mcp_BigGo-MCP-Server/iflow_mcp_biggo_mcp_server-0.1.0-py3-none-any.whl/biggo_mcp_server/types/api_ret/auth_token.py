from pydantic import BaseModel


class AuthTokenRet(BaseModel):
    access_token: str
