# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from elicit import Modal, AsyncModal
from tests.utils import assert_matches_type
from elicit.types.data import JobRetrieveStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestJob:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_status(self, client: Modal) -> None:
        job = client.data.job.retrieve_status(
            job_id="456e7890-e89b-12d3-a456-426614174001",
        )
        assert_matches_type(JobRetrieveStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_status(self, client: Modal) -> None:
        response = client.data.job.with_raw_response.retrieve_status(
            job_id="456e7890-e89b-12d3-a456-426614174001",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(JobRetrieveStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_status(self, client: Modal) -> None:
        with client.data.job.with_streaming_response.retrieve_status(
            job_id="456e7890-e89b-12d3-a456-426614174001",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(JobRetrieveStatusResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncJob:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncModal) -> None:
        job = await async_client.data.job.retrieve_status(
            job_id="456e7890-e89b-12d3-a456-426614174001",
        )
        assert_matches_type(JobRetrieveStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncModal) -> None:
        response = await async_client.data.job.with_raw_response.retrieve_status(
            job_id="456e7890-e89b-12d3-a456-426614174001",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(JobRetrieveStatusResponse, job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncModal) -> None:
        async with async_client.data.job.with_streaming_response.retrieve_status(
            job_id="456e7890-e89b-12d3-a456-426614174001",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(JobRetrieveStatusResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True
