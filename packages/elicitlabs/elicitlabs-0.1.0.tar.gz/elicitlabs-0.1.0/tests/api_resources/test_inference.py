# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from elicit import Modal, AsyncModal
from tests.utils import assert_matches_type
from elicit.types import InferenceProcessResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInference:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_process(self, client: Modal) -> None:
        inference = client.inference.process(
            messages=[
                {
                    "content": "bar",
                    "role": "bar",
                }
            ],
            session_id="session_123",
            user_id="123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(InferenceProcessResponse, inference, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_process(self, client: Modal) -> None:
        response = client.inference.with_raw_response.process(
            messages=[
                {
                    "content": "bar",
                    "role": "bar",
                }
            ],
            session_id="session_123",
            user_id="123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        inference = response.parse()
        assert_matches_type(InferenceProcessResponse, inference, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_process(self, client: Modal) -> None:
        with client.inference.with_streaming_response.process(
            messages=[
                {
                    "content": "bar",
                    "role": "bar",
                }
            ],
            session_id="session_123",
            user_id="123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            inference = response.parse()
            assert_matches_type(InferenceProcessResponse, inference, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncInference:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_process(self, async_client: AsyncModal) -> None:
        inference = await async_client.inference.process(
            messages=[
                {
                    "content": "bar",
                    "role": "bar",
                }
            ],
            session_id="session_123",
            user_id="123e4567-e89b-12d3-a456-426614174000",
        )
        assert_matches_type(InferenceProcessResponse, inference, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_process(self, async_client: AsyncModal) -> None:
        response = await async_client.inference.with_raw_response.process(
            messages=[
                {
                    "content": "bar",
                    "role": "bar",
                }
            ],
            session_id="session_123",
            user_id="123e4567-e89b-12d3-a456-426614174000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        inference = await response.parse()
        assert_matches_type(InferenceProcessResponse, inference, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_process(self, async_client: AsyncModal) -> None:
        async with async_client.inference.with_streaming_response.process(
            messages=[
                {
                    "content": "bar",
                    "role": "bar",
                }
            ],
            session_id="session_123",
            user_id="123e4567-e89b-12d3-a456-426614174000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            inference = await response.parse()
            assert_matches_type(InferenceProcessResponse, inference, path=["response"])

        assert cast(Any, response.is_closed) is True
