"""Fixtures for pyHomee tests."""

from unittest.mock import patch
import pytest
import websockets
from websockets.exceptions import ConnectionClosedOK



from pyHomee import Homee


HOMEE_IP = "127.0.0.1"
HOMEE_USER = "homee_user"
HOMEE_PASSWORD = "homee_password"
HOMEE_DEVICE_ID = "testdevice"
RECONNECT_INTERVAL = 10
MAX_RETRIES = 100
TEST_TOKEN = "VwZ5S9I1nMFbuHcY41I6eoAa2yjHWsvVdvbZibq4cf7EP9hBjIgKHBaUjrV4vRjq"
TEST_EXPIRATION = 31536000


@pytest.fixture
def test_homee() -> Homee:
    """Return a Homee instance."""
    return Homee(
        host=HOMEE_IP,
        user=HOMEE_USER,
        password=HOMEE_PASSWORD,
        device=HOMEE_DEVICE_ID,
        reconnect_interval=RECONNECT_INTERVAL,
        max_retries=MAX_RETRIES,
    )


@pytest.fixture
async def mock_get_access_token():
    """Mock the get_access_token method of the Homee instance."""
    with patch (
        "pyHomee.Homee.get_access_token",
        return_value=TEST_TOKEN,
    ) as mock_method:
        yield mock_method


@pytest.fixture
async def websocket_server():
    """Fixture that runs a test WebSocket server in the background."""
    clients = []

    async def echo_handler(ws):
        clients.append(ws)
        try:
            async for message in ws:
                await ws.send(message)  # echo back
        except ConnectionClosedOK:
            pass

    server = await websockets.serve(echo_handler, "localhost", 8765, subprotocols=["v2"])
    yield server
    server.close()
    await server.wait_closed()
