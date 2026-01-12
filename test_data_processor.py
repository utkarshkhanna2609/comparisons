import pytest
from unittest.mock import patch, MagicMock
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
        SalesRecord(2, "Gadget", 200.0, "2024-01-02", "South"),
        SalesRecord(3, "Widget", 50.0, "2024-01-03", "North"),
        SalesRecord(4, "Thing", 150.0, "2024-01-04", "East"),
        SalesRecord(5, "Gadget", 300.0, "2024-01-05", "West"),
    ]


@pytest.fixture
def data_processor_instance(multiple_sales_records):
    """Create a DataProcessor instance with multiple records."""
    return DataProcessor(records=multiple_sales_records)


# -------------------- SalesRecord tests --------------------


def test_salesrecord_init_valid(sample_sales_record):
    """Test SalesRecord initialization with valid data."""
    assert sample_sales_record.record_id == 1
    assert sample_sales_record.product == "Widget"
    assert sample_sales_record.amount == pytest.approx(100.5)
    assert sample_sales_record.date == "2024-01-01"
    assert sample_sales_record.region == "North"


def test_salesrecord_to_dict(sample_sales_record):
    """Test SalesRecord.to_dict returns correct dictionary."""
    result = sample_sales_record.to_dict()
    expected = {
        "record_id": 1,
        "product": "Widget",
        "amount": 100.5,
        "date": "2024-01-01",
        "region": "North",
    }
    assert result["record_id"] == expected["record_id"]
    assert result["product"] == expected["product"]
    assert result["amount"] == pytest.approx(expected["amount"])
    assert result["date"] == expected["date"]
    assert result["region"] == expected["region"]


def test_salesrecord_from_dict_uses_utils_v_correctly():
    """Test SalesRecord.from_dict uses utils.v for each field and constructs object."""
    data = {
        "record_id": 10,
        "product": "Gizmo",
        "amount": 250.75,
        "date": "2024-02-01",
        "region": "South",
    }

    with patch("data_processor.v") as mock_v:
        # Configure side effects to return values in order of calls
        mock_v.side_effect = [
            data["record_id"],
            data["product"],
            data["amount"],
            data["date"],
            data["region"],
        ]

        record = SalesRecord.from_dict(data)

        # Assert v was called with correct arguments
        expected_calls = [
            ((data, "record_id", "i"),),
            ((data, "product", "s"),),
            ((data, "amount", "f"),),
            ((data, "date", "s"),),
            ((data, "region", "s"),),
        ]
        actual_calls = mock_v.call_args_list
        assert len(actual_calls) == len(expected_calls)
        for actual, expected in zip(actual_calls, expected_calls):
            assert actual[0] == expected[0]

        # Assert record fields are set from v's return values
        assert record.record_id == data["record_id"]
        assert record.product == data["product"]
        assert record.amount == pytest.approx(data["amount"])
        assert record.date == data["date"]
        assert record.region == data["region"]


def test_salesrecord_from_dict_raises_when_v_raises():
    """Test SalesRecord.from_dict propagates exceptions from utils.v."""
    data = {"record_id": "bad"}

    with patch("data_processor.v") as mock_v:
        mock_v.side_effect = ValueError("invalid value")
        with pytest.raises(ValueError):
            SalesRecord.from_dict(data)


# -------------------- DataProcessor tests --------------------


def test_dataprocessor_init_with_records(multiple_sales_records):
    """Test DataProcessor initialization stores records list."""
    processor = DataProcessor(records=multiple_sales_records)
    assert processor.records is multiple_sales_records
    assert len(processor.records) == 5


def test_dataprocessor_sort_by_amount_sorted_correctly(data_processor_instance):
    """Test DataProcessor.sort_by_amount sorts records by amount ascending."""
    sorted_records = data_processor_instance.sort_by_amount()
    amounts = [r.amount for r in sorted_records]
    assert amounts == sorted(amounts)


def test_dataprocessor_sort_by_amount_does_not_modify_original(data_processor_instance):
    """Test DataProcessor.sort_by_amount does not mutate original records list."""
    original_amounts = [r.amount for r in data_processor_instance.records]
    _ = data_processor_instance.sort_by_amount()
    new_amounts = [r.amount for r in data_processor_instance.records]
    assert new_amounts == original_amounts


def test_dataprocessor_sort_by_amount_empty_list():
    """Test DataProcessor.sort_by_amount with empty records list."""
    processor = DataProcessor(records=[])
    sorted_records = processor.sort_by_amount()
    assert sorted_records == []


def test_dataprocessor_filter_by_region_matches(data_processor_instance):
    """Test DataProcessor.filter_by_region returns only matching region records."""
    north_records = data_processor_instance.filter_by_region("North")
    assert len(north_records) == 2
    assert all(r.region == "North" for r in north_records)


def test_dataprocessor_filter_by_region_no_matches(data_processor_instance):
    """Test DataProcessor.filter_by_region returns empty list when no matches."""
    records = data_processor_instance.filter_by_region("Nonexistent")
    assert records == []


def test_dataprocessor_filter_by_product_matches(data_processor_instance):
    """Test DataProcessor.filter_by_product returns only matching product records."""
    widget_records = data_processor_instance.filter_by_product("Widget")
    assert len(widget_records) == 2
    assert all(r.product == "Widget" for r in widget_records)


def test_dataprocessor_filter_by_product_no_matches(data_processor_instance):
    """Test DataProcessor.filter_by_product returns empty list when no matches."""
    records = data_processor_instance.filter_by_product("NonexistentProduct")
    assert records == []


def test_dataprocessor_get_total_sales_correct_sum(data_processor_instance):
    """Test DataProcessor.get_total_sales returns correct sum of amounts."""
    total = data_processor_instance.get_total_sales()
    expected = sum(r.amount for r in data_processor_instance.records)
    assert total == pytest.approx(expected)


