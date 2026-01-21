import pytest
from unittest.mock import Mock, patch, call

from main import (
    create_sample_data,
    demonstrate_sorting,
    demonstrate_reports,
    demonstrate_calculations,
    demonstrate_parallel_processing,
    main,
)


@pytest.fixture
def sample_records():
    """Fixture providing the sample records from create_sample_data."""
    return create_sample_data()


@pytest.fixture
def mock_data_processor_class():
    """Fixture to mock the DataProcessor class."""
    with patch("main.DataProcessor") as mock_cls:
        yield mock_cls


@pytest.fixture
def mock_report_generator_class():
    """Fixture to mock the ReportGenerator class."""
    with patch("main.ReportGenerator") as mock_cls:
        yield mock_cls


@pytest.fixture
def mock_business_calculator_class():
    """Fixture to mock the BusinessCalculator class."""
    with patch("main.BusinessCalculator") as mock_cls:
        yield mock_cls


@pytest.fixture
def mock_format_currency():
    """Fixture to mock the format_currency function."""
    with patch("main.format_currency") as mock_func:
        mock_func.side_effect = lambda x: f"${x:,.2f}"
        yield mock_func


def test_create_sample_data_length(sample_records):
    """Test that create_sample_data returns the expected number of records."""
    assert len(sample_records) == 10


def test_create_sample_data_record_structure(sample_records):
    """Test that records from create_sample_data have expected attributes and values."""
    first = sample_records[0]
    assert hasattr(first, "id")
    assert hasattr(first, "product")
    assert hasattr(first, "amount")
    assert hasattr(first, "date")
    assert hasattr(first, "region")

    assert first.id == 1
    assert first.product == "Laptop"
    assert first.amount == pytest.approx(1200.00)
    assert first.date == "2024-01-15"
    assert first.region == "North"


def test_create_sample_data_unique_ids(sample_records):
    """Test that create_sample_data returns records with unique IDs."""
    ids = [r.id for r in sample_records]
    assert len(set(ids)) == len(ids)


def test_create_sample_data_contains_expected_products(sample_records):
    """Test that create_sample_data includes key expected products."""
    products = {r.product for r in sample_records}
    for expected in ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Webcam"]:
        assert expected in products


def test_demonstrate_sorting_happy_path(
    mock_data_processor_class, mock_format_currency, capsys
):
    """Test demonstrate_sorting prints sorted records and uses DataProcessor and format_currency."""
    mock_instance = mock_data_processor_class.return_value
    mock_record = Mock()
    mock_record.product = "TestProduct"
    mock_record.amount = 123.45
    mock_instance.sort_by_amount.return_value = [mock_record] * 5

    demonstrate_sorting()

    mock_data_processor_class.assert_called_once()
    mock_instance.sort_by_amount.assert_called_once()
    assert mock_format_currency.call_count == 5

    captured = capsys.readouterr().out
    assert "--- Demonstrating Record Sorting ---" in captured
    assert "Records sorted by amount:" in captured
    assert "TestProduct" in captured
    assert "$123.45" in captured


def test_demonstrate_sorting_data_processor_error(mock_data_processor_class, capsys):
    """Test demonstrate_sorting handles exception in DataProcessor.sort_by_amount (propagates error)."""
    mock_instance = mock_data_processor_class.return_value
    mock_instance.sort_by_amount.side_effect = RuntimeError("sort error")

    with pytest.raises(RuntimeError):
        demonstrate_sorting()

    captured = capsys.readouterr().out
    # The heading is printed before the error is raised
    assert "--- Demonstrating Record Sorting ---" in captured


def test_demonstrate_reports_happy_path(
    mock_data_processor_class, mock_report_generator_class, capsys
):
    """Test demonstrate_reports prints all three reports using ReportGenerator."""
    mock_reporter = mock_report_generator_class.return_value
    mock_reporter.generate_summary_report.return_value = "SUMMARY_REPORT"
    mock_reporter.generate_top_products_report.return_value = "TOP_PRODUCTS_REPORT"
    mock_reporter.generate_regional_report.return_value = "REGIONAL_REPORT"

    demonstrate_reports()

    mock_data_processor_class.assert_called_once()
    mock_report_generator_class.assert_called_once_with(
        mock_data_processor_class.return_value
    )
    mock_reporter.generate_summary_report.assert_called_once()
    mock_reporter.generate_top_products_report.assert_called_once_with(3)
    mock_reporter.generate_regional_report.assert_called_once()

    captured = capsys.readouterr().out
    assert "--- Generating Reports ---" in captured
    assert "SUMMARY_REPORT" in captured
    assert "TOP_PRODUCTS_REPORT" in captured
    assert "REGIONAL_REPORT" in captured


def test_demonstrate_reports_report_generator_error(
    mock_data_processor_class, mock_report_generator_class
):
    """Test demonstrate_reports propagates errors thrown by ReportGenerator."""
    mock_reporter = mock_report_generator_class.return_value
    mock_reporter.generate_summary_report.side_effect = ValueError("report error")

    with pytest.raises(ValueError):
        demonstrate_reports()


