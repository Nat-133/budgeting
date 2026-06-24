import pytest
from datetime import datetime, date
import pandas as pd
from backend.calculations.calculations import sum_between_range
from ..fixtures.sample_data import create_sample_budget_data, create_sample_income_data


class TestStep1CalculateDateRanges:
    """Test Step 1: Calculate effective date ranges for each cashflow plan."""

    def test_single_plan_fully_within_range(self):
        """Test date range calculation for a single plan fully within the requested range."""
        budget_df = create_sample_budget_data()
        plans = [(datetime(2024, 2, 1), budget_df)]

        start = date(2024, 1, 1)
        end = date(2024, 4, 1)

        # Import the helper function we'll create
        from backend.calculations.calculations import _calculate_effective_date_ranges

        ranges = _calculate_effective_date_ranges(plans, start, end)

        # Should return one range: (plan_start_date, requested_end)
        assert len(ranges) == 1
        plan_date, df, effective_start, effective_end = ranges[0]
        assert effective_start == date(2024, 2, 1)  # max(2024-01-01, 2024-02-01)
        assert effective_end == date(2024, 4, 1)    # requested end

    def test_single_plan_overlapping_start(self):
        """Test when plan starts before requested range."""
        budget_df = create_sample_budget_data()
        plans = [(datetime(2024, 1, 1), budget_df)]

        start = date(2024, 2, 1)
        end = date(2024, 4, 1)

        from backend.calculations.calculations import _calculate_effective_date_ranges

        ranges = _calculate_effective_date_ranges(plans, start, end)

        assert len(ranges) == 1
        plan_date, df, effective_start, effective_end = ranges[0]
        assert effective_start == date(2024, 2, 1)  # max(2024-02-01, 2024-01-01) = requested start
        assert effective_end == date(2024, 4, 1)

    def test_multiple_plans_non_overlapping(self):
        """Test multiple plans where each ends when the next begins."""
        budget_df1 = create_sample_budget_data()
        budget_df2 = create_sample_budget_data()

        plans = [
            (datetime(2024, 1, 1), budget_df1),
            (datetime(2024, 3, 1), budget_df2),
        ]

        start = date(2024, 1, 1)
        end = date(2024, 5, 1)

        from backend.calculations.calculations import _calculate_effective_date_ranges

        ranges = _calculate_effective_date_ranges(plans, start, end)

        assert len(ranges) == 2

        # First plan: starts at 2024-01-01, ends at 2024-03-01 (when next plan starts)
        _, _, start1, end1 = ranges[0]
        assert start1 == date(2024, 1, 1)
        assert end1 == date(2024, 3, 1)

        # Second plan: starts at 2024-03-01, ends at 2024-05-01 (requested end)
        _, _, start2, end2 = ranges[1]
        assert start2 == date(2024, 3, 1)
        assert end2 == date(2024, 5, 1)

    def test_plan_outside_requested_range(self):
        """Test that plans outside the requested range are excluded."""
        budget_df = create_sample_budget_data()
        plans = [(datetime(2024, 6, 1), budget_df)]

        start = date(2024, 1, 1)
        end = date(2024, 4, 1)

        from backend.calculations.calculations import _calculate_effective_date_ranges

        ranges = _calculate_effective_date_ranges(plans, start, end)

        # Plan starts after requested range ends, should be excluded
        assert len(ranges) == 0

    def test_plans_sorted_by_date(self):
        """Test that plans are processed in chronological order even if input is unsorted."""
        budget_df1 = create_sample_budget_data()
        budget_df2 = create_sample_budget_data()

        # Provide plans in reverse order
        plans = [
            (datetime(2024, 3, 1), budget_df2),
            (datetime(2024, 1, 1), budget_df1),
        ]

        start = date(2024, 1, 1)
        end = date(2024, 5, 1)

        from backend.calculations.calculations import _calculate_effective_date_ranges

        ranges = _calculate_effective_date_ranges(plans, start, end)

        # Should be sorted by date
        assert len(ranges) == 2
        plan_date1, _, _, _ = ranges[0]
        plan_date2, _, _, _ = ranges[1]
        assert plan_date1.date() == date(2024, 1, 1)
        assert plan_date2.date() == date(2024, 3, 1)


