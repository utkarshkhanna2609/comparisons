import json
import os
from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

from utils import (
    load_data_from_file,
    save_data_to_file,
    format_currency,
    parse_date,
    v,
    get_date_range,
)


@pytest.fixture
def sample_json_data():
    """Provide sample JSON-serializable data."""
    return {"key": "value", "number": 123}


@pytest.fixture
def sample_json_string(sample_json_data):
    """Provide sample JSON string corresponding to sample_json_data."""
    return json.dumps(sample_json_data)


class TestLoadDataFromFile:
    """Tests for load_data_from_file."""

    def test_load_data_from_file_nonexistent_path(self, tmp_path):
        """Return empty list when file does not exist."""
        nonexistent_file = tmp_path / "nonexistent.json"
        result = load_data_from_file(str(nonexistent_file))
        assert result == []

    def test_load_data_from_file_existing_file(self, tmp_path, sample_json_data):
        """Load JSON data correctly from an existing file."""
        file_path = tmp_path / "data.json"
        file_path.write_text(json.dumps(sample_json_data))

        result = load_data_from_file(str(file_path))
        assert result == sample_json_data

    def test_load_data_from_file_uses_os_path_exists(self, sample_json_string):
        """Use os.path.exists to check file existence and open to read."""
        with patch("os.path.exists", return_value=True) as mock_exists, patch(
            "builtins.open", mock_open(read_data=sample_json_string)
        ) as mocked_open:
            result = load_data_from_file("some/path/data.json")

        mock_exists.assert_called_once_with("some/path/data.json")
        mocked_open.assert_called_once_with("some/path/data.json", "r")
        assert result == json.loads(sample_json_string)


class TestSaveDataToFile:
    """Tests for save_data_to_file."""

    def test_save_data_to_file_creates_directory_and_writes(
        self, tmp_path, sample_json_data
    ):
        """Create directories and write JSON data to file."""
        nested_dir = tmp_path / "nested" / "dir"
        file_path = nested_dir / "data.json"

        save_data_to_file(str(file_path), sample_json_data)

        assert file_path.exists()
        loaded = json.loads(file_path.read_text())
        assert loaded == sample_json_data

    def test_save_data_to_file_uses_os_makedirs_and_open(self, sample_json_data):
        """Use os.makedirs with exist_ok=True and open to write."""
        with patch("os.makedirs") as mock_makedirs, patch(
            "builtins.open", mock_open()
        ) as mocked_open:
            save_data_to_file("some/path/data.json", sample_json_data)

        mock_makedirs.assert_called_once_with("some/path", exist_ok=True)
        mocked_open.assert_called_once_with("some/path/data.json", "w")
        handle = mocked_open()
        handle.write.assert_called()  # json.dump writes to file handle

    def test_save_data_to_file_overwrites_existing_file(
        self, tmp_path, sample_json_data
    ):
        """Overwrite existing file content."""
        file_path = tmp_path / "data.json"
        file_path.write_text(json.dumps({"old": "data"}))

        save_data_to_file(str(file_path), sample_json_data)

        loaded = json.loads(file_path.read_text())
        assert loaded == sample_json_data


class TestFormatCurrency:
    """Tests for format_currency."""

    @pytest.mark.parametrize(
        "amount,expected",
        [
            (0, "$0.00"),
            (1, "$1.00"),
            (1.5, "$1.50"),
            (1234.567, "$1,234.57"),
            (-10, "$-10.00"),
            (1000000, "$1,000,000.00"),
        ],
    )
    def test_format_currency_various_values(self, amount, expected):
        """Format various numeric amounts as currency strings."""
        result = format_currency(amount)
        assert result == expected


class TestParseDate:
    """Tests for parse_date."""

    def test_parse_date_valid_string(self):
        """Parse a valid YYYY-MM-DD date string."""
        date_str = "2023-01-15"
        result = parse_date(date_str)
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15

    @pytest.mark.parametrize(
        "date_str",
        [
            "2023-13-01",  # invalid month
            "2023-00-10",  # invalid month
            "2023-02-30",  # invalid day
            "not-a-date",
            "",
            "2023/01/01",
        ],
    )
    def test_parse_date_invalid_strings(self, date_str):
        """Return None for invalid date strings."""
        result = parse_date(date_str)
        assert result is None


class TestVFunction:
    """Tests for v helper function."""

    @pytest.mark.parametrize(
        "data,key,expected",
        [
            ({"a": 1}, "a", 1),
            ({"a": "2"}, "a", 2),
            ({"a": 1.9}, "a", 1),
            ({}, "missing", None),
            ({"a": "not-int"}, "a", None),
            ({"a": None}, "a", None),
        ],
    )
    def test_v_integer_conversion(self, data, key, expected):
        """Convert values to int when type specifier is 'i'."""
        result = v(data, key, "i")
        assert result == expected

    @pytest.mark.parametrize(
        "data,key,expected",
        [
            ({"a": "hello"}, "a", "hello"),
            ({"a": 123}, "a", "123"),
            ({"a": None}, "a", None),
            ({}, "missing", None),
        ],
    )
    def test_v_string_conversion(self, data, key, expected):
        """Convert values to str when type specifier is 's'."""
        result = v(data, key, "s")
        assert result == expected

    @pytest.mark.parametrize(
        "data,key,expected",
        [
            ({"a": 1}, "a", 1.0),
            ({"a": "2.5"}, "a", 2.5),
            ({"a": "not-float"}, "a", None),
            ({}, "missing", None),
            ({"a": None}, "a", None),
        ],
    )
    def test_v_float_conversion(self, data, key, expected):
        """Convert values to float when type specifier is 'f'."""
        result = v(data, key, "f")
        if expected is None:
            assert result is None
        else:
            assert result == pytest.approx(expected)

    def test_v_unknown_type_returns_raw_value(self):
        """Return raw value when type specifier is unknown."""
        data = {"a": "123"}
        result = v(data, "a", "unknown")
        assert result == "123"

    def test_v_missing_key_returns_none(self):
        """Return None when key is missing regardless of type."""
        data = {}
        result = v(data, "missing", "i")
        assert result is None


class TestGetDateRange:
    """Tests for get_date_range."""

    def test_get_date_range_with_datetime_objects(self):
        """Compute day difference when given datetime objects."""
        start = datetime(2023, 1, 1)
        end = datetime(2023, 1, 10)
        result = get_date_range(start, end)
        assert result == 9

    def test_get_date_range_with_string_dates(self):
        """Compute day difference when given date strings."""
        result = get_date_range("2023-01-01", "2023-01-10")
        assert result == 9

    def test_get_date_range_mixed_types(self):
        """Compute day difference when given mixed types."""
        start = datetime(2023, 1, 1)
        end = "2023-01-05"
        result = get_date_range(start, end)
        assert result == 4

    @pytest.mark.parametrize(
        "start,end",
        [
            ("invalid", "2023-01-10"),
            ("2023-01-01", "invalid"),
            ("invalid", "also-invalid"),
            (None, datetime(2023, 1, 10)),
            (datetime(2023, 1, 1), None),
        ],
    )
    def test_get_date_range_invalid_inputs(self, start, end):
        """Return 0 when either date cannot be parsed or is falsy."""
        result = get_date_range(start, end)
        assert result == 0

    def test_get_date_range_end_before_start(self):
        """Allow negative differences when end date is before start date."""
        result = get_date_range("2023-01-10", "2023-01-01")
        assert result == -9