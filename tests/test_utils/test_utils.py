from attendance_logger.utils.utils import (
    check_password_hash,
    hash_password,
    convert_naive_time_to_aware,
)
import datetime as dt


def test_check_password_hash() -> None:
    password = "Hello world!"
    hash = hash_password(password)
    assert check_password_hash(password, hash) is True


def test_check_password_hash_mismatch() -> None:
    password = "Hello world!"
    wrong_password = "Hello Wor1d!"
    hash = hash_password(password)
    assert check_password_hash(wrong_password, hash) is False


def test_convert_native_time_to_aware() -> None:
    datetime_wo_tzinfo = dt.datetime(2025, 10, 15, 18, 20)
    print(datetime_wo_tzinfo)
    result = convert_naive_time_to_aware(datetime_wo_tzinfo)
    datetime = dt.datetime(2025, 10, 15, 18, 20, tzinfo=dt.UTC)
    print(datetime)
    assert result == datetime
