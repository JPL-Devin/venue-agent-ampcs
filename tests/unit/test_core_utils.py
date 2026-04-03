"""Unit tests for core/core_utils.py pure functions."""
import pytest
from datetime import datetime


class TestStr2Bool:
    def test_true_bool(self):
        from core.core_utils import str2bool
        assert str2bool(True) is True

    def test_false_bool(self):
        from core.core_utils import str2bool
        assert str2bool(False) is False

    def test_true_string(self):
        from core.core_utils import str2bool
        assert str2bool('true') is True

    def test_false_string(self):
        from core.core_utils import str2bool
        assert str2bool('false') is False

    def test_true_capitalized(self):
        from core.core_utils import str2bool
        assert str2bool('True') is True

    def test_false_uppercase(self):
        from core.core_utils import str2bool
        assert str2bool('FALSE') is False


class TestNormalizeWithMicrosecs:
    def test_subsecond(self):
        from core.core_utils import normalize_with_microsecs
        result = normalize_with_microsecs('2024-001T12:00:00.123456')
        assert result == '2024-001T12:00:00.123456'

    def test_no_subsecond(self):
        from core.core_utils import normalize_with_microsecs
        result = normalize_with_microsecs('2024-001T12:00:00')
        assert result == '2024-001T12:00:00.000000'

    def test_nano_precision_truncated(self):
        from core.core_utils import normalize_with_microsecs
        result = normalize_with_microsecs('2024-001T12:00:00.123456789')
        assert result == '2024-001T12:00:00.123456'


class TestDoyToIsoZ:
    def test_basic_conversion(self):
        from core.core_utils import doyToIsoZ
        result = doyToIsoZ('2024-001T12:30:45.123000')
        assert result == '2024-01-01T12:30:45.123Z'

    def test_mid_year(self):
        from core.core_utils import doyToIsoZ
        result = doyToIsoZ('2024-182T00:00:00.000000')
        assert result == '2024-06-30T00:00:00.000Z'


class TestGetNowIsoZ:
    def test_returns_valid_iso_format(self):
        from core.core_utils import get_now_isoZ
        result = get_now_isoZ()
        assert result.endswith('Z')
        assert 'T' in result
        # Should be parseable
        datetime.strptime(result, '%Y-%m-%dT%H:%M:%S.%fZ')


class TestDoyToDatetime:
    def test_with_subsecond(self):
        from core.core_utils import doy_to_datetime
        result = doy_to_datetime('2024-001T12:30:45.123')
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.minute == 30

    def test_without_subsecond(self):
        from core.core_utils import doy_to_datetime
        result = doy_to_datetime('2024-182T00:00:00')
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 30


class TestIsoToDatetime:
    def test_with_z_and_millis(self):
        from core.core_utils import iso_to_datetime
        result = iso_to_datetime('2024-01-01T12:30:45.123Z')
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1

    def test_without_z(self):
        from core.core_utils import iso_to_datetime
        result = iso_to_datetime('2024-01-01T12:30:45')
        assert result.year == 2024
        assert result.hour == 12

    def test_with_z_no_millis(self):
        from core.core_utils import iso_to_datetime
        result = iso_to_datetime('2024-01-01T12:30:45Z')
        assert result.year == 2024

    def test_without_z_with_millis(self):
        from core.core_utils import iso_to_datetime
        result = iso_to_datetime('2024-01-01T12:30:45.123')
        assert result.microsecond == 123000


class TestDatetimeToDoy:
    def test_no_resolution(self):
        from core.core_utils import datetime_to_doy
        dt = datetime(2024, 1, 1, 12, 30, 45)
        result = datetime_to_doy(dt)
        assert result == '2024-001T12:30:45'

    def test_millis_resolution(self):
        from core.core_utils import datetime_to_doy
        dt = datetime(2024, 1, 1, 12, 30, 45, 123000)
        result = datetime_to_doy(dt, res='millis')
        assert result == '2024-001T12:30:45.123'

    def test_micros_resolution(self):
        from core.core_utils import datetime_to_doy
        dt = datetime(2024, 1, 1, 12, 30, 45, 123456)
        result = datetime_to_doy(dt, res='micros')
        assert result == '2024-001T12:30:45.123456'


