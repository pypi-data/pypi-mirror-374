# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.data import job_retrieve_status_params
from ..._base_client import make_request_options
from ...types.data.job_retrieve_status_response import JobRetrieveStatusResponse

__all__ = ["JobResource", "AsyncJobResource"]


class JobResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> JobResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#accessing-raw-response-data-eg-headers
        """
        return JobResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> JobResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#with_streaming_response
        """
        return JobResourceWithStreamingResponse(self)

    def retrieve_status(
        self,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JobRetrieveStatusResponse:
        """
        return the job status for a specific job.

            This endpoint:
            - Validates authentication tokens
            - Retrieves job status and metadata from the queue

            **Authentication**: Requires valid JWT token in Authorization header

        Args:
          job_id: Unique identifier for the job

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/data/job/status",
            body=maybe_transform({"job_id": job_id}, job_retrieve_status_params.JobRetrieveStatusParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobRetrieveStatusResponse,
        )


class AsyncJobResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncJobResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncJobResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncJobResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ElicitLabs/modal-python-sdk#with_streaming_response
        """
        return AsyncJobResourceWithStreamingResponse(self)

    async def retrieve_status(
        self,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JobRetrieveStatusResponse:
        """
        return the job status for a specific job.

            This endpoint:
            - Validates authentication tokens
            - Retrieves job status and metadata from the queue

            **Authentication**: Requires valid JWT token in Authorization header

        Args:
          job_id: Unique identifier for the job

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/data/job/status",
            body=await async_maybe_transform({"job_id": job_id}, job_retrieve_status_params.JobRetrieveStatusParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobRetrieveStatusResponse,
        )


class JobResourceWithRawResponse:
    def __init__(self, job: JobResource) -> None:
        self._job = job

        self.retrieve_status = to_raw_response_wrapper(
            job.retrieve_status,
        )


class AsyncJobResourceWithRawResponse:
    def __init__(self, job: AsyncJobResource) -> None:
        self._job = job

        self.retrieve_status = async_to_raw_response_wrapper(
            job.retrieve_status,
        )


class JobResourceWithStreamingResponse:
    def __init__(self, job: JobResource) -> None:
        self._job = job

        self.retrieve_status = to_streamed_response_wrapper(
            job.retrieve_status,
        )


class AsyncJobResourceWithStreamingResponse:
    def __init__(self, job: AsyncJobResource) -> None:
        self._job = job

        self.retrieve_status = async_to_streamed_response_wrapper(
            job.retrieve_status,
        )
