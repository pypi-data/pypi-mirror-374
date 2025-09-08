"""Library for interacting with the homee smart home/home automation platform."""

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime
import hashlib
import json
import logging
from urllib.parse import parse_qs
from typing import Any, Literal

import aiohttp
import aiohttp.client_exceptions
from aiohttp.helpers import BasicAuth
import websockets.asyncio.client
import websockets.exceptions

from .const import DeviceApp, DeviceOS, DeviceType, WarningCode
from .model import (
    HomeeDevice,
    HomeeGroup,
    HomeeNode,
    HomeeRelationship,
    HomeeSettings,
    HomeeUser,
    HomeeWarning,
)

_LOGGER = logging.getLogger(__name__)


class Homee:
    """Representation of a Homee system."""

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        device: str = "pymee",
        ping_interval: int = 30,
        reconnect_interval: int = 5,
        reconnect: bool = True,
        max_retries: int = 5,
    ) -> None:
        """Initialize the virtual Homee."""
        self.host: str = host
        self.user: str = user
        self.password: str = password

        self.device: str = device
        self.ping_interval: int = ping_interval
        self.should_reconnect: bool = reconnect
        self.reconnect_interval: int = reconnect_interval
        self.max_retries: int = max_retries

        self.device_id: str = str(device).lower().replace(" ", "-")

        self.devices: list[HomeeDevice] = []
        self.groups: list[HomeeGroup] = []
        self.nodes: list[HomeeNode] = []
        self.relationships: list[HomeeRelationship] = []
        self.settings: HomeeSettings
        self.users: list[HomeeUser] = []
        self.warning = HomeeWarning(
            {'code': 0, 'description': 'None', 'message': 'None', 'data': {}}
        )
        self.token: str = ""
        self.expires: float = 0
        self.connected: bool = False
        self.retries: int = 0
        self.should_close: bool = False

        self._message_queue: asyncio.Queue[str] = asyncio.Queue()
        self._connected_event = asyncio.Event()
        self._disconnected_event = asyncio.Event()
        self._connection_listeners: list[
            Callable[[bool], Coroutine[Any, Any, None]]
        ] = []
        self._nodes_listeners: list[
            Callable[[HomeeNode, bool], Coroutine[Any, Any, None]]
        ] = []

    async def get_access_token(self) -> str:
        """Try asynchronously to get an access token from homee using username and password."""

        # Check if current token is still valid
        if self.token is not None and self.expires > datetime.now().timestamp():
            return self.token

        auth = BasicAuth(
            self.user, hashlib.sha512(self.password.encode("utf-8")).hexdigest()
        )
        url = f"{self.url}/access_token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "device_name": self.device,
            "device_hardware_id": self.device_id,
            "device_os": DeviceOS.LINUX,
            "device_type": DeviceType.NONE,
            "device_app": DeviceApp.HOMEE,
        }

        try:
            async with aiohttp.ClientSession() as client:
                req = await client.post(
                    url,
                    auth=auth,
                    data=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5),
                )

                try:
                    req_text = await req.text()
                except (
                    aiohttp.client_exceptions.ClientError,
                    asyncio.TimeoutError,
                    UnicodeDecodeError,
                    LookupError,
                ) as e:
                    raise HomeeAuthFailedException(
                        f"Failed to decode response: {e}"
                    ) from e
        except asyncio.TimeoutError as e:
            raise HomeeConnectionFailedException("Connection to Homee timed out") from e
        except aiohttp.client_exceptions.ClientError as e:
            raise HomeeConnectionFailedException("Could not connect to Homee") from e

        if req.status == 200:
            try:
                parsed = parse_qs(req_text, strict_parsing=True)
                self.token = parsed["access_token"][0]
                expires = int(parsed["expires"][0])
                self.expires = datetime.now().timestamp() + expires
                self.retries = 0
            except (KeyError, IndexError, ValueError) as e:
                raise HomeeAuthFailedException(
                    f"Invalid token format: {req_text}"
                ) from e
        else:
            raise HomeeAuthFailedException(
                f"Auth request was unsuccessful. Status: {req.status} - {req.reason}"
            )

        return self.token

    async def run(self) -> None:
        """Connect to homee after acquiring an access token and runs until the connection is closed.

        Should be used in combination with asyncio.create_task.
        """

        self.should_close = False
        initial_connect = True

        # Reconnect loop to avoid recursive reconnects
        while initial_connect or (
            not self.should_close
            and self.should_reconnect
            and self.retries < self.max_retries
        ):
            initial_connect = False

            # Sleep after reconnect
            if self.retries > 0:
                await asyncio.sleep(self.reconnect_interval * self.retries)
                _LOGGER.debug(
                    "Attempting to reconnect in %s seconds",
                    self.reconnect_interval * self.retries,
                )

            try:
                await self.get_access_token()
            except HomeeConnectionFailedException as e:
                _LOGGER.debug("Could not connect to Homee: %s", e)
                # Reconnect
                self.retries += 1
                continue
            except HomeeAuthFailedException as e:
                _LOGGER.debug("Could not authenticate with Homee: %s", e)
                # Do not reconnect, since the authentication will not magically work.
                self.should_reconnect = False
                continue

            await self.open_ws()

        # Handle max retries
        if self.retries >= self.max_retries:
            await self.on_max_retries()

    def start(self) -> asyncio.Task:
        """Wrap run() with asyncio.create_task() and returns the resulting task."""
        return asyncio.create_task(self.run())

    async def open_ws(self) -> None:
        """Open the websocket connection assuming an access token was already received.

        Runs until connection is closed again.
        """

        _LOGGER.debug("Opening websocket")

        if self.retries > 0:
            await self.on_reconnect()

        try:
            async with websockets.asyncio.client.connect(
                uri=f"{self.ws_url}/connection?access_token={self.token}",
                subprotocols=[websockets.Subprotocol("v2")],
            ) as ws:
                await self._ws_on_open()

                while (not self.should_close) and self.connected:
                    try:
                        receive_task = asyncio.ensure_future(
                            self._ws_receive_handler(ws)
                        )
                        send_task = asyncio.ensure_future(self._ws_send_handler(ws))
                        done, pending = await asyncio.wait(
                            [receive_task, send_task],
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        exceptions: list[BaseException | None] = []

                        # Kill pending tasks
                        for task in pending:
                            task.cancel()

                        # Check if we finished with an exception
                        exceptions.extend(task.exception() for task in done)

                        if exceptions and exceptions[0] is not None:
                            raise exceptions[0]

                    except websockets.exceptions.ConnectionClosedError as e:
                        self.connected = False
                        await self.on_disconnected(e)
        except (
            websockets.exceptions.WebSocketException,
            ConnectionError,
            OSError,
        ) as e:
            await self._ws_on_error(e)

        self.retries += 1
        await self._ws_on_close()

    async def _ws_receive_handler(
        self, ws: websockets.asyncio.client.ClientConnection
    ) -> None:
        try:
            msg = await ws.recv(decode=True)
            await self._ws_on_message(msg)
        except websockets.exceptions.ConnectionClosedOK:
            return
        except websockets.exceptions.ConnectionClosedError as e:
            if not self.should_close:
                self.connected = False
                raise e

    async def _ws_send_handler(
        self, ws: websockets.asyncio.client.ClientConnection
    ) -> None:
        try:
            msg = await self._message_queue.get()
            if self.connected and not self.should_close:
                await ws.send(msg)
        except websockets.exceptions.ConnectionClosed as e:
            if not self.should_close:
                self.connected = False
                raise e

    async def _ws_on_open(self) -> None:
        """Websocket on_open callback."""

        _LOGGER.debug("Connection to websocket successful")

        self.connected = True

        await self.on_connected()
        await self.send("GET:all")

    async def _ws_on_message(self, msg: str) -> None:
        """Websocket on_message callback."""

        await self._handle_message(json.loads(msg))

    async def _ws_on_close(self) -> None:
        """Websocket on_close callback."""
        # if not self.should_close and self.retries <= 1:

        if self.connected:
            self.connected = False
            self._disconnected_event.set()

            await self.on_disconnected()

    async def _ws_on_error(self, error: Exception) -> None:
        """Websocket on_error callback."""

        await self.on_error(error)

    async def send(self, msg: str) -> None:
        """Send a raw string message to homee."""

        if not self.connected or self.should_close:
            return

        await self._message_queue.put(msg)

    async def reconnect(self) -> None:
        """Start a reconnection attempt."""

        await self.run()

    def disconnect(self) -> None:
        """Disconnect from homee by closing the websocket connection."""

        self.should_close = True

    def add_connection_listener(
        self, listener: Callable[[bool], Coroutine[Any, Any, None]]
    ) -> Callable[[], None]:
        """Add a listener for change in connected state."""
        self._connection_listeners.append(listener)

        def remove_listener() -> None:
            self._connection_listeners.remove(listener)

        return remove_listener

    def add_nodes_listener(
        self, listener: Callable[[HomeeNode, bool], Coroutine[Any, Any, None]]
    ) -> Callable[[], None]:
        """Add a listener for node add/delete events."""
        self._nodes_listeners.append(listener)

        def remove_listener() -> None:
            self._nodes_listeners.remove(listener)

        return remove_listener

    async def _handle_message(self, msg: dict) -> None:
        """Handle incoming homee messages."""

        msg_type = None

        try:
            msg_type = list(msg)[0]
        except TypeError as e:
            _LOGGER.info("Invalid message: %s", msg)
            await self.on_error(e)
            return

        _LOGGER.debug(msg)

        if msg_type == "all":
            self.settings = HomeeSettings(msg["all"]["settings"])

            # Create / Update nodes
            if not self.nodes:
                # Since there might be lots of nodes, we don't want to check for
                # all in the next step, so if we start up, just add all nodes.
                self.nodes = [HomeeNode(node_data) for node_data in msg["all"]["nodes"]]
            else:
                for node_data in msg["all"]["nodes"]:
                    await self._update_or_create_node(node_data, self.warning.code)

            # Create / Update groups
            for group_data in msg["all"]["groups"]:
                self._update_or_create_group(group_data)

            # Create / Update users
            for user_data in msg["all"]["users"]:
                self._update_or_create_user(user_data)

            self._update_or_create_relationships(msg["all"]["relationships"])

            self._remap_relationships()
            self._connected_event.set()

        elif msg_type == "attribute":
            await self._handle_attribute_change(msg["attribute"])
        # Not sure, if devices can be sent alone or only with user, but just in case...
        elif msg_type == "device":
            self._update_or_create_device(msg["device"])
        elif msg_type == "devices":
            for data in msg["devices"]:
                self._update_or_create_device(data)
        elif msg_type == "group":
            self._update_or_create_group(msg["group"])
        elif msg_type == "groups":
            for data in msg["groups"]:
                self._update_or_create_group(data)
        elif msg_type == "node":
            if self.warning.code != WarningCode.CUBE_LEARN_MODE_STARTED:
                # In learn mode, incomlete nodes are sent.
                await self._update_or_create_node(msg["node"], self.warning.code)
        elif msg_type == "nodes":
            for data in msg["nodes"]:
                await self._update_or_create_node(data, self.warning.code)
        elif msg_type == "relationship":
            self._update_or_create_relationship(msg["relationship"])
        elif msg_type == "relationships":
            self._update_or_create_relationships(msg["relationships"])
            self._remap_relationships()
        elif msg_type == "user":
            self._update_or_create_user(msg["user"])
        elif msg_type == "users":
            for data in msg["users"]:
                self._update_or_create_user(data)
        elif msg_type == "warning":
            await self._update_warning(msg["warning"])
        else:
            _LOGGER.debug(
                "Unknown/Unsupported message type: %s.\nMessage: %s", msg_type, msg
            )

        await self.on_message(msg)

    async def _handle_attribute_change(self, attribute_data: dict) -> None:
        """Handle an attribute changed message."""

        _LOGGER.debug("Updating attribute %s", attribute_data["id"])

        attr_node_id = attribute_data["node_id"]
        node = self.get_node_by_id(attr_node_id)
        if node is not None:
            node.update_attribute(attribute_data)
            await self.on_attribute_updated(attribute_data, node)

    async def _update_or_create_node(
        self, node_data: dict, warning_code: WarningCode
    ) -> None:
        existing_node = self.get_node_by_id(node_data["id"])
        if (
            existing_node is not None
            and not node_data["attributes"]
            and warning_code == WarningCode.CUBE_REMOVE_MODE_STARTED
        ):
            # A node without attributes is deleted. checking for remove mode for security.
            _LOGGER.debug(
                "Node %s has no attributes and cube remove mode is active. Removing",
                existing_node.id,
            )
            self.nodes.remove(existing_node)
            self._remap_relationships()
            for listener in self._nodes_listeners:
                await listener(existing_node, False)
            return
        if existing_node is not None:
            existing_node.set_data(node_data)
        else:
            self.nodes.append(HomeeNode(node_data))
            self._remap_relationships()
            _LOGGER.debug("Notifying listener of new node %s", self.nodes[-1].id)
            for listener in self._nodes_listeners:
                await listener(self.nodes[-1], True)

    def _update_or_create_group(self, data: dict) -> None:
        group = self.get_group_by_id(data["id"])
        if group is not None:
            group.set_data(data)
        else:
            self.groups.append(HomeeGroup(data))
            self._remap_relationships()

    def _update_or_create_relationship(self, data: dict) -> None:
        relationship: HomeeRelationship | None = next(
            (r for r in self.relationships if r.id == data["id"]), None
        )

        if relationship is not None:
            relationship.set_data(data)
        else:
            self.relationships.append(HomeeRelationship(data))
        self._remap_relationships()

    def _update_or_create_relationships(self, data: dict) -> None:
        if len(self.relationships) <= 0:
            self.relationships = [
                HomeeRelationship(relationship_data) for relationship_data in data
            ]
        else:
            for relationship_data in data:
                self._update_or_create_relationship(relationship_data)

    def _remap_relationships(self) -> None:
        """Remap the relationships between nodes and groups defined by the relationships list."""

        # Clear existing relationships
        for n in self.nodes:
            n.groups.clear()
        for g in self.groups:
            g.nodes.clear()

        for r in self.relationships:
            node = self.get_node_by_id(r.node_id)
            group = self.get_group_by_id(r.group_id)

            if node is not None and group is not None:
                node.groups.append(group)
                group.nodes.append(node)

    def _update_or_create_user(self, data: dict) -> None:
        """Create a user or update if already exists."""
        user = self.get_user_by_id(data["id"])
        if user is not None:
            user.set_data(data)
        else:
            self.users.append(HomeeUser(data))

        # Create / Update the devices of the user
        for device in data["devices"]:
            self._update_or_create_device(device)

    def _update_or_create_device(self, data: dict) -> None:
        """Create a device or update if already exists."""
        device = self.get_device_by_id(data["id"])
        if device is not None:
            device.set_data(data)
        else:
            self.devices.append(HomeeDevice(data))

    async def _update_warning(self, data: dict) -> None:
        """Set the warning to the latest one received."""
        self.warning.set_data(data)
        await self.on_warning()

    def get_node_index(self, node_id: int) -> int:
        """Return the index of the node with the given id or -1 if none exists."""
        return next((i for i, node in enumerate(self.nodes) if node.id == node_id), -1)

    def get_node_by_id(self, node_id: int) -> HomeeNode | None:
        """Return the node with the given id or 'None' if none exists."""
        index = self.get_node_index(node_id)
        return self.nodes[index] if index != -1 else None

    def get_group_index(self, group_id: int) -> int:
        """Return the index of the group with the given id or -1 if none exists."""
        return next(
            (i for i, group in enumerate(self.groups) if group.id == group_id), -1
        )

    def get_group_by_id(self, group_id: int) -> HomeeGroup | None:
        """Return the group with the given id or 'None' if no group with the given id exists."""
        index = self.get_group_index(group_id)
        return self.groups[index] if index != -1 else None

    def get_user_by_id(self, user_id: int) -> HomeeUser | None:
        """Return the user with the given id or 'None' if no user with the given id exists."""
        index = next((i for i, user in enumerate(self.users) if user.id == user_id), -1)
        return self.users[index] if index != -1 else None

    def get_device_by_id(self, device_id: int) -> HomeeDevice | None:
        """Return the device with the given id or 'None' if no device with the given id exists."""
        index = next(
            (i for i, device in enumerate(self.devices) if device.id == device_id), -1
        )
        return self.devices[index] if index != -1 else None

    async def set_value(self, device_id: int, attribute_id: int, value: float) -> None:
        """Set the target value of an attribute of a device."""

        _LOGGER.debug(
            "Set value: Device: %s Attribute: %s To: %s", device_id, attribute_id, value
        )
        await self.send(
            f"PUT:/nodes/{device_id}/attributes/{attribute_id}?target_value={value}"
        )

    async def update_node(self, node_id: int) -> None:
        """Request current data for a node."""
        _LOGGER.debug("Request current data for node %s", node_id)
        await self.send(f"GET:/nodes/{node_id}/")

    async def update_attribute(self, node_id: int, attribute_id: int) -> None:
        """Request current data for an attribute."""
        _LOGGER.debug(
            "Request current data for attribute %s of device %s", attribute_id, node_id
        )
        await self.send(f"GET:/nodes/{node_id}/attributes/{attribute_id}")

    async def play_homeegram(self, homeegram_id: int) -> None:
        """Invoke a homeegram."""

        await self.send(f"PUT:homeegrams/{homeegram_id}?play=1")

    @property
    def url(self) -> str:
        """Local homee url."""

        return f"http://{self.host}:7681"

    @property
    def ws_url(self) -> str:
        """Local homee websocket url."""

        return f"ws://{self.host}:7681"

    async def wait_until_connected(self) -> Literal[True]:
        """Return a coroutine that runs until a connection has been established."""
        return await self._connected_event.wait()

    async def wait_until_disconnected(self) -> Literal[True]:
        """Return a coroutine that runs until the connection has been closed."""
        return await self._disconnected_event.wait()

    async def on_reconnect(self) -> None:
        """Execute right before a reconnection attempt is started."""
        _LOGGER.debug("Homee %s Reconnecting", self.device)

    async def on_max_retries(self) -> None:
        """Execute if the maximum amount of retries was reached."""
        _LOGGER.info(
            "Could not reconnect Homee %s after %s retries",
            self.device,
            self.max_retries,
        )

    async def on_connected(self) -> None:
        """Execute once the websocket connection has been established."""
        for listener in self._connection_listeners:
            await listener(True)
        if self.retries > 0:
            _LOGGER.debug(
                "Homee %s Reconnected after %s retries", self.device, self.retries
            )
            self.retries = 0

    async def on_disconnected(self, error: Exception | None = None) -> None:
        """Execute after the websocket connection has been closed."""
        if not self.should_close:
            for listener in self._connection_listeners:
                await listener(False)

            _LOGGER.info("Homee %s Disconnected. Error: %s", self.device, error)

    async def on_error(self, error: Exception | None = None) -> None:
        """Execute after an error has occurred."""
        _LOGGER.info("An error occurred: %s", error)

    async def on_message(self, msg: dict) -> None:
        """Execute when the websocket receives a message.

        The message is automatically parsed from json into a dictionary.
        """

    async def on_warning(self) -> None:
        """Execute when a warning message is received."""
        if self.warning.code == WarningCode.CUBE_LEARN_MODE_SUCCESSFUL:
            # we need to get all nodes again, since there is no way to get the newest only.
            await self.send("GET:/nodes/")

    async def on_attribute_updated(self, attribute_data: dict, node: HomeeNode) -> None:
        """Execute when an 'attribute' message was received and an attribute was updated.

        Contains the parsed json attribute data and the corresponding node instance.
        """


class HomeeException(Exception):
    """Base class for all errors thrown by this library."""

    def __init__(self, reason: str | None = None) -> None:
        self.reason = reason


class HomeeConnectionFailedException(HomeeException):
    """Raised if connection can not be established."""


class HomeeAuthFailedException(HomeeException):
    """Raised if no valid access token could be acquired."""
