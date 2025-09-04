# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from elicit import Modal, AsyncModal
from tests.utils import assert_matches_type
from elicit.types import DataIngestResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestData:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_ingest(self, client: Modal) -> None:
        data = client.data.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
        )
        assert_matches_type(DataIngestResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_ingest_with_all_params(self, client: Modal) -> None:
        data = client.data.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
            filename="filename",
            timestamp_override="2024-01-01T12:00:00Z",
        )
        assert_matches_type(DataIngestResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_ingest(self, client: Modal) -> None:
        response = client.data.with_raw_response.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data = response.parse()
        assert_matches_type(DataIngestResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_ingest(self, client: Modal) -> None:
        with client.data.with_streaming_response.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data = response.parse()
            assert_matches_type(DataIngestResponse, data, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncData:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_ingest(self, async_client: AsyncModal) -> None:
        data = await async_client.data.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
        )
        assert_matches_type(DataIngestResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_ingest_with_all_params(self, async_client: AsyncModal) -> None:
        data = await async_client.data.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
            filename="filename",
            timestamp_override="2024-01-01T12:00:00Z",
        )
        assert_matches_type(DataIngestResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_ingest(self, async_client: AsyncModal) -> None:
        response = await async_client.data.with_raw_response.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data = await response.parse()
        assert_matches_type(DataIngestResponse, data, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_ingest(self, async_client: AsyncModal) -> None:
        async with async_client.data.with_streaming_response.ingest(
            content_type="email",
            payload="From: john@example.com\nTo: jane@example.com\nSubject: Hello\n\nHello Jane!",
            user_id="abc-123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data = await response.parse()
            assert_matches_type(DataIngestResponse, data, path=["response"])

        assert cast(Any, response.is_closed) is True