class TestDatetimeToIsoZ:
    def test_no_resolution(self):
        from core.core_utils import datetime_to_isoZ
        dt = datetime(2024, 1, 1, 12, 30, 45)
        result = datetime_to_isoZ(dt)
        assert result == '2024-01-01T12:30:45'

    def test_millis_resolution(self):
        from core.core_utils import datetime_to_isoZ
        dt = datetime(2024, 1, 1, 12, 30, 45, 123000)
        result = datetime_to_isoZ(dt, res='millis')
        assert result == '2024-01-01T12:30:45.123'

    def test_micros_resolution(self):
        from core.core_utils import datetime_to_isoZ
        dt = datetime(2024, 1, 1, 12, 30, 45, 123456)
        result = datetime_to_isoZ(dt, res='micros')
        assert result == '2024-01-01T12:30:45.123456'


class TestGetCsvRowReader:
    def test_basic_csv(self):
        from core.core_utils import get_csv_row_reader
        csv_str = "a,b,c\n1,2,3"
        reader = get_csv_row_reader(csv_str)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ['a', 'b', 'c']
        assert rows[1] == ['1', '2', '3']


class TestValidateTime:
    def test_doy_format(self):
        from core.core_utils import validate_time
        time_type, converted = validate_time('2024-001T12:30:45')
        assert time_type == 'SCET'

    def test_doy_with_subsecond(self):
        from core.core_utils import validate_time
        time_type, converted = validate_time('2024-001T12:30:45.123')
        assert time_type == 'SCET'

    def test_iso_format(self):
        from core.core_utils import validate_time
        time_type, converted = validate_time('2024-01-01T12:30:45')
        assert time_type == 'SCET'

    def test_sclk_float(self):
        from core.core_utils import validate_time
        time_type, converted = validate_time('0410313966.123')
        assert time_type == 'SCLK'

    def test_sclk_dash_format(self):
        from core.core_utils import validate_time
        # SCLK dash format triggers an UnboundLocalError in the existing code
        # (pre-existing bug in core_utils.py). Only dot-separated SCLK works.
        with pytest.raises(UnboundLocalError):
            validate_time('0410313966-123')

    def test_invalid_time(self):
        from core.core_utils import validate_time, TimeParsingError
        with pytest.raises(TimeParsingError):
            validate_time('not-a-time')


class TestReturnValidatedStartEndTimes:
    def test_with_start_and_end(self):
        from core.core_utils import return_validated_start_end_times
        start, end = return_validated_start_end_times(
            '2024-001T12:00:00', '2024-001T13:00:00', 'SCET', None)
        assert start is not None
        assert end is not None

    def test_with_duration_from_start(self):
        from core.core_utils import return_validated_start_end_times
        start, end = return_validated_start_end_times(
            '2024-01-01T12:00:00', None, 'SCET', 3600)
        assert start is not None
        assert end is not None

    def test_error_both_times_and_duration(self):
        from core.core_utils import return_validated_start_end_times, TimeParsingError
        with pytest.raises(TimeParsingError):
            return_validated_start_end_times(
                '2024-001T12:00:00', '2024-001T13:00:00', 'SCET', 3600)


class TestIntsToDay:
    def test_single_digit(self):
        from core.core_utils import ints_to_doy
        result = ints_to_doy([1, 5, 9])
        assert result == ['001', '005', '009']

    def test_double_digit(self):
        from core.core_utils import ints_to_doy
        result = ints_to_doy([10, 50, 99])
        assert result == ['010', '050', '099']

    def test_triple_digit(self):
        from core.core_utils import ints_to_doy
        result = ints_to_doy([100, 200, 365])
        assert result == ['100', '200', '365']


class TestDoysForLookback:
    def test_basic_lookback(self):
        from core.core_utils import doys_for_lookback
        result = doys_for_lookback(3)
        assert isinstance(result, dict)
        # Should have at least one year key
        assert len(result) >= 1
        for year, doys in result.items():
            assert isinstance(year, str)
            assert len(year) == 4
            for doy in doys:
                assert len(doy) == 3
