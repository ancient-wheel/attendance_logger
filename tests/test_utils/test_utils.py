from attendance_logger.utils.utils import convert_naive_time_to_aware
import datetime as dt


def test_convert_native_time_to_aware() -> None:
    datetime_wo_tzinfo = dt.datetime(2025, 10, 15, 18, 20)
    print(datetime_wo_tzinfo)
    result = convert_naive_time_to_aware(datetime_wo_tzinfo)
    datetime = dt.datetime(2025, 10, 15, 18, 20, tzinfo=dt.UTC)
    print(datetime)
    assert result == datetime
