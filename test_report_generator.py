import pytest
from unittest.mock import Mock, patch

from report_generator import ReportGenerator


@pytest.fixture
def mock_processor():
    """Create a mock processor with default attributes for testing."""
    processor = Mock()
    processor.records = []
    return processor


@pytest.fixture
def report_generator_instance(mock_processor):
    """Create ReportGenerator instance with a mocked processor."""
    return ReportGenerator(processor=mock_processor)


def test_reportgenerator_init_sets_processor(mock_processor):
    """Test that ReportGenerator initialization sets the processor attribute."""
    rg = ReportGenerator(processor=mock_processor)
    assert rg.processor is mock_processor


@patch("report_generator.format_currency")
def test_reportgenerator_generate_summary_report_basic(mock_format_currency, mock_processor, report_generator_instance):
    """Test generate_summary_report builds the correct summary format."""
    mock_processor.get_total_sales.return_value = 1234.56
    mock_processor.get_average_sale.return_value = 123.45
    mock_processor.records = [1, 2, 3]

    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_summary_report()

    lines = report.split("\n")
    assert lines[0] == "=" * 50
    assert lines[1] == "SALES SUMMARY REPORT"
    assert lines[2] == "=" * 50
    assert lines[3] == "Total Records: 3"
    assert lines[4] == "Total Sales: $1,234.56"
    assert lines[5] == "Average Sale: $123.45"
    assert lines[6] == "=" * 50

    mock_processor.get_total_sales.assert_called_once()
    mock_processor.get_average_sale.assert_called_once()
    assert mock_format_currency.call_count == 2
    mock_format_currency.assert_any_call(1234.56)
    mock_format_currency.assert_any_call(123.45)


@patch("report_generator.format_currency")
def test_reportgenerator_generate_summary_report_zero_records(mock_format_currency, mock_processor, report_generator_instance):
    """Test generate_summary_report with zero records."""
    mock_processor.get_total_sales.return_value = 0.0
    mock_processor.get_average_sale.return_value = 0.0
    mock_processor.records = []

    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_summary_report()
    assert "Total Records: 0" in report
    assert "Total Sales: $0.00" in report
    assert "Average Sale: $0.00" in report


@patch("report_generator.format_currency")
def test_reportgenerator_generate_regional_report_basic(mock_format_currency, mock_processor, report_generator_instance):
    """Test generate_regional_report with multiple regions and records."""
    record_a1 = Mock()
    record_a1.amount = 100.0
    record_a2 = Mock()
    record_a2.amount = 200.0
    record_b1 = Mock()
    record_b1.amount = 50.0

    grouped = {
        "North": [record_a1, record_a2],
        "South": [record_b1],
    }
    mock_processor.group_by_region.return_value = grouped

    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_regional_report()
    lines = report.split("\n")

    assert lines[0] == "=" * 50
    assert lines[1] == "REGIONAL SALES REPORT"
    assert lines[2] == "=" * 50

    assert "Region: North" in report
    assert "  Records: 2" in report
    assert "  Total Sales: $300.00" in report
    assert "  Average: $150.00" in report

    assert "Region: South" in report
    assert "  Records: 1" in report
    assert "  Total Sales: $50.00" in report
    assert "  Average: $50.00" in report

    mock_processor.group_by_region.assert_called_once()


@patch("report_generator.format_currency")
def test_reportgenerator_generate_regional_report_empty_region(mock_format_currency, mock_processor, report_generator_instance):
    """Test generate_regional_report with a region that has zero records."""
    grouped = {
        "EmptyRegion": [],
    }
    mock_processor.group_by_region.return_value = grouped

    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_regional_report()

    assert "Region: EmptyRegion" in report
    assert "  Records: 0" in report
    assert "  Total Sales: $0.00" in report
    assert "  Average: $0.00" in report


@patch("report_generator.format_currency")
def test_reportgenerator_generate_top_products_report_default_limit(mock_format_currency, mock_processor, report_generator_instance):
    """Test generate_top_products_report with default limit and sample data."""
    mock_processor.get_top_products.return_value = [
        ("ProdA", 1000.0),
        ("ProdB", 750.5),
        ("ProdC", 500.0),
        ("ProdD", 250.0),
        ("ProdE", 100.0),
    ]
    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_top_products_report()
    lines = report.split("\n")

    assert lines[0] == "=" * 50
    assert lines[1] == "TOP 5 PRODUCTS BY SALES"
    assert lines[2] == "=" * 50

    assert "1. ProdA: $1,000.00" in report
    assert "2. ProdB: $750.50" in report
    assert "3. ProdC: $500.00" in report
    assert "4. ProdD: $250.00" in report
    assert "5. ProdE: $100.00" in report
    assert lines[-1] == "=" * 50

    mock_processor.get_top_products.assert_called_once_with(5)


@patch("report_generator.format_currency")
def test_reportgenerator_generate_top_products_report_custom_limit(mock_format_currency, mock_processor, report_generator_instance):
    """Test generate_top_products_report with a custom limit parameter."""
    mock_processor.get_top_products.return_value = [
        ("ProdA", 1000.0),
        ("ProdB", 750.5),
    ]
    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_top_products_report(limit=2)

    assert "TOP 2 PRODUCTS BY SALES" in report
    assert "1. ProdA: $1,000.00" in report
    assert "2. ProdB: $750.50" in report
    mock_processor.get_top_products.assert_called_once_with(2)


