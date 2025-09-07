# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional

import httpx

from ..types import machine_learn_params, machine_query_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, SequenceNotStr
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
from ..types.machine_learn_response import MachineLearnResponse
from ..types.machine_query_response import MachineQueryResponse

__all__ = ["MachineResource", "AsyncMachineResource"]


class MachineResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MachineResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#accessing-raw-response-data-eg-headers
        """
        return MachineResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MachineResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#with_streaming_response
        """
        return MachineResourceWithStreamingResponse(self)

    def learn(
        self,
        *,
        message: Union[Iterable[Dict[str, object]], Dict[str, object], str],
        user_id: str,
        datetime_input: Optional[str] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        speaker: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MachineLearnResponse:
        """
        Process user messages to extract and store episodic memories, preferences, and
        identity attributes.

            This endpoint:
            - Validates authentication tokens
            - Processes conversation messages for memory extraction
            - Queues learning jobs for asynchronous processing (default)
            - Maintains conversation state and session continuity

            **Authentication**: Requires valid JWT token in Authorization header

        Args:
          message: Message content to learn from

          user_id: Unique identifier for the user

          datetime_input: ISO format datetime string for the message timestamp

          session_id: Optional session identifier for conversation context

          speaker: Speaker of the message

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/machine/learn",
            body=maybe_transform(
                {
                    "message": message,
                    "user_id": user_id,
                    "datetime_input": datetime_input,
                    "session_id": session_id,
                    "speaker": speaker,
                },
                machine_learn_params.MachineLearnParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MachineLearnResponse,
        )

    def query(
        self,
        *,
        question: str,
        user_id: str,
        filter_memory_types: Optional[SequenceNotStr[str]] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MachineQueryResponse:
        """
        Query user's stored memories, preferences, and identity attributes based on a
        natural language question.

            This endpoint:
            - Validates authentication tokens
            - Retrieves relevant memories using semantic search
            - Returns structured memory data from all memory types
            - Supports optional session context for conversation continuity
            - Supports filtering specific memory types for performance optimization

            **Authentication**: Requires valid JWT token in Authorization header

            **Memory Types**:
            - `episodic`: Past experiences and events
            - `preference`: User preferences and choices
            - `identity`: Personal attributes and characteristics
            - `short_term`: Current session context and recent conversation

            **Filtering**: Use `filter_memory_types` to exclude specific memory types from retrieval

        Args:
          question: The question to query against user's memories

          user_id: Unique identifier for the user

          filter_memory_types:
              Optional list of memory types to exclude from retrieval. Valid types:
              'episodic', 'preference', 'identity', 'short_term'

          session_id: Optional session identifier for conversation context

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/machine/query",
            body=maybe_transform(
                {
                    "question": question,
                    "user_id": user_id,
                    "filter_memory_types": filter_memory_types,
                    "session_id": session_id,
                },
                machine_query_params.MachineQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MachineQueryResponse,
        )


class AsyncMachineResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMachineResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMachineResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMachineResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#with_streaming_response
        """
        return AsyncMachineResourceWithStreamingResponse(self)

    async def learn(
        self,
        *,
        message: Union[Iterable[Dict[str, object]], Dict[str, object], str],
        user_id: str,
        datetime_input: Optional[str] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        speaker: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MachineLearnResponse:
        """
        Process user messages to extract and store episodic memories, preferences, and
        identity attributes.

            This endpoint:
            - Validates authentication tokens
            - Processes conversation messages for memory extraction
            - Queues learning jobs for asynchronous processing (default)
            - Maintains conversation state and session continuity

            **Authentication**: Requires valid JWT token in Authorization header

        Args:
          message: Message content to learn from

          user_id: Unique identifier for the user

          datetime_input: ISO format datetime string for the message timestamp

          session_id: Optional session identifier for conversation context

          speaker: Speaker of the message

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/machine/learn",
            body=await async_maybe_transform(
                {
                    "message": message,
                    "user_id": user_id,
                    "datetime_input": datetime_input,
                    "session_id": session_id,
                    "speaker": speaker,
                },
                machine_learn_params.MachineLearnParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MachineLearnResponse,
        )

    async def query(
        self,
        *,
        question: str,
        user_id: str,
        filter_memory_types: Optional[SequenceNotStr[str]] | NotGiven = NOT_GIVEN,
        session_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MachineQueryResponse:
        """
        Query user's stored memories, preferences, and identity attributes based on a
        natural language question.

            This endpoint:
            - Validates authentication tokens
            - Retrieves relevant memories using semantic search
            - Returns structured memory data from all memory types
            - Supports optional session context for conversation continuity
            - Supports filtering specific memory types for performance optimization

            **Authentication**: Requires valid JWT token in Authorization header

            **Memory Types**:
            - `episodic`: Past experiences and events
            - `preference`: User preferences and choices
            - `identity`: Personal attributes and characteristics
            - `short_term`: Current session context and recent conversation

            **Filtering**: Use `filter_memory_types` to exclude specific memory types from retrieval

        Args:
          question: The question to query against user's memories

          user_id: Unique identifier for the user

          filter_memory_types:
              Optional list of memory types to exclude from retrieval. Valid types:
              'episodic', 'preference', 'identity', 'short_term'

          session_id: Optional session identifier for conversation context

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/machine/query",
            body=await async_maybe_transform(
                {
                    "question": question,
                    "user_id": user_id,
                    "filter_memory_types": filter_memory_types,
                    "session_id": session_id,
                },
                machine_query_params.MachineQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MachineQueryResponse,
        )


class MachineResourceWithRawResponse:
    def __init__(self, machine: MachineResource) -> None:
        self._machine = machine

        self.learn = to_raw_response_wrapper(
            machine.learn,
        )
        self.query = to_raw_response_wrapper(
            machine.query,
        )


class AsyncMachineResourceWithRawResponse:
    def __init__(self, machine: AsyncMachineResource) -> None:
        self._machine = machine

        self.learn = async_to_raw_response_wrapper(
            machine.learn,
        )
        self.query = async_to_raw_response_wrapper(
            machine.query,
        )


class MachineResourceWithStreamingResponse:
    def __init__(self, machine: MachineResource) -> None:
        self._machine = machine

        self.learn = to_streamed_response_wrapper(
            machine.learn,
        )
        self.query = to_streamed_response_wrapper(
            machine.query,
        )


class AsyncMachineResourceWithStreamingResponse:
    def __init__(self, machine: AsyncMachineResource) -> None:
        self._machine = machine

        self.learn = async_to_streamed_response_wrapper(
            machine.learn,
        )
        self.query = async_to_streamed_response_wrapper(
            machine.query,
        )
