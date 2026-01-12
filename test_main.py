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
def mock_data_processor():
    """Fixture providing a mocked DataProcessor class."""
    with patch("main.DataProcessor") as mock_cls:
        yield mock_cls


@pytest.fixture
def mock_report_generator():
    """Fixture providing a mocked ReportGenerator class."""
    with patch("main.ReportGenerator") as mock_cls:
        yield mock_cls


@pytest.fixture
def mock_business_calculator():
    """Fixture providing a mocked BusinessCalculator class."""
    with patch("main.BusinessCalculator") as mock_cls:
        yield mock_cls


@pytest.fixture
def mock_format_currency():
    """Fixture providing a mocked format_currency function."""
    with patch("main.format_currency") as mock_func:
        yield mock_func


@pytest.fixture
def capture_stdout(monkeypatch):
    """Fixture to capture printed output from functions using print."""
    from io import StringIO

    buffer = StringIO()
    monkeypatch.setattr("sys.stdout", buffer)
    return buffer


def test_create_sample_data_structure(sample_records):
    """Test that create_sample_data returns a non-empty list of SalesRecord instances."""
    assert isinstance(sample_records, list)
    assert len(sample_records) == 10
    # We cannot import SalesRecord directly here, but we can check attributes
    first = sample_records[0]
    assert hasattr(first, "id")
    assert hasattr(first, "product")
    assert hasattr(first, "amount")
    assert hasattr(first, "date")
    assert hasattr(first, "region")


@pytest.mark.parametrize(
    "index,expected_product,expected_amount",
    [
        (0, "Laptop", 1200.00),
        (1, "Mouse", 25.00),
        (9, "Monitor", 400.00),
    ],
)
def test_create_sample_data_contents(index, expected_product, expected_amount):
    """Test that specific records in create_sample_data have expected values."""
    records = create_sample_data()
    record = records[index]
    assert record.product == expected_product
    assert record.amount == pytest.approx(expected_amount)


def test_demonstrate_sorting_happy_path(
    mock_data_processor, mock_format_currency, capture_stdout
):
    """Test demonstrate_sorting prints sorted records using DataProcessor and format_currency."""
    # Arrange
    mock_instance = mock_data_processor.return_value
    # Create fake records with product and amount attributes
    FakeRecord = type("FakeRecord", (), {})
    fake_records = []
    for i in range(5):
        r = FakeRecord()
        r.product = f"Product{i}"
        r.amount = 100 + i
        fake_records.append(r)
    mock_instance.sort_by_amount.return_value = fake_records
    mock_format_currency.side_effect = lambda x: f"${x:.2f}"

    # Act
    demonstrate_sorting()

    # Assert DataProcessor was instantiated with sample data
    mock_data_processor.assert_called_once()
    mock_instance.sort_by_amount.assert_called_once()

    output = capture_stdout.getvalue()
    assert "--- Demonstrating Record Sorting ---" in output
    assert "Records sorted by amount:" in output
    for i in range(5):
        assert f"Product{i}: ${100 + i:.2f}" in output


def test_demonstrate_sorting_error_in_sorting(
    mock_data_processor, mock_format_currency, capture_stdout
):
    """Test demonstrate_sorting handles an exception from sort_by_amount by propagating it."""
    mock_instance = mock_data_processor.return_value
    mock_instance.sort_by_amount.side_effect = RuntimeError("sort failed")

    with pytest.raises(RuntimeError):
        demonstrate_sorting()


def test_demonstrate_reports_happy_path(
    mock_data_processor, mock_report_generator, capture_stdout
):
    """Test demonstrate_reports uses ReportGenerator to print three reports."""
    mock_dp_instance = mock_data_processor.return_value
    mock_rg_instance = mock_report_generator.return_value

    mock_rg_instance.generate_summary_report.return_value = "SUMMARY REPORT"
    mock_rg_instance.generate_top_products_report.return_value = "TOP PRODUCTS"
    mock_rg_instance.generate_regional_report.return_value = "REGIONAL REPORT"

    demonstrate_reports()

    mock_data_processor.assert_called_once()
    mock_report_generator.assert_called_once_with(mock_dp_instance)

    mock_rg_instance.generate_summary_report.assert_called_once()
    mock_rg_instance.generate_top_products_report.assert_called_once_with(3)
    mock_rg_instance.generate_regional_report.assert_called_once()

    output = capture_stdout.getvalue()
    assert "--- Generating Reports ---" in output
    assert "SUMMARY REPORT" in output
    assert "TOP PRODUCTS" in output
    assert "REGIONAL REPORT" in output


def test_demonstrate_reports_error_in_report_generation(
    mock_data_processor, mock_report_generator
):
    """Test demonstrate_reports propagates exceptions from ReportGenerator methods."""
    mock_rg_instance = mock_report_generator.return_value
    mock_rg_instance.generate_summary_report.side_effect = ValueError("bad data")

    with pytest.raises(ValueError):
        demonstrate_reports()


