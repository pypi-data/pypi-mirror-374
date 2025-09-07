from base64 import b64decode, b64encode
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    ValidationInfo,
)
from typing import Generic, List, Optional, Tuple, TypeVar, Union
from maleo.types.base.string import OptionalString


class ResponseContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status_code: int = Field(..., description="Status code")
    media_type: OptionalString = Field(None, description="Media type (Optional)")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Response's headers"
    )
    body: Union[bytes, memoryview] = Field(..., description="Content (Optional)")

    @field_serializer("body")
    def serialize_body(self, body: Union[bytes, memoryview]) -> str:
        """Always base64 encode body for safe serialization."""
        return b64encode(bytes(body)).decode()

    @field_validator("body", mode="before")
    def deserialize_body(cls, v, info: ValidationInfo):
        """Deserialize base64 string back to bytes, or pass through existing bytes/memoryview."""
        if isinstance(v, (bytes, memoryview)):
            return v

        if isinstance(v, str):
            try:
                return b64decode(v)
            except Exception as e:
                raise ValueError(f"Invalid Base64 body string: {e}")

        raise ValueError(f"Unsupported body type: {type(v)}")


ResponseContextT = TypeVar("ResponseContextT", bound=Optional[ResponseContext])


class ResponseContextMixin(BaseModel, Generic[ResponseContextT]):
    response_context: ResponseContextT = Field(..., description="Response's context")
