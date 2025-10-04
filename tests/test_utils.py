import pytest

from app.utils import validate_serial, validate_card


@pytest.mark.parametrize("value", ["000000", "123456", "999999"])
def test_validate_serial_ok(value):
    assert validate_serial(value) == value


@pytest.mark.parametrize(
    "value", ["", "12345", "1234567", "12AB56", None, 123456, " 123456", "123456 "]
)
def test_validate_serial_invalid(value):
    with pytest.raises(ValueError):
        validate_serial(value)


@pytest.mark.parametrize("value", ["000000", "111111", "654321"])
def test_validate_card_ok(value):
    assert validate_card(value) == value


@pytest.mark.parametrize(
    "value", ["", "1", "abcdef", "12345x", None, 654321, " 111111", "111111 "]
)
def test_validate_card_invalid(value):
    with pytest.raises(ValueError):
        validate_card(value)
