# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from elicit import Modal, AsyncModal
from tests.utils import assert_matches_type
from elicit.types import UserCreateOrGetResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_or_get(self, client: Modal) -> None:
        user = client.users.create_or_get(
            email="user@example.com",
            name="John Doe",
        )
        assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_or_get_with_all_params(self, client: Modal) -> None:
        user = client.users.create_or_get(
            email="user@example.com",
            name="John Doe",
            org_user_id="org_123456",
        )
        assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_or_get(self, client: Modal) -> None:
        response = client.users.with_raw_response.create_or_get(
            email="user@example.com",
            name="John Doe",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_or_get(self, client: Modal) -> None:
        with client.users.with_streaming_response.create_or_get(
            email="user@example.com",
            name="John Doe",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_or_get(self, async_client: AsyncModal) -> None:
        user = await async_client.users.create_or_get(
            email="user@example.com",
            name="John Doe",
        )
        assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_or_get_with_all_params(self, async_client: AsyncModal) -> None:
        user = await async_client.users.create_or_get(
            email="user@example.com",
            name="John Doe",
            org_user_id="org_123456",
        )
        assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_or_get(self, async_client: AsyncModal) -> None:
        response = await async_client.users.with_raw_response.create_or_get(
            email="user@example.com",
            name="John Doe",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_or_get(self, async_client: AsyncModal) -> None:
        async with async_client.users.with_streaming_response.create_or_get(
            email="user@example.com",
            name="John Doe",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserCreateOrGetResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True
