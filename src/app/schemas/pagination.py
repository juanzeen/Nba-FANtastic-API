from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, gt=0, le=100)


class PaginationDetails(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginationResponse(BaseModel, Generic[T]):
    message: str
    data: list[T]
    pagination: PaginationDetails
