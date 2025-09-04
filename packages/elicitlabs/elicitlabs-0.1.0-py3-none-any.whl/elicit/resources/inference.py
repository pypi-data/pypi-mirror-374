# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ..types import inference_process_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.inference_process_response import InferenceProcessResponse

__all__ = ["InferenceResource", "AsyncInferenceResource"]


class InferenceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InferenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#accessing-raw-response-data-eg-headers
        """
        return InferenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InferenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#with_streaming_response
        """
        return InferenceResourceWithStreamingResponse(self)

    def process(
        self,
        *,
        messages: Iterable[Dict[str, object]],
        session_id: str,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InferenceProcessResponse:
        """
        Process user messages through the UPL inference engine with
        memory/preference/identity integration.

            This endpoint:
            - Validates authentication tokens
            - Processes messages with memory/preference/identity injection
            - Maintains conversation state

            **Authentication**: Requires valid JWT token in Authorization header

        Args:
          messages: List of conversation messages to process

          session_id: Session identifier for conversation continuity

          user_id: Unique identifier for the user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/inference",
            body=maybe_transform(
                {
                    "messages": messages,
                    "session_id": session_id,
                    "user_id": user_id,
                },
                inference_process_params.InferenceProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceProcessResponse,
        )


class AsyncInferenceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInferenceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncInferenceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInferenceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#with_streaming_response
        """
        return AsyncInferenceResourceWithStreamingResponse(self)

    async def process(
        self,
        *,
        messages: Iterable[Dict[str, object]],
        session_id: str,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InferenceProcessResponse:
        """
        Process user messages through the UPL inference engine with
        memory/preference/identity integration.

            This endpoint:
            - Validates authentication tokens
            - Processes messages with memory/preference/identity injection
            - Maintains conversation state

            **Authentication**: Requires valid JWT token in Authorization header

        Args:
          messages: List of conversation messages to process

          session_id: Session identifier for conversation continuity

          user_id: Unique identifier for the user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/inference",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "session_id": session_id,
                    "user_id": user_id,
                },
                inference_process_params.InferenceProcessParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InferenceProcessResponse,
        )


class InferenceResourceWithRawResponse:
    def __init__(self, inference: InferenceResource) -> None:
        self._inference = inference

        self.process = to_raw_response_wrapper(
            inference.process,
        )


class AsyncInferenceResourceWithRawResponse:
    def __init__(self, inference: AsyncInferenceResource) -> None:
        self._inference = inference

        self.process = async_to_raw_response_wrapper(
            inference.process,
        )


class InferenceResourceWithStreamingResponse:
    def __init__(self, inference: InferenceResource) -> None:
        self._inference = inference

        self.process = to_streamed_response_wrapper(
            inference.process,
        )


class AsyncInferenceResourceWithStreamingResponse:
    def __init__(self, inference: AsyncInferenceResource) -> None:
        self._inference = inference

        self.process = async_to_streamed_response_wrapper(
            inference.process,
        )