class TestStep2CalculateCashflowForRange:
    """Test Step 2: Calculate cashflow totals for a single plan within its date range."""

    def test_budget_cashflow_one_month(self):
        """Test calculating budget cashflow for exactly one month."""
        budget_df = create_sample_budget_data()
        plan_date = datetime(2024, 1, 1)

        effective_start = date(2024, 1, 1)
        effective_end = date(2024, 2, 1)

        from backend.calculations.calculations import _calculate_cashflow_for_range

        result = _calculate_cashflow_for_range(
            plan_date, budget_df, effective_start, effective_end, is_income=False
        )

        assert isinstance(result, pd.Series)
        # For 1 month, values should equal monthly costs
        assert abs(result["Housing"] - 800.00) < 0.01
        assert abs(result["Utility A"] - 150.50) < 0.01

    def test_budget_cashflow_partial_month(self):
        """Test calculating budget cashflow for a partial month."""
        budget_df = create_sample_budget_data()
        plan_date = datetime(2024, 1, 1)

        # Roughly half a month
        effective_start = date(2024, 1, 1)
        effective_end = date(2024, 1, 16)

        from backend.calculations.calculations import _calculate_cashflow_for_range

        result = _calculate_cashflow_for_range(
            plan_date, budget_df, effective_start, effective_end, is_income=False
        )

        # For ~0.5 months, values should be roughly half
        assert result["Housing"] < 800.00
        assert result["Housing"] > 350.00
        assert abs(result["Housing"] / 800.00 - 0.5) < 0.1

    def test_budget_cashflow_multiple_months(self):
        """Test calculating budget cashflow for multiple months."""
        budget_df = create_sample_budget_data()
        plan_date = datetime(2024, 1, 1)

        effective_start = date(2024, 1, 1)
        effective_end = date(2024, 4, 1)  # 3 months

        from backend.calculations.calculations import _calculate_cashflow_for_range

        result = _calculate_cashflow_for_range(
            plan_date, budget_df, effective_start, effective_end, is_income=False
        )

        # For 3 months, values should be triple
        assert abs(result["Housing"] - (800.00 * 3)) < 0.01
        assert abs(result["Utility A"] - (150.50 * 3)) < 0.01

    def test_income_cashflow_one_month(self):
        """Test calculating income cashflow for one month."""
        income_df = create_sample_income_data()
        plan_date = datetime(2024, 1, 1)

        effective_start = date(2024, 1, 1)
        effective_end = date(2024, 2, 1)

        from backend.calculations.calculations import _calculate_cashflow_for_range

        result = _calculate_cashflow_for_range(
            plan_date, income_df, effective_start, effective_end, is_income=True
        )

        assert isinstance(result, pd.Series)
        # For 1 month, sum should equal total monthly income
        expected = income_df["income"].sum()
        assert abs(result.sum() - expected) < 0.01

    def test_cashflow_preserves_all_items(self):
        """Test that all items from the dataframe are present in the result."""
        budget_df = create_sample_budget_data()
        plan_date = datetime(2024, 1, 1)

        effective_start = date(2024, 1, 1)
        effective_end = date(2024, 2, 1)

        from backend.calculations.calculations import _calculate_cashflow_for_range

        result = _calculate_cashflow_for_range(
            plan_date, budget_df, effective_start, effective_end, is_income=False
        )

        # All budget items should be present
        assert "Housing" in result.index
        assert "Utility A" in result.index
        assert "Utility B" in result.index
        assert "Service Fee" in result.index
        assert len(result) == len(budget_df)


class TestStep3CombineCashflows:
    """Test Step 3: Combine multiple cashflow Series into a single itemized Series."""

    def test_combine_single_series(self):
        """Test combining a single Series returns it unchanged."""
        series1 = pd.Series({"Housing": 800.0, "Utilities": 200.0})

        from backend.calculations.calculations import _combine_cashflow_series

        result = _combine_cashflow_series([series1])

        assert isinstance(result, pd.Series)
        assert abs(result["Housing"] - 800.0) < 0.01
        assert abs(result["Utilities"] - 200.0) < 0.01
        assert len(result) == 2

    def test_combine_two_series_no_overlap(self):
        """Test combining two Series with different items."""
        series1 = pd.Series({"Housing": 800.0, "Utilities": 200.0})
        series2 = pd.Series({"Food": 300.0, "Transport": 150.0})

        from backend.calculations.calculations import _combine_cashflow_series

        result = _combine_cashflow_series([series1, series2])

        # Should have all 4 items
        assert len(result) == 4
        assert abs(result["Housing"] - 800.0) < 0.01
        assert abs(result["Utilities"] - 200.0) < 0.01
        assert abs(result["Food"] - 300.0) < 0.01
        assert abs(result["Transport"] - 150.0) < 0.01

    def test_combine_two_series_with_overlap(self):
        """Test combining two Series with some overlapping items (should sum)."""
        series1 = pd.Series({"Housing": 800.0, "Utilities": 200.0})
        series2 = pd.Series({"Housing": 900.0, "Food": 300.0})

        from backend.calculations.calculations import _combine_cashflow_series

        result = _combine_cashflow_series([series1, series2])

        # Should have 3 unique items
        assert len(result) == 3
        # Housing should be summed
        assert abs(result["Housing"] - 1700.0) < 0.01
        assert abs(result["Utilities"] - 200.0) < 0.01
        assert abs(result["Food"] - 300.0) < 0.01

    def test_combine_multiple_series(self):
        """Test combining multiple Series."""
        series1 = pd.Series({"A": 100.0, "B": 200.0})
        series2 = pd.Series({"B": 150.0, "C": 300.0})
        series3 = pd.Series({"A": 50.0, "C": 100.0, "D": 400.0})

        from backend.calculations.calculations import _combine_cashflow_series

        result = _combine_cashflow_series([series1, series2, series3])

        # Should have 4 unique items
        assert len(result) == 4
        # A appears in series1 and series3
        assert abs(result["A"] - 150.0) < 0.01
        # B appears in series1 and series2
        assert abs(result["B"] - 350.0) < 0.01
        # C appears in series2 and series3
        assert abs(result["C"] - 400.0) < 0.01
        # D appears only in series3
        assert abs(result["D"] - 400.0) < 0.01

    def test_combine_empty_list(self):
        """Test combining an empty list returns an empty Series."""
        from backend.calculations.calculations import _combine_cashflow_series

        result = _combine_cashflow_series([])

        assert isinstance(result, pd.Series)
        assert len(result) == 0


