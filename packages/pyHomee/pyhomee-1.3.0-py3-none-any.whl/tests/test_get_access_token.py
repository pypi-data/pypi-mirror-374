"""Test connection handling of the Homee class."""

from unittest.mock import patch
import aiohttp.client_exceptions
import pytest

import aiohttp
import asyncio
from datetime import datetime
from freezegun import freeze_time

from aioresponses import aioresponses
from pyHomee import Homee, HomeeAuthFailedException, HomeeConnectionFailedException

from .conftest import HOMEE_IP, TEST_TOKEN, TEST_EXPIRATION

pytest_plugins = ("pytest_asyncio",)


@freeze_time("2025-07-17 12:00:00")
async def test_success(test_homee: Homee) -> None:
    """Test that get_access_token retrieves a token."""
    with aioresponses() as mocked_request:
        mocked_request.post(
            f"http://{HOMEE_IP}:7681/access_token",
            status=200,
            body=f"access_token={TEST_TOKEN}&user_id=2&device_id=10&expires={TEST_EXPIRATION}",
        )
        await test_homee.get_access_token()

    assert test_homee.token == TEST_TOKEN
    assert test_homee.expires == datetime.now().timestamp() + TEST_EXPIRATION


async def test_unauthorized(test_homee: Homee) -> None:
    """Test that get_access_token raises an error on failure."""
    with aioresponses() as mocked_request:
        mocked_request.post(
            f"http://{HOMEE_IP}:7681/access_token",
            status=401,
            body="Unauthorized",
        )
        with pytest.raises(
            HomeeAuthFailedException,
            match="Auth request was unsuccessful. Status: 401 - Unauthorized",
        ):
            await test_homee.get_access_token()

async def test_parsing_failed(test_homee: Homee) -> None:
    """Test that get_access_token raises an error on parsing failure."""
    with aioresponses() as mocked_request:
        mocked_request.post(
            f"http://{HOMEE_IP}:7681/access_token",
            status=200,
            body="invalid_response_format",
        )
        with pytest.raises(
            HomeeAuthFailedException,
            match="Invalid token format:",
        ):
            await test_homee.get_access_token()


@pytest.mark.parametrize(
    ("error", "exception", "message"),
    [
        (
            asyncio.TimeoutError,
            HomeeConnectionFailedException,
            "Connection to Homee timed out",
        ),
        (
            aiohttp.client_exceptions.ClientError,
            HomeeConnectionFailedException,
            "Could not connect to Homee",
        ),
    ],
)
async def test_connection_errors(
    test_homee: Homee,
    error: BaseException,
    exception: HomeeConnectionFailedException,
    message: str,
) -> None:
    """Test that get_access_token raises an error on connection issues."""
    with patch("aiohttp.ClientSession.post") as mocked_session, \
            patch("aiohttp.ClientSession.close") as mocked_close:
        mocked_session.side_effect = error
        with pytest.raises(
            exception,
            match=message,
        ):
            await test_homee.get_access_token()

    mocked_close.assert_called_once()
