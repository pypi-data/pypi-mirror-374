from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, List, Literal, Optional, TypeVar, overload
from maleo.types.base.dict import OptionalStringToAnyDict


class AggregateField(StrEnum):
    KEY = "key"
    URL = "slug"


class ResourceIdentifier(BaseModel):
    key: str = Field(..., description="Key", min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(..., description="Name", min_length=1)
    slug: str = Field(
        ..., description="URL Slug", min_length=1, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )


class Resource(BaseModel):
    identifiers: List[ResourceIdentifier] = Field(
        ..., min_length=1, description="Identifiers"
    )
    details: OptionalStringToAnyDict = Field(None, description="Details")

    @overload
    def aggregate(
        self, field: Literal[AggregateField.KEY], *, sep: str = ":"
    ) -> str: ...
    @overload
    def aggregate(
        self, field: Literal[AggregateField.URL], *, sep: str = "/"
    ) -> str: ...
    def aggregate(
        self, field: AggregateField = AggregateField.KEY, *, sep: str = ":"
    ) -> str:
        if field is AggregateField.KEY:
            return sep.join([id.key for id in self.identifiers])
        elif field is AggregateField.URL:
            return sep.join([id.slug for id in self.identifiers])


ResourceT = TypeVar("ResourceT", bound=Optional[Resource])


class ResourceMixin(BaseModel, Generic[ResourceT]):
    resource: ResourceT = Field(..., description="Resource")
