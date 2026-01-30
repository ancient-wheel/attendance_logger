from attendance_logger.utils.auth import hash_password, check_password_hash


def test_check_password_hash() -> None:
    password = "Hello world!"
    hash = hash_password(password)
    assert check_password_hash(password, hash) is True


def test_check_password_hash_mismatch() -> None:
    password = "Hello world!"
    wrong_password = "Hello Wor1d!"
    hash = hash_password(password)
    assert check_password_hash(wrong_password, hash) is False
