import asyncio
from datetime import datetime
import logging
import pytest
import websockets

from .conftest import TEST_TOKEN, TEST_EXPIRATION


async def mock_ws_server(websocket):
    """Mock WebSocket server that sends a test message when `message_event` is set."""
    print("Handler started")


    async for message in websocket:
        with open("/workspaces/pyHomee/tests/fixtures/all.json", encoding="utf-8") as f:
            test_msg = f.read()

        await websocket.send(test_msg)


@pytest.mark.asyncio
async def test_homee_websocket_message_handling(
    test_homee, mock_get_access_token, caplog
):
    # Start mock server
    caplog.set_level(logging.DEBUG)
    server = await websockets.serve(
        mock_ws_server,
        "localhost",
        7681,
    )

    # Patch the WebSocket URL method to return our mock URI
    test_homee.token = TEST_TOKEN
    test_homee.expires = datetime.now().timestamp() + TEST_EXPIRATION
    test_homee.connected = False

    # Run Homee in background
    run_task = asyncio.create_task(test_homee.run())

    await test_homee.wait_until_connected()

    assert test_homee.connected

    # Cleanup
    test_homee.disconnect()
    await test_homee.wait_until_disconnected()
    run_task.cancel()
    server.close()
    await server.wait_closed()
