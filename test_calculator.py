import math
import pytest
from unittest.mock import patch

from calculator import BusinessCalculator


@pytest.fixture
def business_calculator():
    """Fixture to provide BusinessCalculator class reference (static methods)."""
    return BusinessCalculator


def test_businesscalculator_initialization():
    """Test that BusinessCalculator can be instantiated without errors."""
    instance = BusinessCalculator()
    assert isinstance(instance, BusinessCalculator)


def test_businesscalculator_calculate_profit_margin_basic(business_calculator):
    """Test calculate_profit_margin with typical positive revenue and costs."""
    result = business_calculator.calculate_profit_margin(1000, 400)
    expected = ((1000 - 400) / 1000) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_profit_margin_zero_revenue(business_calculator):
    """Test calculate_profit_margin returns 0 when revenue is zero."""
    result = business_calculator.calculate_profit_margin(0, 400)
    assert result == 0


def test_businesscalculator_calculate_profit_margin_negative_profit(business_calculator):
    """Test calculate_profit_margin when costs exceed revenue (negative margin)."""
    result = business_calculator.calculate_profit_margin(500, 800)
    expected = ((500 - 800) / 500) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_profit_margin_negative_values(business_calculator):
    """Test calculate_profit_margin with negative revenue and costs."""
    result = business_calculator.calculate_profit_margin(-1000, -400)
    expected = ((-1000 - -400) / -1000) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_roi_basic(business_calculator):
    """Test calculate_roi with typical gain and cost."""
    result = business_calculator.calculate_roi(1500, 1000)
    expected = ((1500 - 1000) / 1000) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_roi_zero_cost(business_calculator):
    """Test calculate_roi returns 0 when cost is zero."""
    result = business_calculator.calculate_roi(1500, 0)
    assert result == 0