class TestSumBetweenRange:
    """Test the complete sum_between_range function - integration tests."""

    def test_single_budget_one_month(self):
        """Test sum_between_range with a single budget for one month."""
        budget_df = create_sample_budget_data()
        budgets = [(datetime(2024, 1, 1), budget_df)]

        start = date(2024, 1, 1)
        end = date(2024, 2, 1)

        result = sum_between_range(budgets, start, end)

        assert isinstance(result, pd.Series)
        # Should have all budget items
        assert "Housing" in result.index
        assert len(result) == len(budget_df)
        # For 1 month, values should match
        assert abs(result["Housing"] - 800.00) < 0.01
        assert abs(result.sum() - budget_df["cost"].sum()) < 0.01

    def test_single_budget_multiple_months(self):
        """Test sum_between_range with a single budget for multiple months."""
        budget_df = create_sample_budget_data()
        budgets = [(datetime(2024, 1, 1), budget_df)]

        start = date(2024, 1, 1)
        end = date(2024, 4, 1)  # 3 months

        result = sum_between_range(budgets, start, end)

        assert isinstance(result, pd.Series)
        # For 3 months, values should be tripled
        assert abs(result["Housing"] - (800.00 * 3)) < 0.01
        assert abs(result.sum() - (budget_df["cost"].sum() * 3)) < 0.01

    def test_multiple_budgets_sequential(self):
        """Test sum_between_range with multiple sequential budgets."""
        budget_df1 = create_sample_budget_data()
        budget_df2 = budget_df1.copy()
        budget_df2["cost"] = budget_df2["cost"] * 1.5  # 50% increase

        budgets = [
            (datetime(2024, 1, 1), budget_df1),
            (datetime(2024, 3, 1), budget_df2),
        ]

        start = date(2024, 1, 1)
        end = date(2024, 5, 1)

        result = sum_between_range(budgets, start, end)

        assert isinstance(result, pd.Series)
        # Should have all items
        assert "Housing" in result.index
        # Jan-Feb: 2 months at 800 = 1600
        # Mar-Apr: 2 months at 1200 = 2400
        # Total: 4000
        expected_housing = (800.00 * 2) + (800.00 * 1.5 * 2)
        assert abs(result["Housing"] - expected_housing) < 0.01

    def test_single_income_one_month(self):
        """Test sum_between_range with income data."""
        income_df = create_sample_income_data()
        incomes = [(datetime(2024, 1, 1), income_df)]

        start = date(2024, 1, 1)
        end = date(2024, 2, 1)

        result = sum_between_range(incomes, start, end)

        assert isinstance(result, pd.Series)
        assert len(result) > 0
        # For 1 month, sum should match total income
        assert abs(result.sum() - income_df["income"].sum()) < 0.01

    def test_budget_partial_overlap(self):
        """Test when budget only partially overlaps with requested range."""
        budget_df = create_sample_budget_data()
        budgets = [(datetime(2024, 2, 1), budget_df)]

        start = date(2024, 1, 1)
        end = date(2024, 3, 1)

        result = sum_between_range(budgets, start, end)

        assert isinstance(result, pd.Series)
        # Budget starts Feb 1, so only Feb counts (1 month)
        assert abs(result["Housing"] - 800.00) < 0.01

    def test_empty_budget_list(self):
        """Test with empty budget list."""
        budgets = []

        start = date(2024, 1, 1)
        end = date(2024, 2, 1)

        result = sum_between_range(budgets, start, end)

        assert isinstance(result, pd.Series)
        assert len(result) == 0

    def test_budget_outside_range(self):
        """Test when budget is completely outside the requested range."""
        budget_df = create_sample_budget_data()
        budgets = [(datetime(2024, 6, 1), budget_df)]

        start = date(2024, 1, 1)
        end = date(2024, 4, 1)

        result = sum_between_range(budgets, start, end)

        assert isinstance(result, pd.Series)
        assert len(result) == 0 or result.sum() == 0.0

    def test_preserves_itemization(self):
        """Test that result maintains itemization (not just a scalar)."""
        budget_df = create_sample_budget_data()
        budgets = [(datetime(2024, 1, 1), budget_df)]

        start = date(2024, 1, 1)
        end = date(2024, 2, 1)

        result = sum_between_range(budgets, start, end)

        # Must be a Series with multiple items
        assert isinstance(result, pd.Series)
        assert len(result) == len(budget_df)
        # Check all original items are present
        for item in budget_df.index:
            assert item in result.index