def test_demonstrate_calculations_happy_path(
    mock_business_calculator, capture_stdout
):
    """Test demonstrate_calculations calls BusinessCalculator methods and prints results."""
    mock_business_calculator.calculate_profit_margin.return_value = 40.0
    mock_business_calculator.calculate_roi.return_value = 50.0
    mock_business_calculator.calculate_compound_growth_rate.return_value = 14.47
    mock_business_calculator.calculate_break_even_point.return_value = 250.0

    demonstrate_calculations()

    # Assert calls with correct arguments
    mock_business_calculator.calculate_profit_margin.assert_called_once_with(
        10000, 6000
    )
    mock_business_calculator.calculate_roi.assert_called_once_with(15000, 10000)
    mock_business_calculator.calculate_compound_growth_rate.assert_called_once_with(
        10000, 15000, 3
    )
    mock_business_calculator.calculate_break_even_point.assert_called_once_with(
        5000, 50, 30
    )

    output = capture_stdout.getvalue()
    assert "--- Business Calculations ---" in output
    assert "Profit Margin" in output
    assert "ROI" in output
    assert "Compound Growth Rate" in output
    assert "Break-even Point" in output


@pytest.mark.parametrize(
    "method_name,exc",
    [
        ("calculate_profit_margin", ZeroDivisionError),
        ("calculate_roi", ValueError),
        ("calculate_compound_growth_rate", ArithmeticError),
        ("calculate_break_even_point", RuntimeError),
    ],
)
def test_demonstrate_calculations_error_cases(
    mock_business_calculator, method_name, exc
):
    """Test demonstrate_calculations propagates exceptions from BusinessCalculator methods."""
    getattr(mock_business_calculator, method_name).side_effect = exc("boom")

    with pytest.raises(exc):
        demonstrate_calculations()


def test_demonstrate_parallel_processing_happy_path(
    mock_data_processor, mock_format_currency, capture_stdout
):
    """Test demonstrate_parallel_processing filters high value records and prints them."""
    mock_instance = mock_data_processor.return_value

    FakeRecord = type("FakeRecord", (), {})
    r1 = FakeRecord()
    r1.product = "High1"
    r1.amount = 150.0
    r2 = FakeRecord()
    r2.product = "High2"
    r2.amount = 200.0
    mock_instance.process_records_parallel.return_value = [r1, r2]

    mock_format_currency.side_effect = lambda x: f"${x:.2f}"

    demonstrate_parallel_processing()

    mock_data_processor.assert_called_once()
    mock_instance.process_records_parallel.assert_called_once_with(100)

    output = capture_stdout.getvalue()
    assert "--- Parallel Processing Demo ---" in output
    assert "Found 2 records above $100:" in output
    assert "High1: $150.00" in output
    assert "High2: $200.00" in output


def test_demonstrate_parallel_processing_error(
    mock_data_processor, mock_format_currency
):
    """Test demonstrate_parallel_processing propagates exceptions from process_records_parallel."""
    mock_instance = mock_data_processor.return_value
    mock_instance.process_records_parallel.side_effect = RuntimeError("parallel fail")

    with pytest.raises(RuntimeError):
        demonstrate_parallel_processing()


def test_main_happy_path(
    mock_data_processor,
    mock_report_generator,
    mock_business_calculator,
    mock_format_currency,
    capture_stdout,
):
    """Test main orchestrates all demonstrations and prints headers and footers."""
    # Configure mocks minimally so that all called functions succeed
    # DataProcessor instances for sorting and parallel processing
    dp_instance = mock_data_processor.return_value

    # sort_by_amount returns empty list to simplify
    dp_instance.sort_by_amount.return_value = []

    # process_records_parallel returns empty list
    dp_instance.process_records_parallel.return_value = []

    # ReportGenerator instance methods
    rg_instance = mock_report_generator.return_value
    rg_instance.generate_summary_report.return_value = "SUMMARY"
    rg_instance.generate_top_products_report.return_value = "TOP"
    rg_instance.generate_regional_report.return_value = "REGIONAL"

    # BusinessCalculator methods
    mock_business_calculator.calculate_profit_margin.return_value = 40.0
    mock_business_calculator.calculate_roi.return_value = 50.0
    mock_business_calculator.calculate_compound_growth_rate.return_value = 10.0
    mock_business_calculator.calculate_break_even_point.return_value = 100.0

    mock_format_currency.side_effect = lambda x: f"${x:.2f}"

    main()

    output = capture_stdout.getvalue()
    assert "BUSINESS ANALYTICS SYSTEM" in output
    assert "Analysis Complete!" in output
    assert "--- Demonstrating Record Sorting ---" in output
    assert "--- Generating Reports ---" in output
    assert "--- Business Calculations ---" in output
    assert "--- Parallel Processing Demo ---" in output


def test_main_error_in_demonstrate_sorting(
    mock_data_processor,
    mock_report_generator,
    mock_business_calculator,
    mock_format_currency,
):
    """Test main propagates exceptions raised during demonstrate_sorting."""
    dp_instance = mock_data_processor.return_value
    dp_instance.sort_by_amount.side_effect = RuntimeError("sort error")

    with pytest.raises(RuntimeError):
        main()