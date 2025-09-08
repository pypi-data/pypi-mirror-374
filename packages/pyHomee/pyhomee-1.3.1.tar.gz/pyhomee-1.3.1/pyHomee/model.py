"""Data model for Homees various data items."""

from enum import IntEnum

from collections.abc import Callable
from typing import Any, Self, Type
import logging
import re
from urllib.parse import unquote
from .const import (
    AttributeBasedOn,
    AttributeChangedBy,
    AttributeState,
    AttributeType,
    DeviceApp,
    DeviceOS,
    DeviceType,
    GroupCategory,
    NodeProfile,
    NodeProtocol,
    NodeState,
    UserRole,
    WarningCode,
)

_LOGGER = logging.getLogger(__name__)


def log_unknown_value(enum_type: Type[IntEnum], value: int) -> None:
    """Log a warning if a value does not exist in an enum."""
    _LOGGER.warning(
        (
            "Unknown %s %s. Please submit a bug report at "
            "https://github.com/Taraman17/pyHomee/issues"
        ),
        enum_type.__name__,
        value,
    )


class HomeeObject:
    """Base class for Homee objects."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize the object."""
        self._data = data
        self.on_changed_listeners: list[Callable] = []

    @property
    def raw_data(self) -> dict[str, Any]:
        """Return the raw dict of the object."""
        return self._data

    def set_data(self, data: dict[str, Any]) -> None:
        """Update data of the attribute."""
        self._data = data

        for listener in self.on_changed_listeners:
            listener(self)

    def add_on_changed_listener(
        self, listener: Callable[[Self], None]
    ) -> Callable[[], None]:
        """Add on_changed listener to node."""
        self.on_changed_listeners.append(listener)

        def remove_listener() -> None:
            self.on_changed_listeners.remove(listener)

        return remove_listener


class HomeeAttributeOptions:
    """Representation of attributes options."""

    def __init__(self, attribute_options: dict[str, Any]) -> None:
        """Initialize options."""
        self._data = attribute_options

    @property
    def can_observe(self) -> list[int]:
        """List (int) of attribute types that this attribute can observe."""
        if "can_observe" in self._data:
            return list(self._data["can_observe"])

        return []

    @property
    def observes(self) -> list[int]:
        """List (int) of attribute ids that this attribute observes."""
        if "observes" in self._data:
            return list(self._data["observes"])

        return []

    @property
    def observed_by(self) -> list[int]:
        """List (int) of attribute ids that observe this attribute."""
        if "observed_by" in self._data:
            return list(self._data["observed_by"])

        return []

    @property
    def automations(self) -> list[int]:
        """List (str) of automations for thie attribute."""
        if "automations" in self._data:
            return list(self._data["automations"])

        return []

    @property
    def history(self) -> dict[str, int | bool] | None:
        """History data for the attribute.

        {'day': int, 'week': int, 'month': int, 'stepped': bool}.
        """
        if "history" in self._data:
            return dict(self._data["history"])

        return None

    @property
    def reverse_control_ui(self) -> bool:
        """Do up/down controls work in opposite direction."""
        if "reverse_control_ui" in self._data:
            return bool(self._data["reverse_control_ui"])

        return False


