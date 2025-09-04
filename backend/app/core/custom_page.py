from dataclasses import dataclass
from typing import Any, Generic, Sequence, Type, TypeVar

from fastapi import Query
from pydantic import Field

from fastapi_pagination.bases import AbstractParams, BasePage, RawParams


@dataclass
class CustomParams(AbstractParams):
    current: int = Query(1, ge=1, description="Page number")
    pageSize: int = Query(20, ge=1, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.pageSize,
            offset=self.pageSize * (self.current - 1),
        )


T = TypeVar("T")
C = TypeVar("C", bound="Page[Any]")


class Page(BasePage[T], Generic[T]):
    items: Sequence[T] = Field(..., description="Items in the current page")
    total: int = Field(..., description="Total number of items")
    current: int = Field(..., description="Current index")
    pageSize: int = Field(..., description="Number of rows per page")

    __params_type__ = CustomParams

    @classmethod
    def create(
        cls: Type[C], items: Sequence[T], params: AbstractParams, **kwargs: Any
    ) -> C:
        assert isinstance(params, CustomParams)

        return cls(
            items=items,
            current=params.current,
            pageSize=params.pageSize,
            **kwargs,
        )
