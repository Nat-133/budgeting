import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from backend.calculations.balance_analyzer import (
    calculate_previous_total,
    calculate_months_since_last_recording,
    calculate_expected_income_since_last_recording,
    calculate_predicted_spend_since_last_recording,
    calculate_actual_spend_since_last_recording,
    calculate_spending_deficit,
    calculate_spending_rate,
    calculate_predicted_total_from_last_recording,
    calculate_predicted_total_deficit,
    calculate_balance_change,
    calculate_saving_rate,
    calculate_predicted_saving_rate,
    calculate_predicted_latest_total,
    calculate_latest_total_difference,
)
from ..fixtures.sample_data import create_sample_budget_data, create_sample_income_data


class TestBalanceAnalyzerFunctions:
    """Test individual calculation functions from balance_analyzer."""

    def test_calculate_previous_total(self):
        """Test that previous total correctly shifts the balance."""
        balance = pd.DataFrame({
            "Date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "Total": [1000.0, 1100.0, 1200.0]
        })

        result = calculate_previous_total(balance)

        assert pd.isna(result.iloc[0])  # First row should be NaN
        assert result.iloc[1] == 1000.0
        assert result.iloc[2] == 1100.0

    def test_calculate_months_since_last_recording(self):
        """Test fractional months calculation between dates."""
        dates = pd.Series([
            datetime(2024, 1, 1),
            datetime(2024, 2, 1),  # Exactly 1 month
            datetime(2024, 2, 16),  # Half month
        ])

        result = calculate_months_since_last_recording(dates)

        assert np.isnan(result[0])  # First entry is NaN
        assert abs(result[1] - 1.0) < 0.01  # ~1 month
        assert abs(result[2] - 0.5) < 0.1  # ~0.5 months

    def test_calculate_expected_income_since_last_recording(self):
        """Test expected income calculation between dates."""
        dates = pd.Series([
            datetime(2024, 4, 7),
            datetime(2024, 5, 7),  # 1 month later
        ])
        income_df = create_sample_income_data()
        income = [(datetime(2024, 4, 7), income_df)]

        result = calculate_expected_income_since_last_recording(dates, income)

        assert np.isnan(result[0])  # First entry is NaN
        expected = income_df["income"].sum()  # 3291.39
        assert abs(result[1] - expected) < 0.01

    def test_calculate_predicted_spend_since_last_recording(self):
        """Test predicted spending calculation between dates."""
        dates = pd.Series([
            datetime(2024, 4, 7),
            datetime(2024, 5, 7),  # 1 month later
        ])
        budget_df = create_sample_budget_data()
        budgets = [(datetime(2024, 4, 7), budget_df)]

        result = calculate_predicted_spend_since_last_recording(dates, budgets)

        assert np.isnan(result[0])  # First entry is NaN
        expected = budget_df["cost"].sum()  # 905.89
        assert abs(result[1] - expected) < 0.01

    def test_calculate_actual_spend_since_last_recording(self):
        """Test actual spending calculation from balance changes.

        Formula: actual_spend = previous_total + expected_income - current_total
        """
        current_total = pd.Series([1000.0, 1500.0, 1800.0])
        previous_total = pd.Series([np.nan, 1000.0, 1500.0])
        expected_income = pd.Series([np.nan, 1000.0, 1000.0])

        result = calculate_actual_spend_since_last_recording(
            current_total, previous_total, expected_income
        )

        # First row: NaN (no previous data)
        assert pd.isna(result.iloc[0])

        # Second row: 1000 + 1000 - 1500 = 500
        assert result.iloc[1] == 500.0

        # Third row: 1500 + 1000 - 1800 = 700
        assert result.iloc[2] == 700.0

    def test_calculate_spending_deficit_underspending(self):
        """Test spending deficit when actual spending is less than predicted."""
        predicted = pd.Series([1000.0, 1000.0, 1000.0])
        actual = pd.Series([800.0, 900.0, 950.0])

        result = calculate_spending_deficit(predicted, actual)

        # Positive deficit = underspending
        assert result.iloc[0] == 200.0
        assert result.iloc[1] == 100.0
        assert result.iloc[2] == 50.0

    def test_calculate_spending_deficit_overspending(self):
        """Test spending deficit when actual spending exceeds predicted."""
        predicted = pd.Series([1000.0, 1000.0, 1000.0])
        actual = pd.Series([1200.0, 1100.0, 1050.0])

        result = calculate_spending_deficit(predicted, actual)

        # Negative deficit = overspending
        assert result.iloc[0] == -200.0
        assert result.iloc[1] == -100.0
        assert result.iloc[2] == -50.0

    def test_calculate_spending_rate(self):
        """Test spending rate per month calculation."""
        spending = pd.Series([1000.0, 2000.0, 1500.0])
        months = pd.Series([1.0, 2.0, 0.5])

        result = calculate_spending_rate(spending, months)

        assert result.iloc[0] == 1000.0  # 1000/1
        assert result.iloc[1] == 1000.0  # 2000/2
        assert result.iloc[2] == 3000.0  # 1500/0.5

    def test_calculate_predicted_total_from_last_recording(self):
        """Test predicted balance calculation."""
        previous_total = pd.Series([np.nan, 1000.0, 1500.0])
        expected_income = pd.Series([np.nan, 3000.0, 3000.0])
        predicted_spend = pd.Series([np.nan, 2000.0, 2000.0])

        result = calculate_predicted_total_from_last_recording(
            previous_total, expected_income, predicted_spend
        )

        # First row: NaN
        assert pd.isna(result.iloc[0])

        # Second row: 1000 + 3000 - 2000 = 2000
        assert result.iloc[1] == 2000.0

        # Third row: 1500 + 3000 - 2000 = 2500
        assert result.iloc[2] == 2500.0

    def test_calculate_predicted_total_deficit(self):
        """Test difference between actual and predicted balance."""
        actual_total = pd.Series([1000.0, 2100.0, 2600.0])
        predicted_total = pd.Series([1000.0, 2000.0, 2500.0])

        result = calculate_predicted_total_deficit(actual_total, predicted_total)

        assert result.iloc[0] == 0.0   # No difference
        assert result.iloc[1] == 100.0  # Better than predicted
        assert result.iloc[2] == 100.0  # Better than predicted

    def test_calculate_balance_change(self):
        """Test balance change calculation."""
        current_total = pd.Series([1000.0, 1100.0, 1050.0])
        previous_total = pd.Series([np.nan, 1000.0, 1100.0])

        result = calculate_balance_change(current_total, previous_total)

        assert pd.isna(result.iloc[0])  # First row is NaN
        assert result.iloc[1] == 100.0   # Increased by 100
        assert result.iloc[2] == -50.0   # Decreased by 50

    def test_calculate_saving_rate(self):
        """Test saving rate per month calculation."""
        balance_change = pd.Series([np.nan, 500.0, 300.0])
        months = pd.Series([np.nan, 1.0, 2.0])

        result = calculate_saving_rate(balance_change, months)

        assert pd.isna(result.iloc[0])
        assert result.iloc[1] == 500.0  # 500/1
        assert result.iloc[2] == 150.0  # 300/2

    def test_calculate_predicted_saving_rate(self):
        """Test predicted saving rate calculation."""
        expected_income = pd.Series([np.nan, 3000.0, 3000.0])
        predicted_spend = pd.Series([np.nan, 2500.0, 2700.0])
        months = pd.Series([np.nan, 1.0, 2.0])

        result = calculate_predicted_saving_rate(
            expected_income, predicted_spend, months
        )

        assert pd.isna(result.iloc[0])
        assert result.iloc[1] == 500.0  # (3000-2500)/1
        assert result.iloc[2] == 150.0  # (3000-2700)/2

    def test_calculate_predicted_latest_total(self):
        """Test prediction of latest balance from historical points."""
        balance = pd.DataFrame({
            "Date": [datetime(2024, 1, 1), datetime(2024, 2, 1)],
            "Total": [1000.0, 1500.0]
        })
        latest_date = datetime(2024, 3, 1)

        budget_df = create_sample_budget_data()
        income_df = create_sample_income_data()
        budgets = [(datetime(2024, 1, 1), budget_df)]
        income = [(datetime(2024, 1, 1), income_df)]

        result = calculate_predicted_latest_total(balance, latest_date, budgets, income)

        assert len(result) == 2
        # Each result should be a prediction from that historical point
        assert all(isinstance(x, (int, float)) for x in result)

    def test_calculate_latest_total_difference(self):
        """Test difference between actual and predicted latest totals."""
        latest_total = 5000.0
        predicted_latest = pd.Series([4800.0, 4900.0, 5100.0])

        result = calculate_latest_total_difference(latest_total, predicted_latest)

        assert result.iloc[0] == 200.0   # 5000 - 4800
        assert result.iloc[1] == 100.0   # 5000 - 4900
        assert result.iloc[2] == -100.0  # 5000 - 5100

    def test_mathematical_invariant_balance_equation(self):
        """Test that balance change equals income minus spending."""
        # Setup test data where we know the relationships
        previous_total = pd.Series([1000.0, 1500.0])
        current_total = pd.Series([1500.0, 2000.0])
        expected_income = pd.Series([1000.0, 1200.0])

        # Calculate actual spending
        actual_spend = calculate_actual_spend_since_last_recording(
            current_total, previous_total, expected_income
        )

        # Calculate balance change
        balance_change = calculate_balance_change(current_total, previous_total)

        # Invariant: balance_change = expected_income - actual_spend
        for i in range(len(balance_change)):
            if not pd.isna(balance_change.iloc[i]):
                expected_change = expected_income.iloc[i] - actual_spend.iloc[i]
                assert abs(balance_change.iloc[i] - expected_change) < 0.01

    def test_edge_case_zero_months(self):
        """Test handling of zero months in rate calculations."""
        spending = pd.Series([1000.0])
        months = pd.Series([0.0])

        result = calculate_spending_rate(spending, months)

        # Division by zero should result in inf
        assert np.isinf(result.iloc[0])

    def test_edge_case_negative_spending(self):
        """Test handling of negative spending (which shouldn't happen but might)."""
        predicted = pd.Series([1000.0])
        actual = pd.Series([-100.0])

        result = calculate_spending_deficit(predicted, actual)

        # Large positive deficit indicates something went very wrong
        assert result.iloc[0] == 1100.0