class HomeeAttribute(HomeeObject):
    """Representation of a Homee attribute."""

    @property
    def id(self) -> int:
        """The unique id of the attribute."""
        return int(self._data["id"])

    @property
    def node_id(self) -> int:
        """The id of the node the attribute belongs to."""
        return int(self._data["node_id"])

    @property
    def instance(self) -> int:
        """If more than one attribute of same type is present, they are numbered starting at 1."""
        return int(self._data["instance"])

    @property
    def minimum(self) -> float:
        """The minimum possible value of the attribute."""
        return float(self._data["minimum"])

    @property
    def maximum(self) -> float:
        """The maximum possible value of the attribute."""
        return float(self._data["maximum"])

    @property
    def current_value(self) -> float:
        """The current value of the attribute."""
        return float(self._data["current_value"])

    @property
    def target_value(self) -> float:
        """The target value of the attribute.

        Only used to change the attribute value.
        In most cases you want to use current_value instead.
        """
        return float(self._data["target_value"])

    @property
    def last_value(self) -> float:
        """The last value of the attribute. In most cases you want to use current_value instead."""
        return float(self._data["last_value"])

    @property
    def unit(self) -> str:
        """The decoded unit of the attribute."""
        return unquote(self._data["unit"])

    @property
    def step_value(self) -> float:
        """The step value used for attributes with discret increments."""
        return float(self._data["step_value"])

    @property
    def editable(self) -> bool:
        """Wether the attribute is editable of read only."""
        return bool(self._data["editable"])

    @property
    def type(self) -> AttributeType:
        """The attribute type. Compare with const.AttributeType."""
        try:
            return AttributeType(self._data["type"])
        except ValueError:
            log_unknown_value(AttributeType, self._data["type"])

        return AttributeType.NONE

    @property
    def state(self) -> AttributeState:
        """The attribute state. Compare with const.AttributeState."""
        try:
            return AttributeState(self._data["state"])
        except ValueError:
            log_unknown_value(AttributeState, self._data["state"])

        return AttributeState.NONE

    @property
    def last_changed(self) -> int:
        """The last time the attribute was changed."""
        return int(self._data["last_changed"])

    @property
    def changed_by(self) -> AttributeChangedBy:
        """How the attribute was changed. Compare with const.AttributeChangedBy."""
        try:
            return AttributeChangedBy(self._data["changed_by"])
        except ValueError:
            log_unknown_value(AttributeChangedBy, self._data["changed_by"])

        return AttributeChangedBy.NONE

    @property
    def changed_by_id(self) -> int:
        """The id of the user/homeegram the attribute was changed by."""
        return int(self._data["changed_by_id"])

    @property
    def based_on(self) -> AttributeBasedOn:
        """TODO"""
        try:
            return AttributeBasedOn(self._data["based_on"])
        except ValueError:
            log_unknown_value(AttributeBasedOn, self._data["based_on"])

        return AttributeBasedOn.NONE

    @property
    def name(self) -> str:
        """The decoded name of the attribute."""
        return unquote(self._data["name"])

    @property
    def data(self) -> str:
        """The data string of the attribute. Note that the data may be uri encoded."""
        return unquote(self._data["data"])

    @property
    def options(self) -> HomeeAttributeOptions | None:
        """The options collection of the attribute. Optional, not on every attribute."""
        if "options" in self._data:
            return HomeeAttributeOptions(self._data["options"])

        return None

    @property
    def is_reversed(self) -> bool:
        """Check if movement direction is reversed."""
        if self.options is not None:
            return bool(self.options.reverse_control_ui)

        return False

    def get_value(self) -> float | str:
        """Get the current value or data of the attribute."""
        # If the unit of the attribute is 'text', it is stored in .data
        if self.unit == "text":
            return self.data

        return self.current_value


