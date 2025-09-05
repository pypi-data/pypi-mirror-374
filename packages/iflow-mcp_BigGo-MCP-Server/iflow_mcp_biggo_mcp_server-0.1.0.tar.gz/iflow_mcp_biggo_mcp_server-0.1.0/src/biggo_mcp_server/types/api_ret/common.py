from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ErrorContext(BaseModel):
    code: int
    message: str


class BigGoAPIRet(BaseModel, Generic[T]):
    result: bool
    data: T | None = None
    error: ErrorContext | None = None
