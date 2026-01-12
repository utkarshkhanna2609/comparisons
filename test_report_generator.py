import pytest
from unittest.mock import Mock, patch

from report_generator import ReportGenerator


@pytest.fixture
def mock_processor():
    """Create a mock processor with default attributes for testing."""
    processor = Mock()
    processor.records = []
    processor.get_total_sales.return_value = 0.0
    processor.get_average_sale.return_value = 0.0
    processor.group_by_region.return_value = {}
    processor.get_top_products.return_value = []
    return processor


@pytest.fixture
def report_generator_instance(mock_processor):
    """Create ReportGenerator instance for testing."""
    return ReportGenerator(processor=mock_processor)


def test_ReportGenerator___init___stores_processor(mock_processor):
    """Test that __init__ correctly stores the processor."""
    rg = ReportGenerator(processor=mock_processor)
    assert rg.processor is mock_processor


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_summary_report_basic(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_summary_report with basic processor values."""
    mock_processor.records = [1, 2, 3]
    mock_processor.get_total_sales.return_value = 1234.56
    mock_processor.get_average_sale.return_value = 411.52

    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_summary_report()

    assert "SALES SUMMARY REPORT" in report
    assert "Total Records: 3" in report
    assert "Total Sales: $1,234.56" in report
    assert "Average Sale: $411.52" in report
    assert report.startswith("=" * 50)
    assert report.endswith("=" * 50)
    assert mock_processor.get_total_sales.called
    assert mock_processor.get_average_sale.called


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_summary_report_zero_records(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_summary_report when there are zero records."""
    mock_processor.records = []
    mock_processor.get_total_sales.return_value = 0.0
    mock_processor.get_average_sale.return_value = 0.0

    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_summary_report()

    assert "Total Records: 0" in report
    assert "Total Sales: $0.00" in report
    assert "Average Sale: $0.00" in report


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_regional_report_basic(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_regional_report with multiple regions and records."""
    Record = Mock
    r1 = Record()
    r1.amount = 100.0
    r2 = Record()
    r2.amount = 200.0
    r3 = Record()
    r3.amount = 300.0

    mock_processor.group_by_region.return_value = {
        "North": [r1, r2],
        "South": [r3],
    }

    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_regional_report()

    assert "REGIONAL SALES REPORT" in report
    assert "\nRegion: North" in report
    assert "  Records: 2" in report
    assert "  Total Sales: $300.00" in report
    assert "  Average: $150.00" in report

    assert "\nRegion: South" in report
    assert "  Records: 1" in report
    assert "  Total Sales: $300.00" in report
    assert "  Average: $300.00" in report

    mock_processor.group_by_region.assert_called_once()


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_regional_report_empty_group(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_regional_report when group_by_region returns empty dict."""
    mock_processor.group_by_region.return_value = {}
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_regional_report()

    assert "REGIONAL SALES REPORT" in report
    # No regions should be listed
    assert "\nRegion:" not in report
    assert report.endswith("=" * 50)


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_regional_report_zero_records_in_region(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_regional_report when a region has zero records."""
    mock_processor.group_by_region.return_value = {"EmptyRegion": []}
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_regional_report()

    assert "\nRegion: EmptyRegion" in report
    assert "  Records: 0" in report
    assert "  Total Sales: $0.00" in report
    assert "  Average: $0.00" in report


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_top_products_report_default_limit(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_top_products_report with default limit."""
    mock_processor.get_top_products.return_value = [
        ("Product A", 1000.0),
        ("Product B", 800.0),
        ("Product C", 600.0),
    ]
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_top_products_report()

    mock_processor.get_top_products.assert_called_once_with(5)
    assert "TOP 5 PRODUCTS BY SALES" in report
    assert "1. Product A: $1,000.00" in report
    assert "2. Product B: $800.00" in report
    assert "3. Product C: $600.00" in report
    assert report.endswith("=" * 50)


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_top_products_report_custom_limit(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_top_products_report with a custom limit."""
    mock_processor.get_top_products.return_value = [
        ("Product X", 500.0),
        ("Product Y", 400.0),
    ]
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_top_products_report(limit=2)

    mock_processor.get_top_products.assert_called_once_with(2)
    assert "TOP 2 PRODUCTS BY SALES" in report
    assert "1. Product X: $500.00" in report
    assert "2. Product Y: $400.00" in report


@patch("report_generator.format_currency")
def test_ReportGenerator_generate_top_products_report_empty_list(format_currency_mock, report_generator_instance, mock_processor):
    """Test generate_top_products_report when no products are returned."""
    mock_processor.get_top_products.return_value = []
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_top_products_report(limit=3)

    assert "TOP 3 PRODUCTS BY SALES" in report
    # No numbered lines should appear
    assert "1." not in report
    assert report.endswith("=" * 50)


def test_ReportGenerator_apply_advanced_filter_valid_expression(report_generator_instance, mock_processor):
    """Test apply_advanced_filter with a valid filter expression."""
    Record = Mock
    r1 = Record()
    r1.amount = 100
    r1.region = "North"
    r2 = Record()
    r2.amount = 50
    r2.region = "South"
    r3 = Record()
    r3.amount = 200
    r3.region = "North"

    mock_processor.records = [r1, r2, r3]

    # Expression is evaluated in the context where 'record' is defined in the loop
    filtered = report_generator_instance.apply_advanced_filter("record.amount > 100 and record.region == 'North'")

    assert filtered == [r3]


def test_ReportGenerator_apply_advanced_filter_invalid_expression(report_generator_instance, mock_processor):
    """Test apply_advanced_filter silently ignores invalid expressions."""
    Record = Mock
    r1 = Record()
    r1.amount = 100
    mock_processor.records = [r1]

    # This will raise inside eval; method should catch and ignore
    filtered = report_generator_instance.apply_advanced_filter("invalid syntax !!!")

    assert filtered == []


def test_ReportGenerator_apply_advanced_filter_expression_raises_per_record(report_generator_instance, mock_processor):
    """Test apply_advanced_filter continues when eval raises for some records."""
    class Record:
        def __init__(self, amount):
            self.amount = amount

    r1 = Record(100)
    r2 = Record("not-a-number")
    r3 = Record(300)

    mock_processor.records = [r1, r2, r3]

    # This will work for numeric amounts, but raise for the string amount
    filtered = report_generator_instance.apply_advanced_filter("record.amount > 150")

    # r2 should be skipped due to exception, r3 should be included
    assert filtered == [r3]


@patch("report_generator.format_currency")
@patch("report_generator.BusinessCalculator")
def test_ReportGenerator_calculate_growth_report_basic(business_calc_mock, format_currency_mock, report_generator_instance):
    """Test calculate_growth_report with normal values."""
    business_calc_mock.calculate_compound_growth_rate.return_value = 12.3456
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.calculate_growth_report(
        region="North",
        start_value=1000.0,
        end_value=2000.0,
        periods=3,
    )

    business_calc_mock.calculate_compound_growth_rate.assert_called_once_with(
        1000.0, 2000.0, 3
    )

    assert "GROWTH ANALYSIS - North" in report
    assert "Starting Value: $1,000.00" in report
    assert "Ending Value: $2,000.00" in report
    assert "Periods: 3" in report
    # Growth rate formatted to 2 decimal places with percent sign
    assert "Growth Rate: 12.35%" in report
    assert report.startswith("=" * 50)
    assert report.endswith("=" * 50)


@patch("report_generator.format_currency")
@patch("report_generator.BusinessCalculator")
def test_ReportGenerator_calculate_growth_report_zero_periods(business_calc_mock, format_currency_mock, report_generator_instance):
    """Test calculate_growth_report passes zero periods to BusinessCalculator."""
    business_calc_mock.calculate_compound_growth_rate.return_value = 0.0
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.calculate_growth_report(
        region="Global",
        start_value=0.0,
        end_value=0.0,
        periods=0,
    )

    business_calc_mock.calculate_compound_growth_rate.assert_called_once_with(
        0.0, 0.0, 0
    )
    assert "GROWTH ANALYSIS - Global" in report
    assert "Growth Rate: 0.00%" in report


@patch("report_generator.format_currency")
@patch("report_generator.BusinessCalculator")
def test_ReportGenerator_calculate_growth_report_negative_values(business_calc_mock, format_currency_mock, report_generator_instance):
    """Test calculate_growth_report with negative start and end values."""
    business_calc_mock.calculate_compound_growth_rate.return_value = -5.0
    format_currency_mock.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.calculate_growth_report(
        region="TestRegion",
        start_value=-100.0,
        end_value=-200.0,
        periods=2,
    )

    business_calc_mock.calculate_compound_growth_rate.assert_called_once_with(
        -100.0, -200.0, 2
    )
    assert "Starting Value: $-100.00" in report
    assert "Ending Value: $-200.00" in report
    assert "Growth Rate: -5.00%" in report