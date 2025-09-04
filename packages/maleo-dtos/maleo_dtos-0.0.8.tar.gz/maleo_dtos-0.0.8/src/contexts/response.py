import traceback
from base64 import b64decode, b64encode
from io import BytesIO
from fastapi.responses import Response, StreamingResponse
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

    @classmethod
    async def async_from_response(
        cls, response: Response
    ) -> Tuple["ResponseContext", Response]:
        """
        Extract ResponseContext from a Response, handling streaming responses properly.
        Returns a tuple of (context, new_response) where new_response can be used normally.
        """
        response_body = b""

        if hasattr(response, "body_iterator"):
            # StreamingResponse case - we need to consume the iterator
            body_buffer = BytesIO()

            try:
                async for chunk in response.body_iterator:  # type: ignore
                    # Handle different chunk types
                    if isinstance(chunk, str):
                        body_buffer.write(chunk.encode("utf-8"))
                    elif isinstance(chunk, (bytes, memoryview)):
                        body_buffer.write(bytes(chunk))  # Convert memoryview to bytes
                    else:
                        # Fallback for unexpected types
                        body_buffer.write(str(chunk).encode("utf-8"))

                response_body = body_buffer.getvalue()

                # Create new StreamingResponse with the collected body
                new_response = StreamingResponse(
                    iter([response_body]),  # Single chunk iterator
                    status_code=response.status_code,
                    headers=dict(response.headers),  # Copy headers
                    media_type=response.media_type,  # Use media_type, not header lookup
                )

            except Exception as e:
                print(f"Error consuming body iterator: {e}")
                print(traceback.format_exc())
                # Create empty response as fallback
                new_response = Response(
                    content=b"",
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

        else:
            # Regular Response case - body should be directly accessible
            try:
                response_body = getattr(response, "body", b"")
            except Exception as e:
                print(f"Failed retrieving response body: {e}")
                print(traceback.format_exc())
                response_body = b""

            # No need to create a new response for non-streaming
            new_response = response

        # Create the context
        response_context = cls(
            status_code=response.status_code,
            media_type=response.media_type,
            headers=list(response.headers.items()) if response.headers else None,
            body=response_body,
        )

        return response_context, new_response

    @classmethod
    def sync_from_response(
        cls, response: Response
    ) -> Tuple["ResponseContext", Response]:
        """
        Synchronous version - only works with non-streaming responses.
        Use from_response() for StreamingResponse support.
        """
        if hasattr(response, "body_iterator"):
            raise ValueError(
                "Cannot process StreamingResponse synchronously. "
                "Use 'await from_response()' instead."
            )

        try:
            response_body = getattr(response, "body", b"")
        except Exception as e:
            print(f"Failed retrieving response body: {e}")
            response_body = b""

        response_context = cls(
            status_code=response.status_code,
            media_type=response.media_type,
            headers=list(response.headers.items()) if response.headers else None,
            body=response_body,
        )

        return response_context, response


ResponseContextT = TypeVar("ResponseContextT", bound=Optional[ResponseContext])


class ResponseContextMixin(BaseModel, Generic[ResponseContextT]):
    response_context: ResponseContextT = Field(..., description="Response's context")
