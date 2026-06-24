import pytest
from datetime import datetime
import pandas as pd
from backend.calculations.calculations import (
    budgeted_spending_between_dates_itemized,
    income_between_dates_itemized,
)
from ..fixtures.sample_data import create_sample_budget_data, create_sample_income_data


class TestCalculationsItemized:
    """Test itemized calculation functions that return per-item breakdowns."""

    def test_budgeted_spending_itemized_returns_series(self):
        """Test that itemized spending returns a pandas Series."""
        budget_df = create_sample_budget_data()
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)

        assert isinstance(result, pd.Series)
        assert len(result) > 0

    def test_budgeted_spending_itemized_has_correct_items(self):
        """Test that itemized spending includes all budget items."""
        budget_df = create_sample_budget_data()
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)

        # Check that budget items are in the result
        assert "Housing" in result.index
        assert "Utility A" in result.index
        assert "Utility B" in result.index
        assert "Service Fee" in result.index

    def test_budgeted_spending_itemized_values_for_one_month(self):
        """Test that itemized spending values are correct for 1 month period."""
        budget_df = create_sample_budget_data()
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)

        # For 1 month, values should match the original budget
        assert abs(result["Housing"] - 800.00) < 0.01
        assert abs(result["Utility A"] - 150.50) < 0.01
        assert abs(result["Utility B"] - 50.25) < 0.01
        assert abs(result["Service Fee"] - 100.75) < 0.01

    def test_budgeted_spending_itemized_sum_equals_total(self):
        """Test that sum of itemized spending equals the total spending."""
        budget_df = create_sample_budget_data()
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)
        expected_total = budget_df["cost"].sum()

        assert abs(result.sum() - expected_total) < 0.01

    def test_budgeted_spending_itemized_partial_month(self):
        """Test itemized spending for partial month (should be proportional)."""
        budget_df = create_sample_budget_data()
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        # Half month period
        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 4, 22)

        result = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)

        # For ~0.5 months, values should be roughly half
        assert result["Housing"] < 800.00
        assert result["Housing"] > 350.00  # Roughly half
        assert abs(result["Housing"] / 800.00 - 0.5) < 0.1  # Within 10% of half

    def test_budgeted_spending_itemized_empty_period(self):
        """Test itemized spending when no budget overlaps the period."""
        budget_df = create_sample_budget_data()
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        # Period before budget starts
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 1)

        result = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)

        assert len(result) == 0 or result.sum() == 0.0

    def test_budgeted_spending_itemized_multiple_budgets(self):
        """Test itemized spending across multiple budget periods."""
        budget_df1 = create_sample_budget_data()
        budget_df2 = budget_df1.copy()
        budget_df2["cost"] = budget_df2["cost"] * 1.5  # 50% increase

        budgets = [
            (datetime(2024, 1, 1), budget_df1),
            (datetime(2024, 3, 1), budget_df2),
        ]

        # Period spanning both budgets: Feb 1 - Apr 1
        # Feb 1 - Mar 1: 1 month at budget1 (650)
        # Mar 1 - Apr 1: 1 month at budget2 (975)
        # Total: 1625
        start_date = datetime(2024, 2, 1)
        end_date = datetime(2024, 4, 1)

        result = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)

        # Should have housing from both periods
        assert "Housing" in result.index
        # Should be 1 month of budget1 (800) + 1 month of budget2 (1200) = 2000
        expected = 800.00 + (800.00 * 1.5)
        assert abs(result["Housing"] - expected) < 0.01

    def test_income_itemized_returns_series(self):
        """Test that itemized income returns a pandas Series."""
        income_df = create_sample_income_data()
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = income_between_dates_itemized(start_date, end_date, incomes)

        assert isinstance(result, pd.Series)
        assert len(result) > 0

    def test_income_itemized_has_correct_sources(self):
        """Test that itemized income includes all income sources."""
        income_df = create_sample_income_data()
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = income_between_dates_itemized(start_date, end_date, incomes)

        # Check that income sources are in the result
        assert "Primary Income" in result.index

    def test_income_itemized_values_for_one_month(self):
        """Test that itemized income values are correct for 1 month period."""
        income_df = create_sample_income_data()
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = income_between_dates_itemized(start_date, end_date, incomes)

        # For 1 month, value should match the original income (but calculated differently)
        expected = income_df["income"].sum()
        assert abs(result.sum() - expected) < 0.01

    def test_income_itemized_sum_equals_total(self):
        """Test that sum of itemized income equals the total income."""
        income_df = create_sample_income_data()
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 6, 7)

        result = income_between_dates_itemized(start_date, end_date, incomes)
        expected_total = income_df["income"].sum() * 2  # 2 months

        assert abs(result.sum() - expected_total) < 0.01

    def test_income_itemized_empty_period(self):
        """Test itemized income when no income overlaps the period."""
        income_df = create_sample_income_data()
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        # Period before income starts
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 1)

        result = income_between_dates_itemized(start_date, end_date, incomes)

        assert len(result) == 0 or result.sum() == 0.0

    def test_multiple_income_sources(self):
        """Test itemized income with multiple income sources."""
        # Create income with multiple sources
        income_df = pd.DataFrame({
            'schedule': ['monthly', 'monthly'],
            'income': [3000.0, 500.0],
            'category': ['Salary', 'Freelance']
        }, index=['Job', 'Side Gig'])

        incomes = [(datetime(2024, 1, 1), income_df)]

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 1)

        result = income_between_dates_itemized(start_date, end_date, incomes)

        assert "Job" in result.index
        assert "Side Gig" in result.index
        assert abs(result["Job"] - 3000.0) < 0.01
        assert abs(result["Side Gig"] - 500.0) < 0.01
