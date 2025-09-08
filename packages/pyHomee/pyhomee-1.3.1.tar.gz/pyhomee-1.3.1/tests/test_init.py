"""Test initialization of the Homee class."""
from pyHomee import Homee

from .conftest import (
    HOMEE_IP,
    HOMEE_USER,
    HOMEE_PASSWORD,
    HOMEE_DEVICE_ID,
    RECONNECT_INTERVAL,
    MAX_RETRIES
)

def test_initialize_homee(test_homee: Homee) -> None:
    """Test that Homee can be initialized correctly."""
    assert test_homee.host == HOMEE_IP
    assert test_homee.user == HOMEE_USER
    assert test_homee.password == HOMEE_PASSWORD
    assert test_homee.device == HOMEE_DEVICE_ID
    assert test_homee.reconnect_interval == RECONNECT_INTERVAL
    assert test_homee.max_retries == MAX_RETRIES
    assert not test_homee.connected