class HomeeNode(HomeeObject):
    """Representation of a node in Homee."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize a Homee node."""
        super().__init__(data)
        self.attributes: list[HomeeAttribute] = []
        for a in self.attributes_raw:
            new_attribute = HomeeAttribute(a)
            new_attribute.add_on_changed_listener(self._on_attribute_changed)
            self.attributes.append(new_attribute)
        self._attribute_map: dict[AttributeType, HomeeAttribute] = {}
        self.remap_attributes()
        self.groups: list[HomeeGroup] = []

    @property
    def id(self) -> int:
        """The unique id of the node."""
        return int(self._data["id"])

    @property
    def name(self) -> str:
        """The decoded primary name of the node."""
        return unquote(self._data["name"])

    @property
    def profile(self) -> NodeProfile:
        """The NodeProfile of this node."""
        try:
            return NodeProfile(self._data["profile"])
        except ValueError:
            log_unknown_value(NodeProfile, self._data["profile"])

        return NodeProfile.NONE

    @property
    def image(self) -> str:
        return unquote(self._data["image"])

    @property
    def favorite(self) -> int:
        return int(self._data["favorite"])

    @property
    def order(self) -> int:
        return int(self._data["order"])

    @property
    def protocol(self) -> NodeProtocol:
        """The network protocol of the node."""
        try:
            return NodeProtocol(self._data["protocol"])
        except ValueError:
            log_unknown_value(NodeProfile, self._data["protocol"])

        return NodeProtocol.NONE

    @property
    def routing(self) -> bool:
        return bool(self._data["routing"])

    @property
    def state(self) -> NodeState:
        """State of availability."""
        try:
            return NodeState(self._data["state"])
        except ValueError:
            log_unknown_value(NodeState, self._data["state"])

        return NodeState.NONE

    @property
    def state_changed(self) -> int:
        return int(self._data["state_changed"])

    @property
    def added(self) -> int:
        return int(self._data["added"])

    @property
    def history(self) -> int:
        return int(self._data["history"])

    @property
    def cube_type(self) -> int:
        """Type of the Homee cube the node is part of."""
        return int(self._data["cube_type"])

    @property
    def note(self) -> str:
        """Text Note describing the node."""
        return unquote(self._data["note"])

    @property
    def services(self) -> int:
        return int(self._data["services"])

    @property
    def phonetic_name(self) -> str:
        """Name of the node."""
        return unquote(self._data["phonetic_name"])

    @property
    def owner(self) -> int:
        return int(self._data["owner"])

    @property
    def security(self) -> int:
        return int(self._data["security"])

    @property
    def attribute_map(self) -> dict[AttributeType, HomeeAttribute] | None:
        """Dict containing all attributes with attributeType as key."""
        return self._attribute_map

    @property
    def attributes_raw(self) -> list[dict[str, Any]]:
        """Return raw dict all the node's attributes."""
        return list(self._data["attributes"])

    def set_data(self, data: dict[str, Any]) -> None:
        """Update data of the node."""
        super().set_data(data)
        self.update_attributes(self._data["attributes"])

    def get_attribute_index(self, attribute_id: int) -> int:
        """Find and return attribute for a given index.

        Returns -1 if not found."""
        return next(
            (i for i, a in enumerate(self.attributes) if a.id == attribute_id), -1
        )

    def get_attribute_by_type(
        self, attribute_type: int, instance: int = 0
    ) -> HomeeAttribute | None:
        """Find and return attribute by attributeType.

        If multiple attributes of the same type are present,
        the instance number can be used to select the correct one."""
        for a in self.attributes:
            if a.type == attribute_type and a.instance == instance:
                return a

        return None

    def get_attribute_by_id(self, attribute_id: int) -> HomeeAttribute | None:
        """Find and return attribute for a given id."""
        index = self.get_attribute_index(attribute_id)
        return self.attributes[index] if index != -1 else None

    def _on_attribute_changed(self, attribute: HomeeAttribute) -> None:
        for listener in self.on_changed_listeners:
            listener(self)

    def update_attribute(self, attribute_data: dict[str, Any]) -> None:
        """Update a single attribute of a node."""
        attribute = self.get_attribute_by_id(attribute_data["id"])
        if attribute is not None:
            attribute.set_data(attribute_data)

    def update_attributes(self, attributes: list[dict]) -> None:
        """Update the given attributes."""
        for attr in attributes:
            self.update_attribute(attr)

    def remap_attributes(self) -> None:
        """Remap the node's attributes."""
        self._attribute_map.clear()
        for a in self.attributes:
            self._attribute_map.update({a.type: a})


class HomeeGroup(HomeeObject):
    """Representation of a Homee group."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize a Homee group."""
        super().__init__(data)
        self.nodes: list[HomeeNode] = []

    @property
    def id(self) -> int:
        """Id of the group, unique in Homee."""
        return int(self._data["id"])

    @property
    def name(self) -> str:
        """Decoded user given name of the group."""
        return unquote(self._data["name"])

    @property
    def image(self) -> str:
        return unquote(self._data["image"])

    @property
    def order(self) -> int:
        return int(self._data["order"])

    @property
    def added(self) -> int:
        return int(self._data["added"])

    @property
    def state(self) -> int:
        return int(self._data["state"])

    @property
    def category(self) -> GroupCategory:
        try:
            return GroupCategory(self._data["category"])
        except ValueError:
            log_unknown_value(GroupCategory, self._data["category"])

        return GroupCategory.NONE

    @property
    def phonetic_name(self) -> str:
        return unquote(self._data["phonetic_name"])

    @property
    def note(self) -> str:
        """Note describing the group."""
        return unquote(self._data["note"])

    @property
    def services(self) -> int:
        return int(self._data["services"])

    @property
    def owner(self) -> int:
        return int(self._data["owner"])