def test_dataprocessor_get_total_sales_empty():
    """Test DataProcessor.get_total_sales returns 0 for empty records."""
    processor = DataProcessor(records=[])
    total = processor.get_total_sales()
    assert total == pytest.approx(0.0)


def test_dataprocessor_get_average_sale_non_empty(data_processor_instance):
    """Test DataProcessor.get_average_sale returns correct average for non-empty list."""
    avg = data_processor_instance.get_average_sale()
    expected = sum(r.amount for r in data_processor_instance.records) / len(
        data_processor_instance.records
    )
    assert avg == pytest.approx(expected)


def test_dataprocessor_get_average_sale_empty():
    """Test DataProcessor.get_average_sale returns 0 for empty records."""
    processor = DataProcessor(records=[])
    avg = processor.get_average_sale()
    assert avg == pytest.approx(0.0)


def test_dataprocessor_group_by_region_groups_correctly(data_processor_instance):
    """Test DataProcessor.group_by_region groups records by region."""
    grouped = data_processor_instance.group_by_region()
    # Expected regions from fixture: North(2), South(1), East(1), West(1)
    assert set(grouped.keys()) == {"North", "South", "East", "West"}
    assert len(grouped["North"]) == 2
    assert all(r.region == "North" for r in grouped["North"])
    assert len(grouped["South"]) == 1
    assert len(grouped["East"]) == 1
    assert len(grouped["West"]) == 1


def test_dataprocessor_group_by_region_empty():
    """Test DataProcessor.group_by_region with empty records returns empty dict."""
    processor = DataProcessor(records=[])
    grouped = processor.group_by_region()
    assert grouped == {}


def test_dataprocessor_get_top_products_default_limit(data_processor_instance):
    """Test DataProcessor.get_top_products returns top 5 (or fewer) products by sales."""
    top_products = data_processor_instance.get_top_products()
    # Compute expected totals
    totals = {}
    for r in data_processor_instance.records:
        totals[r.product] = totals.get(r.product, 0) + r.amount
    expected_sorted = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    expected = expected_sorted[:5]
    assert len(top_products) == len(expected)
    for (prod, amt), (exp_prod, exp_amt) in zip(top_products, expected):
        assert prod == exp_prod
        assert amt == pytest.approx(exp_amt)


def test_dataprocessor_get_top_products_custom_limit(data_processor_instance):
    """Test DataProcessor.get_top_products respects custom limit."""
    top_two = data_processor_instance.get_top_products(limit=2)
    assert len(top_two) == 2


def test_dataprocessor_get_top_products_limit_exceeds_unique_products(data_processor_instance):
    """Test DataProcessor.get_top_products when limit exceeds number of unique products."""
    totals = {}
    for r in data_processor_instance.records:
        totals[r.product] = totals.get(r.product, 0) + r.amount
    unique_count = len(totals)
    top = data_processor_instance.get_top_products(limit=10)
    assert len(top) == unique_count


def test_dataprocessor_get_top_products_empty():
    """Test DataProcessor.get_top_products returns empty list for no records."""
    processor = DataProcessor(records=[])
    top = processor.get_top_products()
    assert top == []


def test_dataprocessor_process_records_parallel_threshold_filtering(multiple_sales_records):
    """Test DataProcessor.process_records_parallel filters records above threshold."""
    processor = DataProcessor(records=multiple_sales_records)
    threshold = 150.0
    results = processor.process_records_parallel(threshold)
    assert all(r.amount > threshold for r in results)
    expected = [r for r in multiple_sales_records if r.amount > threshold]
    assert sorted([r.record_id for r in results]) == sorted(
        [r.record_id for r in expected]
    )


def test_dataprocessor_process_records_parallel_includes_equal_threshold(multiple_sales_records):
    """Test DataProcessor.process_records_parallel excludes records equal to threshold."""
    processor = DataProcessor(records=multiple_sales_records)
    threshold = 200.0
    results = processor.process_records_parallel(threshold)
    # Only amounts strictly greater than threshold
    assert all(r.amount > threshold for r in results)
    assert all(r.amount != threshold for r in results)


def test_dataprocessor_process_records_parallel_empty_records():
    """Test DataProcessor.process_records_parallel with empty records returns empty list."""
    processor = DataProcessor(records=[])
    results = processor.process_records_parallel(threshold=100.0)
    assert results == []


def test_dataprocessor_process_records_parallel_small_number_of_records():
    """Test DataProcessor.process_records_parallel when records < 4 uses chunk_size 1."""
    records = [
        SalesRecord(1, "A", 10.0, "2024-01-01", "X"),
        SalesRecord(2, "B", 20.0, "2024-01-02", "Y"),
        SalesRecord(3, "C", 30.0, "2024-01-03", "Z"),
    ]
    processor = DataProcessor(records=records)
    results = processor.process_records_parallel(threshold=15.0)
    expected_ids = [2, 3]
    assert sorted([r.record_id for r in results]) == expected_ids


def test_dataprocessor_process_records_parallel_threading_called(multiple_sales_records):
    """Test DataProcessor.process_records_parallel creates and starts threads."""
    processor = DataProcessor(records=multiple_sales_records)

    with patch("data_processor.threading.Thread") as mock_thread_cls:
        mock_thread_instance = MagicMock()
        mock_thread_cls.return_value = mock_thread_instance

        _ = processor.process_records_parallel(threshold=100.0)

        # Ensure Thread was instantiated at least once and start/join called
        assert mock_thread_cls.call_count >= 1
        assert mock_thread_instance.start.call_count == mock_thread_cls.call_count
        assert mock_thread_instance.join.call_count == mock_thread_cls.call_count