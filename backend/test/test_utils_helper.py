import re
import time
from utils import helpers  # adjust import path if needed


def test_generate_uuid():
    uuid_str = helpers.generate_uuid()
    # UUID should be a string of correct format
    assert isinstance(uuid_str, str)
    assert re.match(
        r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
        uuid_str
    )


def test_timestamp_increases():
    t1 = helpers.timestamp()
    time.sleep(1)
    t2 = helpers.timestamp()
    assert t2 > t1  # timestamps should increase


def test_format_duration_seconds():
    assert helpers.format_duration(45) == "45s"


def test_format_duration_minutes():
    assert helpers.format_duration(65) == "1m 5s"
    assert helpers.format_duration(3599) == "59m 59s"


def test_format_duration_hours():
    assert helpers.format_duration(3700) == "1h 1m"
    assert helpers.format_duration(7322) == "2h 2m"


def test_safe_get_existing_key():
    d = {"user": {"profile": {"name": "Alice"}}}
    assert helpers.safe_get(d, "user", "profile", "name") == "Alice"


def test_safe_get_missing_key():
    d = {"user": {"profile": {}}}
    assert helpers.safe_get(d, "user", "profile", "age", default=25) == 25


def test_safe_get_non_dict():
    d = {"user": None}
    assert helpers.safe_get(d, "user", "profile", "name", default="N/A") == "N/A"