class HomeeSettings(HomeeObject):
    """Representation of the settings object passed by Homee."""

    @property
    def address(self) -> str:
        """Street set by user."""
        return unquote(self._data["address"])

    @property
    def city(self) -> str:
        """City set by user."""
        return unquote(self._data["city"])

    @property
    def zip(self) -> str:
        """Zip code set by user."""
        return unquote(self._data["zip"])

    @property
    def state(self) -> str:
        """State set by user."""
        return unquote(self._data["state"])

    @property
    def latitude(self) -> float:
        """Latitude of set position of Homee."""
        return float(self._data["latitude"])

    @property
    def longitude(self) -> float:
        """Longitude of set position of Homee."""
        return float(self._data["longitude"])

    @property
    def country(self) -> str:
        """Country set by user."""
        return unquote(self._data["country"])

    @property
    def language(self) -> str:
        """Frontend language."""
        return unquote(self._data["language"])

    @property
    def remote_access(self) -> int:
        """Remote access enabled or not."""
        return int(self._data["remote_access"])

    @property
    def beta(self) -> bool:
        """Is user accepting beta releases of firmware."""
        return bool(self._data["beta"])

    @property
    def webhooks_key(self) -> str:
        """Key used for webhooks."""
        return str(self._data["webhooks_key"])

    @property
    def automatic_location_detection(self) -> bool:
        return bool(self._data["automatic_location_detection"])

    @property
    def polling_interval(self) -> float:
        """Standard polling interval set in Homee."""
        return float(self._data["polling_interval"])

    @property
    def timezone(self) -> str:
        """Timezone of Homee."""
        return unquote(self._data["timezone"])

    @property
    def enable_analytics(self) -> bool:
        """Send analytical data back home."""
        return bool(self._data["enable_analytics"])

    @property
    def homee_name(self) -> str:
        """Decoded name of Homee."""
        return unquote(self._data["homee_name"])

    @property
    def LastMissingCubeNotification(self) -> str:
        return unquote(self._data["LastMissingCubeNotification"])

    @property
    def local_ssl_enabled(self) -> bool:
        return bool(self._data["local_ssl_enabled"])

    @property
    def wlan_enabled(self) -> bool:
        return bool(self._data["wlan_enabled"])

    @property
    def wlan_ssid(self) -> str:
        return str(self._data["wlan_ssid"])

    @property
    def wlan_mode(self) -> int:
        return int(self._data["wlan_mode"])

    @property
    def mac_address(self) -> str:
        """Return MAC Address derived from HomeeID"""
        return ":".join(re.findall("..", self._data["uid"]))

    @property
    def internet_access(self) -> bool:
        return bool(self._data["internet_access"])

    @property
    def lan_enabled(self) -> bool:
        return bool(self._data["lan_enabled"])

    @property
    def lan_ip_address(self) -> str:
        return unquote(self._data["lan_ip_address"])

    @property
    def available_ssids(self) -> list[str]:
        return list(self._data["available_ssids"])

    @property
    def time(self) -> int:
        return int(self._data["time"])

    @property
    def civil_time(self) -> str:
        return str(self._data["civil_time"])

    @property
    def version(self) -> str:
        return str(self._data["version"])

    @property
    def uid(self) -> str:
        return str(self._data["uid"])

    @property
    def cubes(self) -> list[dict[str, Any]]:
        """List of cubes attached to this Homee."""
        return list(self._data["cubes"])

    @property
    def extensions(self) -> list[dict]:
        return list(self._data["extensions"])


class HomeeRelationship(HomeeObject):
    """Representation of a Homee relationship."""

    @property
    def id(self) -> int:
        """Id unique to this Homee."""
        return int(self._data["id"])

    @property
    def group_id(self) -> int:
        return int(self._data["group_id"])

    @property
    def node_id(self) -> int:
        return int(self._data["node_id"])

    @property
    def homeegram_id(self) -> int:
        return int(self._data["homeegram_id"])

    @property
    def order(self) -> int:
        return int(self._data["order"])

    def set_data(self, data: dict[str, Any]) -> None:
        """Update data of the relationship."""
        self._data = data
        for listener in self.on_changed_listeners:
            listener(self)

    def add_on_changed_listener(
        self, listener: Callable[[Self], None]
    ) -> Callable[[], None]:
        """Add on_changed listener to node."""
        self.on_changed_listeners.append(listener)

        def remove_listener() -> None:
            self.on_changed_listeners.remove(listener)

        return remove_listener


class HomeeWarningData:
    """Representation of the data part of a Homee warning."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize warning data."""
        self._data = data

    @property
    def protocol(self) -> NodeProtocol | None:
        """Return the protocol, the warning originates from."""
        if "protocol" in self._data:
            try:
                return NodeProtocol(self._data["protocol"])
            except ValueError:
                log_unknown_value(NodeProtocol, self._data["protocol"])

            return NodeProtocol.NONE

        return None

    @property
    def protocol_string(self) -> str:
        """Return the descriptive string for the protocol."""
        if "protocol" in self._data:
            try:
                return NodeProtocol(self._data["protocol"]).name
            except ValueError:
                log_unknown_value(NodeProtocol, self._data["protocol"])

            return NodeProtocol.NONE.name

        return ""

    @property
    def reason(self) -> str:
        """Return the reason for the warning."""
        if "reason" in self._data:
            return unquote(self._data["reason"])

        return ""


