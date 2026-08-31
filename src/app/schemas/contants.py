from typing import TypedDict, Generic, TypeVar

T = TypeVar("T")


class ResponseDict(TypedDict, Generic[T]):
    data: T
    message: str


class ErrorResponseDict(TypedDict):
    detail: dict[str, str]
