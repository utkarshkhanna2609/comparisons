import pytest
from unittest.mock import Mock, patch

from data_processor import SalesRecord, DataProcessor


@pytest.fixture
def sample_sales_record():
    """Create a sample SalesRecord instance for testing."""
    return SalesRecord(
        record_id=1,
        product="Widget",
        amount=100.5,
        date="2024-01-01",
        region="North",
    )


@pytest.fixture
def multiple_sales_records():
    """Create a list of SalesRecord instances for DataProcessor tests."""
    return [
        SalesRecord(1, "Widget", 100.0, "2024-01-01", "North"),
        SalesRecord(2, "Gadget", 50.0, "2024-01-02", "South"),
        SalesRecord(3, "Widget", 150.0, "2024-01-03", "East"),
        SalesRecord(4, "Thingamajig", 75.0, "2024-01-04", "North"),
        SalesRecord(5, "Gadget", 200.0, "2024-01-05", "West"),
    ]


@pytest.fixture
def data_processor_instance(multiple_sales_records):
    """Create a DataProcessor instance with multiple sales records."""
    return DataProcessor(records=multiple_sales_records)


# --- SalesRecord tests ---


def test_salesrecord_init_valid(sample_sales_record):
    """Test SalesRecord initialization with valid data."""
    record = sample_sales_record
    assert record.record_id == 1
    assert record.product == "Widget"
    assert record.amount == pytest.approx(100.5)
    assert record.date == "2024-01-01"
    assert record.region == "North"


def test_salesrecord_to_dict(sample_sales_record):
    """Test SalesRecord.to_dict returns correct dictionary representation."""
    record = sample_sales_record
    result = record.to_dict()
    assert result == {
        "record_id": 1,
        "product": "Widget",
        "amount": pytest.approx(100.5),
        "date": "2024-01-01",
        "region": "North",
    }


def test_salesrecord_from_dict_uses_v_correctly():
    """Test SalesRecord.from_dict uses utils.v with correct arguments."""
    # Prepare a fake input dict
    input_data = {
        "record_id": 10,
        "product": "Gizmo",
        "amount": 42.3,
        "date": "2024-02-02",
        "region": "South",
    }

    # Mock v so we control its returned values and inspect calls
    with patch("data_processor.v") as mock_v:
        # Configure side effects for successive calls
        mock_v.side_effect = [
            10,  # record_id
            "Gizmo",  # product
            42.3,  # amount
            "2024-02-02",  # date
            "South",  # region
        ]

        record = SalesRecord.from_dict(input_data)

        # Assert v was called with expected args and order
        expected_calls = [
            ((input_data, "record_id", "i"),),
            ((input_data, "product", "s"),),
            ((input_data, "amount", "f"),),
            ((input_data, "date", "s"),),
            ((input_data, "region", "s"),),
        ]
        actual_calls = mock_v.call_args_list
        assert len(actual_calls) == len(expected_calls)
        for actual_call, expected_call in zip(actual_calls, expected_calls):
            assert actual_call[0] == expected_call[0]

        # Assert returned object has attributes from v's return values
        assert isinstance(record, SalesRecord)
        assert record.record_id == 10
        assert record.product == "Gizmo"
        assert record.amount == pytest.approx(42.3)
        assert record.date == "2024-02-02"
        assert record.region == "South"


def test_salesrecord_from_dict_propagates_exception():
    """Test SalesRecord.from_dict propagates exceptions from utils.v."""
    with patch("data_processor.v") as mock_v:
        mock_v.side_effect = ValueError("bad data")

        with pytest.raises(ValueError):
            SalesRecord.from_dict({"record_id": "x"})


# --- DataProcessor tests ---


def test_dataprocessor_init_with_records(multiple_sales_records):
    """Test DataProcessor initialization with a list of records."""
    processor = DataProcessor(records=multiple_sales_records)
    assert processor.records is multiple_sales_records
    assert len(processor.records) == 5


def test_dataprocessor_sort_by_amount_orders_correctly(data_processor_instance):
    """Test DataProcessor.sort_by_amount sorts records ascending by amount."""
    processor = data_processor_instance
    sorted_records = processor.sort_by_amount()
    amounts = [r.amount for r in sorted_records]
    assert amounts == sorted(amounts)


def test_dataprocessor_sort_by_amount_stable_for_equal_amounts():
    """Test DataProcessor.sort_by_amount is stable for records with equal amounts."""
    r1 = SalesRecord(1, "A", 100.0, "2024-01-01", "X")
    r2 = SalesRecord(2, "B", 100.0, "2024-01-02", "Y")
    r3 = SalesRecord(3, "C", 100.0, "2024-01-03", "Z")
    processor = DataProcessor(records=[r1, r2, r3])

    sorted_records = processor.sort_by_amount()

    # Bubble sort as implemented is stable; order should be preserved
    assert [r.record_id for r in sorted_records] == [1, 2, 3]


def test_dataprocessor_sort_by_amount_empty_list():
    """Test DataProcessor.sort_by_amount with no records returns empty list."""
    processor = DataProcessor(records=[])
    assert processor.sort_by_amount() == []


def test_dataprocessor_filter_by_region_matches(data_processor_instance):
    """Test DataProcessor.filter_by_region returns only matching region records."""
    processor = data_processor_instance
    north_records = processor.filter_by_region("North")
    assert all(r.region == "North" for r in north_records)
    assert {r.record_id for r in north_records} == {1, 4}


def test_dataprocessor_filter_by_region_no_matches(data_processor_instance):
    """Test DataProcessor.filter_by_region returns empty list when no matches."""
    processor = data_processor_instance
    records = processor.filter_by_region("NonExistingRegion")
    assert records == []