class HomeeWarning(HomeeObject):
    """Representation of a Homee warning message."""

    @property
    def code(self) -> WarningCode:
        """Return the numerical code of the warning."""
        try:
            return WarningCode(self._data["code"])
        except ValueError:
            log_unknown_value(WarningCode, self._data["code"])

        return WarningCode.NONE

    @property
    def code_string(self) -> str:
        """Return the descriptive string for the warning code."""
        try:
            return WarningCode(self._data["code"]).name
        except ValueError:
            log_unknown_value(WarningCode, self._data["code"])

        return WarningCode.NONE.name

    @property
    def description(self) -> str:
        """Return the text description of the warning."""
        return unquote(self._data["description"])

    @property
    def message(self) -> str:
        """Return the message of the warning."""
        return unquote(self._data["message"])

    @property
    def data(self) -> HomeeWarningData | None:
        """The data collection of the warning. Optional, not on every warning."""
        if "data" in self._data:
            return HomeeWarningData(self._data["data"])

        return None


class HomeeDevice(HomeeObject):
    """Represent a Homee device."""

    @property
    def id(self) -> int:
        """Return the unique id of the device."""
        return int(self._data["id"])

    @property
    def user_id(self) -> int:
        """Return the id of the user the device belongs to."""
        return int(self._data["user_id"])

    @property
    def hardware_id(self) -> str:
        """Return the hardware id of the device."""
        return str(self._data["hardware_id"])

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return unquote(self._data["name"])

    @property
    def added(self) -> int:
        """Return the time the device was added."""
        return int(self._data["added"])

    @property
    def last_connected(self) -> int:
        """Return the last time the device was connected."""
        return int(self._data["last_connected"])

    @property
    def os(self) -> DeviceOS:
        """Return the operating system of the device."""
        try:
            return DeviceOS(self._data["os"])
        except ValueError:
            log_unknown_value(DeviceOS, self._data["os"])

        return DeviceOS.NONE

    @property
    def type(self) -> DeviceType:
        """Return the type of the device."""
        try:
            return DeviceType(self._data["type"])
        except ValueError:
            log_unknown_value(DeviceType, self._data["type"])

        return DeviceType.NONE

    @property
    def app(self) -> DeviceApp:
        """Return the app version of the device."""
        try:
            return DeviceApp(self._data["app"])
        except ValueError:
            log_unknown_value(DeviceApp, self._data["app"])

        return DeviceApp.NONE

    @property
    def connected(self) -> bool:
        """Return whether the device is currently connected."""
        return bool(self._data["connected"])

    @property
    def push_registration_id(self) -> str:
        """Return the push registration id of the device."""
        return str(self._data["push_registration_id"])


