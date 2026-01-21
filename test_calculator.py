import math
import pytest
from unittest.mock import patch

from calculator import BusinessCalculator


@pytest.fixture
def business_calculator():
    """Fixture to provide BusinessCalculator class reference"""
    return BusinessCalculator


def test_business_calculator_class_exists(business_calculator):
    """Test BusinessCalculator class is defined"""
    assert business_calculator is not None
    assert isinstance(business_calculator, type)


def test_business_calculator_calculate_profit_margin_normal(business_calculator):
    """Test calculate_profit_margin with normal positive revenue and costs"""
    result = business_calculator.calculate_profit_margin(1000, 400)
    expected = ((1000 - 400) / 1000) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_profit_margin_zero_revenue(business_calculator):
    """Test calculate_profit_margin returns 0 when revenue is zero"""
    result = business_calculator.calculate_profit_margin(0, 400)
    assert result == 0


def test_business_calculator_calculate_profit_margin_negative_costs(business_calculator):
    """Test calculate_profit_margin with negative costs"""
    result = business_calculator.calculate_profit_margin(1000, -200)
    expected = ((1000 - (-200)) / 1000) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_profit_margin_negative_revenue(business_calculator):
    """Test calculate_profit_margin with negative revenue"""
    result = business_calculator.calculate_profit_margin(-1000, 400)
    expected = ((-1000 - 400) / -1000) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_roi_normal(business_calculator):
    """Test calculate_roi with normal gain and cost"""
    result = business_calculator.calculate_roi(1500, 1000)
    expected = ((1500 - 1000) / 1000) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_roi_zero_cost(business_calculator):
    """Test calculate_roi returns 0 when cost is zero"""
    result = business_calculator.calculate_roi(1500, 0)
    assert result == 0