def test_dataprocessor_filter_by_product_matches(data_processor_instance):
    """Test DataProcessor.filter_by_product returns only matching product records."""
    processor = data_processor_instance
    widget_records = processor.filter_by_product("Widget")
    assert all(r.product == "Widget" for r in widget_records)
    assert {r.record_id for r in widget_records} == {1, 3}


def test_dataprocessor_filter_by_product_no_matches(data_processor_instance):
    """Test DataProcessor.filter_by_product returns empty list when no matches."""
    processor = data_processor_instance
    records = processor.filter_by_product("NonExistingProduct")
    assert records == []


def test_dataprocessor_get_total_sales(data_processor_instance):
    """Test DataProcessor.get_total_sales sums all record amounts."""
    processor = data_processor_instance
    expected_total = sum(r.amount for r in processor.records)
    assert processor.get_total_sales() == pytest.approx(expected_total)


def test_dataprocessor_get_total_sales_empty():
    """Test DataProcessor.get_total_sales with no records returns zero."""
    processor = DataProcessor(records=[])
    assert processor.get_total_sales() == pytest.approx(0.0)


def test_dataprocessor_get_average_sale_non_empty(data_processor_instance):
    """Test DataProcessor.get_average_sale computes correct average."""
    processor = data_processor_instance
    expected_total = sum(r.amount for r in processor.records)
    expected_avg = expected_total / len(processor.records)
    assert processor.get_average_sale() == pytest.approx(expected_avg)


def test_dataprocessor_get_average_sale_empty():
    """Test DataProcessor.get_average_sale returns 0 when there are no records."""
    processor = DataProcessor(records=[])
    assert processor.get_average_sale() == pytest.approx(0.0)


def test_dataprocessor_group_by_region_groups_correctly(data_processor_instance):
    """Test DataProcessor.group_by_region groups records by region."""
    processor = data_processor_instance
    grouped = processor.group_by_region()

    # Expected regions from fixture
    expected_regions = {"North", "South", "East", "West"}
    assert set(grouped.keys()) == expected_regions

    # Check that each record appears in the correct region list
    for region, records in grouped.items():
        assert all(r.region == region for r in records)

    # Ensure total records preserved
    total_grouped = sum(len(v) for v in grouped.values())
    assert total_grouped == len(processor.records)


def test_dataprocessor_get_top_products_default_limit(data_processor_instance):
    """Test DataProcessor.get_top_products returns top 5 or fewer products by total sales."""
    processor = data_processor_instance
    top_products = processor.get_top_products()

    # Manually calculate expected product totals
    totals = {}
    for r in processor.records:
        totals.setdefault(r.product, 0)
        totals[r.product] += r.amount

    # Sort manually
    expected_sorted = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    expected_limited = expected_sorted[:5]

    assert len(top_products) == len(expected_limited)
    assert top_products == expected_limited


def test_dataprocessor_get_top_products_custom_limit(data_processor_instance):
    """Test DataProcessor.get_top_products respects custom limit."""
    processor = data_processor_instance
    top_two = processor.get_top_products(limit=2)

    totals = {}
    for r in processor.records:
        totals.setdefault(r.product, 0)
        totals[r.product] += r.amount

    expected_two = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:2]
    assert top_two == expected_two
    assert len(top_two) == 2


def test_dataprocessor_get_top_products_limit_exceeds_products(data_processor_instance):
    """Test DataProcessor.get_top_products when limit exceeds number of products."""
    processor = data_processor_instance
    # There are only a few unique products in fixture
    totals = {r.product for r in processor.records}
    over_limit = len(totals) + 10

    top_products = processor.get_top_products(limit=over_limit)
    assert len(top_products) == len(totals)


def test_dataprocessor_process_records_parallel_threshold_filtering(multiple_sales_records):
    """Test DataProcessor.process_records_parallel returns records above threshold."""
    processor = DataProcessor(records=multiple_sales_records)
    threshold = 100.0

    results = processor.process_records_parallel(threshold)

    # All results should have amount > threshold
    assert all(r.amount > threshold for r in results)

    # Check which records are expected
    expected_ids = {r.record_id for r in multiple_sales_records if r.amount > threshold}
    result_ids = {r.record_id for r in results}
    assert result_ids == expected_ids


def test_dataprocessor_process_records_parallel_with_few_records():
    """Test DataProcessor.process_records_parallel when records < 4 uses chunk_size 1."""
    records = [
        SalesRecord(1, "A", 10.0, "2024-01-01", "X"),
        SalesRecord(2, "B", 20.0, "2024-01-02", "Y"),
    ]
    processor = DataProcessor(records=records)
    threshold = 15.0

    results = processor.process_records_parallel(threshold)
    expected_ids = {2}
    assert {r.record_id for r in results} == expected_ids


def test_dataprocessor_process_records_parallel_no_records():
    """Test DataProcessor.process_records_parallel with no records returns empty list."""
    processor = DataProcessor(records=[])
    results = processor.process_records_parallel(threshold=50.0)
    assert results == []


def test_dataprocessor_process_records_parallel_threading_called(multiple_sales_records):
    """Test DataProcessor.process_records_parallel creates threads as expected."""
    processor = DataProcessor(records=multiple_sales_records)

    # Patch threading.Thread to ensure it's called expected number of times
    with patch("data_processor.threading.Thread") as mock_thread_cls:
        mock_thread_instance = Mock()
        mock_thread_cls.return_value = mock_thread_instance

        processor.process_records_parallel(threshold=0.0)

        # chunk_size will be len(records)//4 = 5//4 = 1, so one record per thread
        expected_thread_count = len(multiple_sales_records)
        assert mock_thread_cls.call_count == expected_thread_count
        assert mock_thread_instance.start.call_count == expected_thread_count
        assert mock_thread_instance.join.call_count == expected_thread_count