@pytest.mark.parametrize(
    "profit_args,roi_args,growth_args,break_even_args",
    [
        ((10000, 6000), (15000, 10000), (10000, 15000, 3), (5000, 50, 30)),
    ],
)
def test_demonstrate_calculations_happy_path(
    mock_business_calculator_class,
    capsys,
    profit_args,
    roi_args,
    growth_args,
    break_even_args,
):
    """Test demonstrate_calculations calls BusinessCalculator methods and prints results."""
    mock_business_calculator_class.calculate_profit_margin.return_value = 40.0
    mock_business_calculator_class.calculate_roi.return_value = 50.0
    mock_business_calculator_class.calculate_compound_growth_rate.return_value = 14.47
    mock_business_calculator_class.calculate_break_even_point.return_value = 250.0

    demonstrate_calculations()

    mock_business_calculator_class.calculate_profit_margin.assert_called_once_with(
        *profit_args
    )
    mock_business_calculator_class.calculate_roi.assert_called_once_with(*roi_args)
    mock_business_calculator_class.calculate_compound_growth_rate.assert_called_once_with(
        *growth_args
    )
    mock_business_calculator_class.calculate_break_even_point.assert_called_once_with(
        *break_even_args
    )

    captured = capsys.readouterr().out
    assert "--- Business Calculations ---" in captured
    assert "Profit Margin" in captured
    assert "ROI" in captured
    assert "Compound Growth Rate" in captured
    assert "Break-even Point" in captured


def test_demonstrate_calculations_business_calculator_error(
    mock_business_calculator_class,
):
    """Test demonstrate_calculations propagates errors from BusinessCalculator."""
    mock_business_calculator_class.calculate_profit_margin.side_effect = ZeroDivisionError(
        "division error"
    )

    with pytest.raises(ZeroDivisionError):
        demonstrate_calculations()


def test_demonstrate_parallel_processing_happy_path(
    mock_data_processor_class, mock_format_currency, capsys
):
    """Test demonstrate_parallel_processing filters records and prints them."""
    mock_instance = mock_data_processor_class.return_value
    mock_record1 = Mock(product="ProductA", amount=200.0)
    mock_record2 = Mock(product="ProductB", amount=300.0)
    mock_instance.process_records_parallel.return_value = [mock_record1, mock_record2]

    demonstrate_parallel_processing()

    mock_data_processor_class.assert_called_once()
    mock_instance.process_records_parallel.assert_called_once_with(100)
    assert mock_format_currency.call_count == 2

    captured = capsys.readouterr().out
    assert "--- Parallel Processing Demo ---" in captured
    assert "Found 2 records above $100:" in captured
    assert "ProductA" in captured
    assert "ProductB" in captured


def test_demonstrate_parallel_processing_no_records(
    mock_data_processor_class, mock_format_currency, capsys
):
    """Test demonstrate_parallel_processing when no records are returned."""
    mock_instance = mock_data_processor_class.return_value
    mock_instance.process_records_parallel.return_value = []

    demonstrate_parallel_processing()

    mock_data_processor_class.assert_called_once()
    mock_instance.process_records_parallel.assert_called_once_with(100)
    mock_format_currency.assert_not_called()

    captured = capsys.readouterr().out
    assert "Found 0 records above $100:" in captured


def test_demonstrate_parallel_processing_error(mock_data_processor_class):
    """Test demonstrate_parallel_processing propagates errors from DataProcessor."""
    mock_instance = mock_data_processor_class.return_value
    mock_instance.process_records_parallel.side_effect = RuntimeError("parallel error")

    with pytest.raises(RuntimeError):
        demonstrate_parallel_processing()


def test_main_happy_path(
    mock_data_processor_class,
    mock_report_generator_class,
    mock_business_calculator_class,
    mock_format_currency,
    capsys,
):
    """Test main orchestrates all demonstrations and prints headers/footers."""
    # Configure mocks for called methods to avoid errors
    dp_instance = mock_data_processor_class.return_value
    dp_instance.sort_by_amount.return_value = []
    dp_instance.process_records_parallel.return_value = []

    reporter_instance = mock_report_generator_class.return_value
    reporter_instance.generate_summary_report.return_value = "SUMMARY"
    reporter_instance.generate_top_products_report.return_value = "TOP"
    reporter_instance.generate_regional_report.return_value = "REGION"

    mock_business_calculator_class.calculate_profit_margin.return_value = 40.0
    mock_business_calculator_class.calculate_roi.return_value = 50.0
    mock_business_calculator_class.calculate_compound_growth_rate.return_value = 10.0
    mock_business_calculator_class.calculate_break_even_point.return_value = 100.0

    main()

    captured = capsys.readouterr().out
    assert "BUSINESS ANALYTICS SYSTEM" in captured
    assert "Analysis Complete!" in captured

    # Ensure major components were invoked
    assert mock_data_processor_class.call_count >= 3
    mock_report_generator_class.assert_called_once()
    assert mock_business_calculator_class.calculate_profit_margin.called
    assert mock_business_calculator_class.calculate_roi.called
    assert mock_business_calculator_class.calculate_compound_growth_rate.called
    assert mock_business_calculator_class.calculate_break_even_point.called


def test_main_propagates_error_in_subroutine(
    mock_data_processor_class,
    mock_report_generator_class,
    mock_business_calculator_class,
):
    """Test main propagates an error raised inside one of the demonstration functions."""
    dp_instance = mock_data_processor_class.return_value
    dp_instance.sort_by_amount.side_effect = RuntimeError("sort failure")

    with pytest.raises(RuntimeError):
        main()


@pytest.mark.parametrize(
    "index,expected_product,expected_amount",
    [
        (0, "Laptop", 1200.00),
        (1, "Mouse", 25.00),
        (2, "Keyboard", 75.00),
        (3, "Monitor", 350.00),
        (4, "Laptop", 1150.00),
        (5, "Mouse", 30.00),
        (6, "Headphones", 120.00),
        (7, "Webcam", 80.00),
        (8, "Laptop", 1300.00),
        (9, "Monitor", 400.00),
    ],
)
def test_create_sample_data_parametrized_records(
    sample_records, index, expected_product, expected_amount
):
    """Parametrized test over all sample records for expected product and amount."""
    rec = sample_records[index]
    assert rec.product == expected_product
    assert rec.amount == pytest.approx(expected_amount)