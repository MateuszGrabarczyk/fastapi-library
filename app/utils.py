import re
from datetime import datetime, timezone

SIX_DIGITS = re.compile(r"^\d{6}$")


def validate_serial(serial: str) -> str:
    if not isinstance(serial, str) or not SIX_DIGITS.match(serial):
        raise ValueError("serial_number must be exactly 6 digits")
    return serial


def validate_card(card: str) -> str:
    if not isinstance(card, str) or not SIX_DIGITS.match(card):
        raise ValueError("card_number must be exactly 6 digits")
    return card


def utcnow() -> datetime:
    return datetime.now(timezone.utc)