import pytest
from networkapp.models.switch import cisco_switch

def test_switch_instantition():
    sw = cisco_switch(hostname="test", user="test", psswd="foo", device_type="cisco_nexus")
    assert sw is not None
    assert sw.hostname == "test"

def test_error_instantition():
    """
    Validate exception are raised when params are missing
    :return:
    """
    with pytest.raises(Exception):
        sw = cisco_switch()

    with pytest.raises(Exception):
        sw = cisco_switch(hostname="test")

