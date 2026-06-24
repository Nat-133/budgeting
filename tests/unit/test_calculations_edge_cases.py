import pytest
from datetime import datetime
import pandas as pd
from backend.calculations.calculations import (
    fractional_months_between,
    budgeted_spending_between_dates,
    income_between_dates
)
from ..fixtures.sample_data import create_sample_budget_data, create_sample_income_data


class TestCalculationsEdgeCases:
    """Test edge cases and error scenarios for core calculations."""

    # ===== Time Period Edge Cases =====

    def test_fractional_months_negative_period(self):
        """Test when end date is before start date (negative time period)."""
        start = datetime(2025, 3, 15)
        end = datetime(2025, 1, 10)

        result = fractional_months_between(start, end)

        # Should return negative value for reverse time period
        assert result < 0
        # Should be approximately -2.16 months (Jan 10 to Mar 15 backwards)
        assert abs(result + 2.16) < 0.1

    def test_fractional_months_same_date(self):
        """Test when start and end dates are identical."""
        date = datetime(2025, 6, 15)
        result = fractional_months_between(date, date)

        assert result == 0.0

    def test_fractional_months_leap_year_boundary(self):
        """Test calculations crossing leap year February."""
        # Non-leap year: Feb 28 -> Mar 1 (1 day in February)
        start_non_leap = datetime(2023, 2, 28)
        end_non_leap = datetime(2023, 3, 1)
        result_non_leap = fractional_months_between(start_non_leap, end_non_leap)

        # Leap year: Feb 28 -> Mar 1 (1 day in February)
        start_leap = datetime(2024, 2, 28)
        end_leap = datetime(2024, 3, 1)
        result_leap = fractional_months_between(start_leap, end_leap)

        # Results should be different due to leap year February having different length
        assert result_leap != result_non_leap
        # Leap year Feb has 29 days, non-leap has 28, so 1 day is larger fraction in non-leap year
        assert result_leap > result_non_leap  # 1/28 > 1/29 after corrected logic

    def test_fractional_months_month_end_edge_cases(self):
        """Test month-end calculations with varying month lengths."""
        # Jan 31 -> Feb 28 (non-leap year) - this is exactly 28 days = 1 full month
        jan31_to_feb28 = fractional_months_between(
            datetime(2023, 1, 31),
            datetime(2023, 2, 28)
        )

        # Jan 31 -> Mar 31 (should be exactly 2 months)
        jan31_to_mar31 = fractional_months_between(
            datetime(2023, 1, 31),
            datetime(2023, 3, 31)
        )

        # Should handle month-end correctly
        assert pytest.approx(jan31_to_feb28, abs=0.01) == 1.0    # Exactly 1 month (28 days in Feb)
        assert pytest.approx(jan31_to_mar31, abs=0.01) == 2.0    # Exactly 2 months

    def test_fractional_months_year_boundary(self):
        """Test calculations crossing year boundaries."""
        # Dec 31, 2023 -> Jan 1, 2024 (1 day)
        year_boundary = fractional_months_between(
            datetime(2023, 12, 31),
            datetime(2024, 1, 1)
        )

        # Should be 1 day out of 31 days in January
        expected = 1.0 / 31
        assert pytest.approx(year_boundary, abs=0.001) == expected

    # ===== Data Validation Edge Cases =====

    def test_budgeted_spending_empty_list(self):
        """Test spending calculation with empty budget list."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 2, 1)
        empty_budgets = []

        result = budgeted_spending_between_dates(start, end, empty_budgets)

        assert result == 0.0

    def test_income_between_dates_empty_list(self):
        """Test income calculation with empty income list."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 2, 1)
        empty_income = []

        result = income_between_dates(start, end, empty_income)

        assert result == 0.0

    def test_budgeted_spending_no_matching_dates(self):
        """Test spending when date range is before any budget exists."""
        budget_df = create_sample_budget_data()
        # Budget is dated 2024-04-07, request data from before it
        budgets = [(datetime(2024, 4, 7), budget_df)]

        # Period before any budget exists
        start = datetime(2024, 1, 1)
        end = datetime(2024, 2, 1)

        result = budgeted_spending_between_dates(start, end, budgets)

        assert result == 0.0

    def test_income_no_matching_dates(self):
        """Test income when no income periods overlap with requested range."""
        income_df = create_sample_income_data()
        # Income is dated 2024-04-07, request data from 2023
        income = [(datetime(2024, 4, 7), income_df)]

        start = datetime(2023, 1, 1)
        end = datetime(2023, 2, 1)

        result = income_between_dates(start, end, income)

        assert result == 0.0

    def test_far_future_dates(self):
        """Test calculations with dates far in the future."""
        budget_df = create_sample_budget_data()
        budgets = [(datetime(2024, 4, 7), budget_df)]

        # Request data 50 years in the future
        start = datetime(2024, 4, 7)
        end = datetime(2074, 4, 7)

        result = budgeted_spending_between_dates(start, end, budgets)

        # Should handle large time periods without error
        assert result > 0
        # Should be roughly 50 years * 12 months * monthly budget
        expected_roughly = 50 * 12 * budget_df['cost'].sum()
        assert abs(result - expected_roughly) < expected_roughly * 0.1  # Within 10%

    # ===== Multiple Period Scenarios =====

    def test_overlapping_budget_periods(self):
        """Test handling of overlapping budget periods."""
        # Create two budgets with overlapping date ranges
        budget1 = create_sample_budget_data()
        budget2 = budget1.copy()
        budget2['cost'] = budget2['cost'] * 1.5  # 50% higher costs

        budgets = [
            (datetime(2024, 1, 1), budget1),  # Starts Jan 1
            (datetime(2024, 3, 1), budget2),  # Starts Mar 1, overlaps
        ]

        # Request data from Feb 1 to May 1 (covers both budgets)
        start = datetime(2024, 2, 1)
        end = datetime(2024, 5, 1)

        result = budgeted_spending_between_dates(start, end, budgets)

        # Should include spending from both budget periods
        # Feb 1 - Mar 1: budget1 (1 month)
        # Mar 1 - May 1: budget2 (2 months)
        expected = budget1['cost'].sum() * 1 + budget2['cost'].sum() * 2
        assert pytest.approx(result, rel=0.01) == expected

    def test_budget_gaps(self):
        """Test periods with no budget data."""
        budget_df = create_sample_budget_data()
        # Budget only covers April 2024
        budgets = [(datetime(2024, 4, 1), budget_df)]

        # Request data from January (before any budget)
        start = datetime(2024, 1, 1)
        end = datetime(2024, 3, 1)

        result = budgeted_spending_between_dates(start, end, budgets)

        # Should return 0 for periods with no budget
        assert result == 0.0

    def test_partial_period_coverage(self):
        """Test when budget starts mid-way through requested range."""
        budget_df = create_sample_budget_data()
        # Budget starts March 15
        budgets = [(datetime(2024, 3, 15), budget_df)]

        # Request data from March 1 to April 1
        start = datetime(2024, 3, 1)
        end = datetime(2024, 4, 1)

        result = budgeted_spending_between_dates(start, end, budgets)

        # Should only include spending from March 15 to April 1
        expected_days = (datetime(2024, 4, 1) - datetime(2024, 3, 15)).days
        expected_fraction = expected_days / 31  # March has 31 days
        expected = budget_df['cost'].sum() * expected_fraction

        assert pytest.approx(result, rel=0.05) == expected

    def test_multiple_income_periods(self):
        """Test income calculation with multiple overlapping periods."""
        income1 = create_sample_income_data()
        income2 = income1.copy()
        income2['income'] = income2['income'] * 1.2  # 20% raise

        income_periods = [
            (datetime(2024, 1, 1), income1),
            (datetime(2024, 6, 1), income2),  # Raise starts June
        ]

        # Calculate income for full year
        start = datetime(2024, 1, 1)
        end = datetime(2025, 1, 1)

        result = income_between_dates(start, end, income_periods)

        # Should be 5 months of income1 + 7 months of income2
        expected = income1['income'].sum() * 5 + income2['income'].sum() * 7
        assert pytest.approx(result, rel=0.01) == expected

    # ===== Regression Tests =====

    def test_income_applies_to_future_periods_after_file_date(self):
        """Regression test: Income file should apply to periods entirely after its date.

        This tests the bug where income_between_dates returned 0 when calculating
        for a period that starts after the income file date (e.g., income file dated
        April 2024, but calculating income for Dec 2024 to May 2025).

        Bug: Only counted income if income_start fell within [start_date, end_date).
        Fix: Use most recent income file active at start_date.
        """
        income_df = create_sample_income_data()
        # Income file dated April 7, 2024
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        # Calculate income for period entirely AFTER the income file date
        # This was the scenario that caused zero predicted saving rate
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2025, 5, 1)  # 5 months later

        result = income_between_dates(start_date, end_date, incomes)

        # Should apply the April 2024 income rates for the entire period
        expected = income_df['income'].sum() * 5  # 5 months of income
        assert result > 0, "Income should be counted even when period is after income file date"
        assert pytest.approx(result, rel=0.01) == expected

    def test_budget_applies_to_future_periods_after_file_date(self):
        """Regression test: Budget file should apply to periods entirely after its date.

        Similar to the income bug above, but for budgeted spending.
        """
        budget_df = create_sample_budget_data()
        # Budget file dated April 7, 2024
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        # Calculate spending for period entirely AFTER the budget file date
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2025, 5, 1)  # 5 months later

        result = budgeted_spending_between_dates(start_date, end_date, budgets)

        # Should apply the April 2024 budget rates for the entire period
        expected = budget_df['cost'].sum() * 5  # 5 months of spending
        assert result > 0, "Budget should be counted even when period is after budget file date"
        assert pytest.approx(result, rel=0.01) == expected

    def test_fractional_months_spans_multiple_years(self):
        """Regression test: fractional_months_between must count years correctly.

        Bug: Only used delta.months (0-11), ignoring delta.years.
        Fix: Use delta.years * 12 + delta.months.
        """
        # Test 14 month span (more than 1 year)
        start = datetime(2024, 1, 1)
        end = datetime(2025, 3, 1)  # 14 months later

        result = fractional_months_between(start, end)

        # Should be 14 months, not 2 months
        assert result > 12, "Should count years in addition to months"
        assert pytest.approx(result, abs=0.1) == 14.0
