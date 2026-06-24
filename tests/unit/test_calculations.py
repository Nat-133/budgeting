import pytest
from datetime import datetime
import pandas as pd
from backend.calculations.calculations import (
    fractional_months_between,
    budgeted_spending_between_dates,
    income_between_dates
)
from ..fixtures.sample_data import create_sample_budget_data, create_sample_income_data


class TestCalculations:
    def test_fractional_months_between(self):
        # Test full month
        start = datetime(2025, 1, 1)
        end = datetime(2025, 2, 1)
        result = fractional_months_between(start, end)
        assert result == 1.0

        # Test partial month (roughly half)
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 16)
        result = fractional_months_between(start, end)
        assert 0.4 < result < 0.6  # Approximately half a month

        # Test zero months
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 1)
        result = fractional_months_between(start, end)
        assert result == 0.0

    def test_budgeted_spending_between_dates(self):
        budget_df = create_sample_budget_data()
        budget_date = datetime(2024, 4, 7)
        budgets = [(budget_date, budget_df)]

        # Test spending calculation for 1 month period
        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = budgeted_spending_between_dates(start_date, end_date, budgets)

        expected_monthly_cost = budget_df["cost"].sum()  # Should be around 905.89
        assert abs(result - expected_monthly_cost) < 0.01

        # Test no spending when date range doesn't include budget
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 1)
        result = budgeted_spending_between_dates(start_date, end_date, budgets)
        assert result == 0.0

    def test_income_between_dates(self):
        income_df = create_sample_income_data()
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        # Test income calculation for 1 month period
        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 5, 7)

        result = income_between_dates(start_date, end_date, incomes)

        expected_monthly_income = income_df["income"].sum()  # Should be 3291.39
        assert abs(result - expected_monthly_income) < 0.01

        # Test no income when date range doesn't include income
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 1)
        result = income_between_dates(start_date, end_date, incomes)
        assert result == 0.0

    def test_income_multiple_months(self):
        income_df = create_sample_income_data()
        income_date = datetime(2024, 4, 7)
        incomes = [(income_date, income_df)]

        # Test income calculation for 2 month period
        start_date = datetime(2024, 4, 7)
        end_date = datetime(2024, 6, 7)

        result = income_between_dates(start_date, end_date, incomes)

        expected_income = income_df["income"].sum() * 2  # 2 months
        assert abs(result - expected_income) < 0.01