def test_business_calculator_calculate_roi_negative_cost(business_calculator):
    """Test calculate_roi with negative cost"""
    result = business_calculator.calculate_roi(1500, -1000)
    expected = ((1500 - -1000) / -1000) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_compound_growth_rate_normal(business_calculator):
    """Test calculate_compound_growth_rate with normal positive values"""
    result = business_calculator.calculate_compound_growth_rate(1000, 2000, 4)
    total_growth = (2000 - 1000) / 1000
    expected = (total_growth / 4) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_compound_growth_rate_zero_starting_value(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when starting_value is zero"""
    result = business_calculator.calculate_compound_growth_rate(0, 2000, 4)
    assert result == 0


def test_business_calculator_calculate_compound_growth_rate_negative_starting_value(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when starting_value is negative"""
    result = business_calculator.calculate_compound_growth_rate(-1000, 2000, 4)
    assert result == 0


def test_business_calculator_calculate_compound_growth_rate_zero_periods(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when periods is zero"""
    result = business_calculator.calculate_compound_growth_rate(1000, 2000, 0)
    assert result == 0


def test_business_calculator_calculate_compound_growth_rate_negative_periods(business_calculator):
    """Test calculate_compound_growth_rate returns 0 when periods is negative"""
    result = business_calculator.calculate_compound_growth_rate(1000, 2000, -3)
    assert result == 0


def test_business_calculator_calculate_compound_growth_rate_decreasing_value(business_calculator):
    """Test calculate_compound_growth_rate when ending_value is less than starting_value"""
    result = business_calculator.calculate_compound_growth_rate(2000, 1000, 4)
    total_growth = (1000 - 2000) / 2000
    expected = (total_growth / 4) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_break_even_point_normal(business_calculator):
    """Test calculate_break_even_point with positive contribution margin"""
    result = business_calculator.calculate_break_even_point(10000, 50, 30)
    contribution_margin = 50 - 30
    expected = 10000 / contribution_margin
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_break_even_point_zero_contribution_margin(business_calculator):
    """Test calculate_break_even_point returns None when contribution margin is zero"""
    result = business_calculator.calculate_break_even_point(10000, 50, 50)
    assert result is None


def test_business_calculator_calculate_break_even_point_negative_contribution_margin(business_calculator):
    """Test calculate_break_even_point returns None when contribution margin is negative"""
    result = business_calculator.calculate_break_even_point(10000, 30, 50)
    assert result is None


def test_business_calculator_calculate_discount_price_normal(business_calculator):
    """Test calculate_discount_price with normal price and discount"""
    result = business_calculator.calculate_discount_price(200, 25)
    expected = 200 - (200 * (25 / 100))
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_discount_price_zero_discount(business_calculator):
    """Test calculate_discount_price with zero discount"""
    result = business_calculator.calculate_discount_price(200, 0)
    expected = 200
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_discount_price_over_100_discount(business_calculator):
    """Test calculate_discount_price with discount over 100 percent"""
    result = business_calculator.calculate_discount_price(200, 150)
    expected = 200 - (200 * (150 / 100))
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_tax_amount_normal(business_calculator):
    """Test calculate_tax_amount with normal amount and tax rate"""
    result = business_calculator.calculate_tax_amount(1000, 10)
    expected = 1000 * (10 / 100)
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_tax_amount_zero_tax_rate(business_calculator):
    """Test calculate_tax_amount with zero tax rate"""
    result = business_calculator.calculate_tax_amount(1000, 0)
    expected = 0
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_tax_amount_negative_tax_rate(business_calculator):
    """Test calculate_tax_amount with negative tax rate"""
    result = business_calculator.calculate_tax_amount(1000, -5)
    expected = 1000 * (-5 / 100)
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_net_present_value_normal(business_calculator):
    """Test calculate_net_present_value with valid cash flows and discount rate"""
    cash_flows = [1000, 2000, 3000]
    discount_rate = 0.1
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)

    expected = 0
    for period, cash_flow in enumerate(cash_flows):
        expected += cash_flow / math.pow(1 + discount_rate, period)

    assert result == pytest.approx(expected)


def test_business_calculator_calculate_net_present_value_empty_flows(business_calculator):
    """Test calculate_net_present_value with empty cash flows list"""
    cash_flows = []
    discount_rate = 0.1
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)
    assert result == pytest.approx(0)


def test_business_calculator_calculate_net_present_value_zero_discount_rate(business_calculator):
    """Test calculate_net_present_value with zero discount rate"""
    cash_flows = [1000, 2000, 3000]
    discount_rate = 0.0
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)

    expected = 0
    for period, cash_flow in enumerate(cash_flows):
        expected += cash_flow / math.pow(1 + discount_rate, period)

    assert result == pytest.approx(expected)


def test_business_calculator_calculate_net_present_value_negative_discount_rate(business_calculator):
    """Test calculate_net_present_value with negative discount rate"""
    cash_flows = [1000, 2000, 3000]
    discount_rate = -0.1
    result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)

    expected = 0
    for period, cash_flow in enumerate(cash_flows):
        expected += cash_flow / math.pow(1 + discount_rate, period)

    assert result == pytest.approx(expected)


def test_business_calculator_calculate_net_present_value_uses_math_pow(business_calculator):
    """Test calculate_net_present_value uses math.pow for discounting"""
    cash_flows = [1000, 2000]
    discount_rate = 0.05

    with patch("calculator.math.pow") as mock_pow:
        mock_pow.side_effect = math.pow
        result = business_calculator.calculate_net_present_value(cash_flows, discount_rate)

        assert mock_pow.call_count == len(cash_flows)
        for i, call in enumerate(mock_pow.call_args_list):
            args, _ = call
            assert args[0] == pytest.approx(1 + discount_rate)
            assert args[1] == i

        expected = 0
        for period, cash_flow in enumerate(cash_flows):
            expected += cash_flow / math.pow(1 + discount_rate, period)
        assert result == pytest.approx(expected)


def test_business_calculator_calculate_markup_percentage_normal(business_calculator):
    """Test calculate_markup_percentage with normal cost and selling price"""
    result = business_calculator.calculate_markup_percentage(100, 150)
    expected = ((150 - 100) / 100) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_markup_percentage_zero_cost(business_calculator):
    """Test calculate_markup_percentage returns 0 when cost is zero"""
    result = business_calculator.calculate_markup_percentage(0, 150)
    assert result == 0


def test_business_calculator_calculate_markup_percentage_negative_cost(business_calculator):
    """Test calculate_markup_percentage with negative cost"""
    result = business_calculator.calculate_markup_percentage(-100, 150)
    expected = ((150 - -100) / -100) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_calculate_markup_percentage_negative_selling_price(business_calculator):
    """Test calculate_markup_percentage with negative selling price"""
    result = business_calculator.calculate_markup_percentage(100, -150)
    expected = ((-150 - 100) / 100) * 100
    assert result == pytest.approx(expected)


def test_business_calculator_methods_do_not_raise_exceptions_with_valid_input(business_calculator):
    """Test that all methods do not raise exceptions with typical valid inputs"""
    business_calculator.calculate_profit_margin(1000, 500)
    business_calculator.calculate_roi(1500, 1000)
    business_calculator.calculate_compound_growth_rate(1000, 1200, 2)
    business_calculator.calculate_break_even_point(10000, 60, 40)
    business_calculator.calculate_discount_price(200, 10)
    business_calculator.calculate_tax_amount(1000, 5)
    business_calculator.calculate_net_present_value([1000, 2000, 3000], 0.1)
    business_calculator.calculate_markup_percentage(100, 130)


def test_business_calculator_calculate_net_present_value_invalid_cash_flows_type(business_calculator):
    """Test calculate_net_present_value raises TypeError when cash_flows is not iterable"""
    with pytest.raises(TypeError):
        business_calculator.calculate_net_present_value(None, 0.1)


def test_business_calculator_calculate_net_present_value_invalid_discount_rate_type(business_calculator):
    """Test calculate_net_present_value raises TypeError when discount_rate is invalid type"""
    with pytest.raises(TypeError):
        business_calculator.calculate_net_present_value([1000, 2000], "0.1")