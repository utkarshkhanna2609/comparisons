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
    """Provide a sample Python object representing JSON data."""
    return {"name": "Alice", "age": 30}


@pytest.fixture
def sample_json_string(sample_json_data):
    """Provide a sample JSON string for file read mocking."""
    return json.dumps(sample_json_data)


@pytest.fixture
def sample_date_strings():
    """Provide a pair of sample date strings."""
    return "2024-01-01", "2024-01-10"


class TestLoadDataFromFile:
    """Tests for load_data_from_file function."""

    def test_load_data_from_file_nonexistent_path(self, tmp_path):
        """Return empty list when file does not exist."""
        nonexistent_file = tmp_path / "does_not_exist.json"
        result = load_data_from_file(str(nonexistent_file))
        assert result == []

    def test_load_data_from_file_valid_json(self, sample_json_data, sample_json_string):
        """Load and parse JSON content from an existing file."""
        m = mock_open(read_data=sample_json_string)
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", m
        ), patch("json.load", return_value=sample_json_data) as mock_json_load:
            result = load_data_from_file("dummy_path.json")
            mock_json_load.assert_called_once()
        assert result == sample_json_data

    def test_load_data_from_file_with_empty_file(self):
        """Handle empty file content gracefully (json.load will raise)."""
        m = mock_open(read_data="")
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", m
        ), patch("json.load", side_effect=ValueError):
            with pytest.raises(ValueError):
                load_data_from_file("dummy_path.json")


class TestSaveDataToFile:
    """Tests for save_data_to_file function."""

    def test_save_data_to_file_creates_directory_and_writes(
        self, sample_json_data, tmp_path
    ):
        """Create directories and write JSON data to file."""
        filepath = tmp_path / "nested" / "data.json"
        m = mock_open()

        with patch("os.makedirs") as mock_makedirs, patch(
            "builtins.open", m
        ), patch("json.dump") as mock_json_dump:
            save_data_to_file(str(filepath), sample_json_data)

        mock_makedirs.assert_called_once_with(os.path.dirname(str(filepath)), exist_ok=True)
        m.assert_called_once_with(str(filepath), "w")
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        assert args[0] == sample_json_data
        assert kwargs.get("indent") == 2

    def test_save_data_to_file_raises_on_io_error(self, sample_json_data, tmp_path):
        """Propagate IOErrors raised during file opening."""
        filepath = tmp_path / "data.json"
        with patch("os.makedirs"), patch(
            "builtins.open", side_effect=IOError("cannot open")
        ):
            with pytest.raises(IOError):
                save_data_to_file(str(filepath), sample_json_data)


class TestFormatCurrency:
    """Tests for format_currency function."""

    @pytest.mark.parametrize(
        "amount, expected",
        [
            (0, "$0.00"),
            (1, "$1.00"),
            (1234.5, "$1,234.50"),
            (1234.567, "$1,234.57"),
            (-50, "$-50.00"),
            (1000000, "$1,000,000.00"),
        ],
    )
    def test_format_currency_various_values(self, amount, expected):
        """Format numeric amounts into currency strings with two decimals and commas."""
        result = format_currency(amount)
        assert result == expected


class TestParseDate:
    """Tests for parse_date function."""

    @pytest.mark.parametrize(
        "input_str, expected",
        [
            ("2024-01-01", datetime(2024, 1, 1)),
            ("1999-12-31", datetime(1999, 12, 31)),
        ],
    )
    def test_parse_date_valid_strings(self, input_str, expected):
        """Parse valid date strings into datetime objects."""
        result = parse_date(input_str)
        assert isinstance(result, datetime)
        assert result == expected

    @pytest.mark.parametrize(
        "input_str",
        [
            "2024/01/01",
            "01-01-2024",
            "invalid",
            "",
            "2024-13-01",
            "2024-00-10",
        ],
    )
    def test_parse_date_invalid_strings(self, input_str):
        """Return None for invalid date strings."""
        result = parse_date(input_str)
        assert result is None


class TestVFunction:
    """Tests for v helper function."""

    @pytest.mark.parametrize(
        "data, key, t, expected",
        [
            ({"a": "10"}, "a", "i", 10),
            ({"b": 20}, "b", "i", 20),
            ({"c": "text"}, "c", "s", "text"),
            ({"d": 5.5}, "d", "f", 5.5),
            ({"e": "5.5"}, "e", "f", 5.5),
        ],
    )
    def test_v_valid_conversions(self, data, key, t, expected):
        """Convert values from dict to specified type when possible."""
        result = v(data, key, t)
        if isinstance(expected, float):
            assert result == pytest.approx(expected)
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "data, key, t",
        [
            ({"a": "not-int"}, "a", "i"),
            ({"b": "not-float"}, "b", "f"),
        ],
    )
    def test_v_invalid_conversions_return_none(self, data, key, t):
        """Return None when conversion to int or float fails."""
        result = v(data, key, t)
        assert result is None

    def test_v_missing_key_returns_none(self):
        """Return None when key does not exist in dictionary."""
        data = {"a": 1}
        result = v(data, "missing", "i")
        assert result is None

    def test_v_type_s_returns_string_representation(self):
        """Return string representation for type 's'."""
        data = {"a": 123}
        result = v(data, "a", "s")
        assert result == "123"

    def test_v_unknown_type_returns_raw_value(self):
        """Return raw value when type code is unknown."""
        data = {"a": 123}
        result = v(data, "a", "unknown")
        assert result == 123


class TestGetDateRange:
    """Tests for get_date_range function."""

    def test_get_date_range_with_datetime_objects(self):
        """Calculate day difference when given datetime objects."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 10)
        result = get_date_range(start, end)
        assert result == 9

    def test_get_date_range_with_string_dates(self, sample_date_strings):
        """Calculate day difference when given date strings."""
        start_str, end_str = sample_date_strings
        result = get_date_range(start_str, end_str)
        assert result == 9

    def test_get_date_range_mixed_types(self):
        """Support mix of datetime and string inputs."""
        start = datetime(2024, 1, 1)
        end_str = "2024-01-05"
        result = get_date_range(start, end_str)
        assert result == 4

    @pytest.mark.parametrize(
        "start, end",
        [
            ("invalid", "2024-01-10"),
            ("2024-01-01", "invalid"),
            ("invalid", "invalid"),
            (None, "2024-01-10"),
            ("2024-01-01", None),
            (None, None),
        ],
    )
    def test_get_date_range_invalid_inputs_return_zero(self, start, end):
        """Return 0 when either date fails to parse or is falsy."""
        result = get_date_range(start, end)
        assert result == 0

    def test_get_date_range_negative_difference(self):
        """Return negative number of days when end_date is before start_date."""
        start = "2024-01-10"
        end = "2024-01-01"
        result = get_date_range(start, end)
        assert result == -9