class HomeeUser(HomeeObject):
    """Represent a Homee user."""

    @property
    def id(self) -> int:
        """Return the unique id of the user."""
        return int(self._data["id"])

    @property
    def username(self) -> str:
        """Return the username of the user."""
        return str(self._data["username"])

    @property
    def forename(self) -> str:
        """Return the forename of the user."""
        return unquote(self._data["forename"])

    @property
    def surname(self) -> str:
        """Return the surname of the user."""
        return unquote(self._data["surname"])

    @property
    def image(self) -> str:
        """Return the image of the user."""
        return unquote(self._data["image"])

    @property
    def role(self) -> UserRole:
        """Return the role of the user."""
        try:
            return UserRole(self._data["role"])
        except ValueError:
            log_unknown_value(UserRole, self._data["role"])

        return UserRole.NONE

    @property
    def type(self) -> int:
        """Return the type of the user."""
        return int(self._data["type"])

    @property
    def email(self) -> str:
        """Return the email of the user."""
        return unquote(self._data["email"])

    @property
    def phone(self) -> str:
        """Return the phone number of the user."""
        return str(self._data["phone"])

    @property
    def added(self) -> int:
        """Return the time the user was added."""
        return int(self._data["added"])

    @property
    def homee_image(self) -> str:
        """Return the homee image of the user."""
        return unquote(self._data["homee_image"])

    @property
    def access(self) -> int:
        """Return the access level of the user."""
        return int(self._data["access"])

    @property
    def presence_detection(self) -> bool:
        """Return whether presence detection is enabled for the user."""
        return bool(self._data["presence_detection"])

    @property
    def cube_push_notifications(self) -> bool:
        """Return whether cube push notifications are enabled for the user."""
        return bool(self._data["cube_push_notifications"])

    @property
    def cube_email_notifications(self) -> bool:
        """Return whether cube email notifications are enabled for the user."""
        return bool(self._data["cube_email_notifications"])

    @property
    def cube_sms_notifications(self) -> bool:
        """Return whether cube SMS notifications are enabled for the user."""
        return bool(self._data["cube_sms_notifications"])

    @property
    def warning_push_notifications(self) -> bool:
        """Return whether warning push notifications are enabled for the user."""
        return bool(self._data["warning_push_notifications"])

    @property
    def warning_push_notifications_as_critical(self) -> bool:
        """Return whether warning push notifications are marked as critical for the user."""
        return bool(self._data["warning_push_notifications_as_critical"])

    @property
    def warning_email_notifications(self) -> bool:
        """Return whether warning email notifications are enabled for the user."""
        return bool(self._data["warning_email_notifications"])

    @property
    def warning_sms_notifications(self) -> bool:
        """Return whether warning SMS notifications are enabled for the user."""
        return bool(self._data["warning_sms_notifications"])

    @property
    def node_push_notifications(self) -> bool:
        """Return whether node push notifications are enabled for the user."""
        return bool(self._data["node_push_notifications"])

    @property
    def node_email_notifications(self) -> bool:
        """Return whether node email notifications are enabled for the user."""
        return bool(self._data["node_email_notifications"])

    @property
    def node_sms_notifications(self) -> bool:
        """Return whether node SMS notifications are enabled for the user."""
        return bool(self._data["node_sms_notifications"])

    @property
    def update_push_notifications(self) -> bool:
        """Return whether update push notifications are enabled for the user."""
        return bool(self._data["update_push_notifications"])

    @property
    def update_email_notifications(self) -> bool:
        """Return whether update email notifications are enabled for the user."""
        return bool(self._data["update_email_notifications"])

    @property
    def update_sms_notifications(self) -> bool:
        """Return whether update SMS notifications are enabled for the user."""
        return bool(self._data["update_sms_notifications"])

    @property
    def homeegram_push_notifications(self) -> bool:
        """Return whether homeegram push notifications are enabled for the user."""
        return bool(self._data["homeegram_push_notifications"])

    @property
    def homeegram_email_notifications(self) -> bool:
        """Return whether homeegram email notifications are enabled for the user."""
        return bool(self._data["homeegram_email_notifications"])

    @property
    def homeegram_sms_notifications(self) -> bool:
        """Return whether homeegram SMS notifications are enabled for the user."""
        return bool(self._data["homeegram_sms_notifications"])

    @property
    def api_push_notifications(self) -> bool:
        """Return whether API push notifications are enabled for the user."""
        return bool(self._data["api_push_notifications"])

    @property
    def api_email_notifications(self) -> bool:
        """Return whether API email notifications are enabled for the user."""
        return bool(self._data["api_email_notifications"])

    @property
    def api_sms_notifications(self) -> bool:
        """Return whether API SMS notifications are enabled for the user."""
        return bool(self._data["api_sms_notifications"])

    @property
    def plan_push_notifications(self) -> bool:
        """Return whether plan push notifications are enabled for the user."""
        return bool(self._data["plan_push_notifications"])

    @property
    def plan_email_notifications(self) -> bool:
        """Return whether plan email notifications are enabled for the user."""
        return bool(self._data["plan_email_notifications"])

    @property
    def plan_sms_notifications(self) -> bool:
        """Return whether plan SMS notifications are enabled for the user."""
        return bool(self._data["plan_sms_notifications"])

    @property
    def watchdog_push_notifications(self) -> bool:
        """Return whether watchdog push notifications are enabled for the user."""
        return bool(self._data["watchdog_push_notifications"])

    @property
    def watchdog_email_notifications(self) -> bool:
        """Return whether watchdog email notifications are enabled for the user."""
        return bool(self._data["watchdog_email_notifications"])

    @property
    def watchdog_sms_notifications(self) -> bool:
        """Return whether watchdog SMS notifications are enabled for the user."""
        return bool(self._data["watchdog_sms_notifications"])

    @property
    def devices(self) -> list[HomeeDevice]:
        """Return the list of devices associated with the user."""
        devices = []
        for device in self._data["devices"]:
            devices.append(HomeeDevice(device))

        return devices