def test_businesscalculator_calculate_roi_negative_gain(business_calculator):
    """Test calculate_roi with negative gain."""
    result = business_calculator.calculate_roi(-500, 1000)
    expected = ((-500 - 1000) / 1000) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_compound_growth_rate_basic(business_calculator):
    """Test calculate_compound_growth_rate with valid positive values."""
    result = business_calculator.calculate_compound_growth_rate(1000, 2000, 4)
    total_growth = (2000 - 1000) / 1000
    expected = (total_growth / 4) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_compound_growth_rate_zero_starting_value(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when starting_value is zero."""
    result = business_calculator.calculate_compound_growth_rate(0, 2000, 4)
    assert result == 0


def test_businesscalculator_calculate_compound_growth_rate_negative_starting_value(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when starting_value is negative."""
    result = business_calculator.calculate_compound_growth_rate(-1000, 2000, 4)
    assert result == 0


def test_businesscalculator_calculate_compound_growth_rate_zero_periods(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when periods is zero."""
    result = business_calculator.calculate_compound_growth_rate(1000, 2000, 0)
    assert result == 0


def test_businesscalculator_calculate_compound_growth_rate_negative_periods(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when periods is negative."""
    result = business_calculator.calculate_compound_growth_rate(1000, 2000, -3)
    assert result == 0


def test_businesscalculator_calculate_compound_growth_rate_decreasing_value(business_calculator):
    """Test calculate_compound_growth_rate when ending_value is less than starting_value."""
    result = business_calculator.calculate_compound_growth_rate(2000, 1000, 4)
    total_growth = (1000 - 2000) / 2000
    expected = (total_growth / 4) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_break_even_point_basic(business_calculator):
    """Test calculate_break_even_point with valid positive values."""
    result = business_calculator.calculate_break_even_point(10000, 50, 30)
    contribution_margin = 50 - 30
    expected = 10000 / contribution_margin
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_break_even_point_zero_contribution_margin(business_calculator):
    """Test calculate_break_even_point returns None when contribution margin is zero."""
    result = business_calculator.calculate_break_even_point(10000, 30, 30)
    assert result is None


def test_businesscalculator_calculate_break_even_point_negative_contribution_margin(business_calculator):
    """Test calculate_break_even_point returns None when contribution margin is negative."""
    result = business_calculator.calculate_break_even_point(10000, 20, 30)
    assert result is None


def test_businesscalculator_calculate_break_even_point_zero_fixed_costs(business_calculator):
    """Test calculate_break_even_point with zero fixed costs."""
    result = business_calculator.calculate_break_even_point(0, 50, 30)
    contribution_margin = 50 - 30
    expected = 0 / contribution_margin
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_discount_price_basic(business_calculator):
    """Test calculate_discount_price with typical values."""
    result = business_calculator.calculate_discount_price(200, 25)
    discount_amount = 200 * (25 / 100)
    expected = 200 - discount_amount
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_discount_price_zero_discount(business_calculator):
    """Test calculate_discount_price with zero discount percentage."""
    result = business_calculator.calculate_discount_price(200, 0)
    assert result == pytest.approx(200)


def test_businesscalculator_calculate_discount_price_full_discount(business_calculator):
    """Test calculate_discount_price with 100 percent discount."""
    result = business_calculator.calculate_discount_price(200, 100)
    assert result == pytest.approx(0)


def test_businesscalculator_calculate_discount_price_negative_discount(business_calculator):
    """Test calculate_discount_price with negative discount percentage (price increases)."""
    result = business_calculator.calculate_discount_price(200, -10)
    discount_amount = 200 * (-10 / 100)
    expected = 200 - discount_amount
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_tax_amount_basic(business_calculator):
    """Test calculate_tax_amount with typical values."""
    result = business_calculator.calculate_tax_amount(1000, 15)
    expected = 1000 * (15 / 100)
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_tax_amount_zero_tax_rate(business_calculator):
    """Test calculate_tax_amount with zero tax rate."""
    result = business_calculator.calculate_tax_amount(1000, 0)
    assert result == pytest.approx(0)


def test_businesscalculator_calculate_tax_amount_negative_tax_rate(business_calculator):
    """Test calculate_tax_amount with negative tax rate."""
    result = business_calculator.calculate_tax_amount(1000, -5)
    expected = 1000 * (-5 / 100)
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_net_present_value_basic(business_calculator):
    """Test calculate_net_present_value with typical cash flows and discount rate."""
    cash_flows = [1000, 2000, 3000]
    discount_rate = 0.1
    expected = 0
    for period, cash_flow in enumerate(cash_flows):
        expected += cash_flow / math.pow(1 + discount_rate, period)
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_net_present_value_zero_discount_rate(business_calculator):
    """Test calculate_net_present_value with zero discount rate."""
    cash_flows = [100, 200, 300]
    discount_rate = 0.0
    expected = sum(cash_flows)  # since (1 + 0)^period = 1
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_net_present_value_empty_cash_flows(business_calculator):
    """Test calculate_net_present_value with empty cash flows list."""
    cash_flows = []
    discount_rate = 0.1
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)
    assert result == pytest.approx(0)


def test_businesscalculator_calculate_net_present_value_negative_cash_flows(business_calculator):
    """Test calculate_net_present_value with negative cash flows."""
    cash_flows = [-1000, -500, 2000]
    discount_rate = 0.05
    expected = 0
    for period, cash_flow in enumerate(cash_flows):
        expected += cash_flow / math.pow(1 + discount_rate, period)
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_net_present_value_uses_math_pow(business_calculator):
    """Test calculate_net_present_value uses math.pow for discounting."""
    cash_flows = [100, 200]
    discount_rate = 0.1
    with patch("calculator.math.pow") as mock_pow:
        mock_pow.side_effect = math.pow
        result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)
        assert mock_pow.call_count == len(cash_flows)
        assert result == pytest.approx(
            100 / math.pow(1 + discount_rate, 0)
            + 200 / math.pow(1 + discount_rate, 1)
        )


def test_businesscalculator_calculate_net_present_value_invalid_discount_rate_raises(business_calculator):
    """Test calculate_net_present_value raises ValueError when discount_rate is -1 (division by zero)."""
    cash_flows = [100, 200]
    discount_rate = -1.0
    with pytest.raises(ZeroDivisionError):
        business_calculator.calculate_net_present_value(cash_flows, discount_rate)


def test_businesscalculator_calculate_markup_percentage_basic(business_calculator):
    """Test calculate_markup_percentage with typical cost and selling price."""
    result = business_calculator.calculate_markup_percentage(100, 150)
    expected = ((150 - 100) / 100) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_markup_percentage_zero_cost(business_calculator):
    """Test calculate_markup_percentage returns 0 when cost is zero."""
    result = business_calculator.calculate_markup_percentage(0, 150)
    assert result == 0


def test_businesscalculator_calculate_markup_percentage_negative_markup(business_calculator):
    """Test calculate_markup_percentage when selling price is less than cost."""
    result = business_calculator.calculate_markup_percentage(200, 150)
    expected = ((150 - 200) / 200) * 100
    assert result == pytest.approx(expected)


def test_businesscalculator_calculate_markup_percentage_negative_values(business_calculator):
    """Test calculate_markup_percentage with negative cost and selling price."""
    result = business_calculator.calculate_markup_percentage(-100, -50)
    expected = ((-50 - -100) / -100) * 100
    assert result == pytest.approx(expected)