@patch("report_generator.format_currency")
def test_reportgenerator_generate_top_products_report_empty_list(mock_format_currency, mock_processor, report_generator_instance):
    """Test generate_top_products_report when no products are returned."""
    mock_processor.get_top_products.return_value = []
    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.generate_top_products_report(limit=3)

    lines = report.split("\n")
    assert lines[1] == "TOP 3 PRODUCTS BY SALES"
    assert lines[2] == "=" * 50
    assert lines[-1] == "=" * 50
    assert len(lines) == 4  # header line, title, separator, closing separator


def test_reportgenerator_apply_advanced_filter_valid_expression(report_generator_instance, mock_processor):
    """Test apply_advanced_filter with a valid expression that filters correctly."""
    record1 = Mock()
    record1.amount = 100
    record2 = Mock()
    record2.amount = 200
    record3 = Mock()
    record3.amount = 50

    mock_processor.records = [record1, record2, record3]
    report_generator_instance.processor = mock_processor

    expression = "record.amount > 100"
    result = report_generator_instance.apply_advanced_filter(expression)

    assert result == [record2]


def test_reportgenerator_apply_advanced_filter_uses_eval_scope(report_generator_instance, mock_processor):
    """Test apply_advanced_filter uses 'record' from loop in eval expression."""
    record1 = Mock()
    record1.amount = 10
    record2 = Mock()
    record2.amount = 20

    mock_processor.records = [record1, record2]
    report_generator_instance.processor = mock_processor

    expression = "record.amount % 20 == 0"
    result = report_generator_instance.apply_advanced_filter(expression)

    assert result == [record2]


def test_reportgenerator_apply_advanced_filter_invalid_expression_ignored(report_generator_instance, mock_processor):
    """Test apply_advanced_filter silently ignores exceptions from eval."""
    record1 = Mock()
    record1.amount = 10
    record2 = Mock()
    record2.amount = 20

    mock_processor.records = [record1, record2]
    report_generator_instance.processor = mock_processor

    expression = "1 / 0"  # will raise ZeroDivisionError inside eval
    result = report_generator_instance.apply_advanced_filter(expression)

    assert result == []


def test_reportgenerator_apply_advanced_filter_expression_raising_name_error(report_generator_instance, mock_processor):
    """Test apply_advanced_filter ignores NameError from invalid variable in expression."""
    record = Mock()
    record.amount = 10
    mock_processor.records = [record]
    report_generator_instance.processor = mock_processor

    expression = "nonexistent_var > 5"
    result = report_generator_instance.apply_advanced_filter(expression)

    assert result == []


@patch("report_generator.BusinessCalculator")
@patch("report_generator.format_currency")
def test_reportgenerator_calculate_growth_report_basic(mock_format_currency, mock_business_calculator, report_generator_instance):
    """Test calculate_growth_report builds report using BusinessCalculator result."""
    mock_business_calculator.calculate_compound_growth_rate.return_value = 12.3456
    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    region = "North"
    start_value = 1000.0
    end_value = 2000.0
    periods = 3

    report = report_generator_instance.calculate_growth_report(region, start_value, end_value, periods)
    lines = report.split("\n")

    assert lines[0] == "=" * 50
    assert lines[1] == f"GROWTH ANALYSIS - {region}"
    assert lines[2] == "=" * 50
    assert lines[3] == "Starting Value: $1,000.00"
    assert lines[4] == "Ending Value: $2,000.00"
    assert lines[5] == f"Periods: {periods}"
    assert lines[6] == "Growth Rate: 12.35%"
    assert lines[7] == "=" * 50

    mock_business_calculator.calculate_compound_growth_rate.assert_called_once_with(
        start_value, end_value, periods
    )
    mock_format_currency.assert_any_call(start_value)
    mock_format_currency.assert_any_call(end_value)


@patch("report_generator.BusinessCalculator")
@patch("report_generator.format_currency")
def test_reportgenerator_calculate_growth_report_zero_growth(mock_format_currency, mock_business_calculator, report_generator_instance):
    """Test calculate_growth_report when BusinessCalculator returns zero growth."""
    mock_business_calculator.calculate_compound_growth_rate.return_value = 0.0
    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.calculate_growth_report("East", 500.0, 500.0, 1)
    assert "Growth Rate: 0.00%" in report


@patch("report_generator.BusinessCalculator")
@patch("report_generator.format_currency")
def test_reportgenerator_calculate_growth_report_negative_growth(mock_format_currency, mock_business_calculator, report_generator_instance):
    """Test calculate_growth_report when BusinessCalculator returns negative growth."""
    mock_business_calculator.calculate_compound_growth_rate.return_value = -5.6789
    mock_format_currency.side_effect = lambda x: f"${x:,.2f}"

    report = report_generator_instance.calculate_growth_report("West", 1000.0, 800.0, 2)
    assert "Growth Rate: -5.68%" in report