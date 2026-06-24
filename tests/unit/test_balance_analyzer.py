import pytest
import pandas as pd
from datetime import datetime
from backend.calculations.balance_analyzer import (
    calculate_balance_analysis,
    generate_predicted_balance_timeline
)
from ..fixtures.sample_data import (
    create_sample_budget_data,
    create_sample_income_data,
    create_sample_balance_data
)


class TestBalanceAnalyzer:
    def test_calculate_balance_analysis(self):
        # Prepare test data
        balance = create_sample_balance_data()
        balance['Total'] = balance.drop(columns=['Date']).sum(axis=1)

        budget_df = create_sample_budget_data()
        income_df = create_sample_income_data()

        budgets = [(datetime(2024, 4, 7), budget_df)]
        income = [(datetime(2024, 4, 7), income_df)]

        # Run analysis
        result = calculate_balance_analysis(balance, budgets, income)

        # Check that all expected columns are present
        expected_columns = [
            "Date", "Total", "previous total",
            "months since last recording",
            "expected income since last recording",
            "predicted spend since last recording",
            "actual spend since last recording",
            "spending deficit",
            "saving rate since last recording",
            "predicted saving rate"
        ]

        for col in expected_columns:
            assert col in result.columns

        # Check that first row has NaN values (as expected)
        assert pd.isna(result["months since last recording"].iloc[0])
        assert pd.isna(result["expected income since last recording"].iloc[0])

        # Check that subsequent rows have calculated values
        assert not pd.isna(result["months since last recording"].iloc[1])
        assert not pd.isna(result["expected income since last recording"].iloc[1])

    def test_generate_predicted_balance_timeline(self):
        balance = create_sample_balance_data()
        balance['Total'] = balance.drop(columns=['Date']).sum(axis=1)

        budget_df = create_sample_budget_data()
        income_df = create_sample_income_data()

        budgets = [(datetime(2024, 4, 7), budget_df)]
        income = [(datetime(2024, 4, 7), income_df)]

        result = generate_predicted_balance_timeline(balance, budgets, income)

        # Check structure
        assert isinstance(result, pd.DataFrame)
        assert "Date" in result.columns
        assert "Predicted Balance" in result.columns

        # Should have multiple prediction points
        assert len(result) > len(balance)

        # Predicted balances should be reasonable (not negative infinity, etc.)
        assert all(result["Predicted Balance"] > -1000000)
        assert all(result["Predicted Balance"] < 1000000)

    def test_generate_predicted_balance_timeline_with_specific_start_dates(self):
        """Test that predictions start from the correct date when specified"""
        # Create balance data with specific dates including December 2024
        balance = pd.DataFrame({
            'Date': [
                datetime(2024, 6, 15),
                datetime(2024, 9, 20),
                datetime(2024, 12, 10),
                datetime(2025, 1, 15)
            ],
            'Total': [5000, 5500, 6000, 6200]
        })

        budget_df = create_sample_budget_data()
        income_df = create_sample_income_data()

        budgets = [(datetime(2024, 4, 7), budget_df)]
        income = [(datetime(2024, 4, 7), income_df)]

        # Test prediction starting from each balance date
        for idx, row in balance.iterrows():
            test_date = row['Date']
            test_balance = row['Total']

            result = generate_predicted_balance_timeline(
                balance,
                budgets,
                income,
                prediction_start_date=test_date,
                prediction_start_balance=test_balance
            )

            # Verify the timeline starts from the specified date or later
            assert result['Date'].min() >= test_date, \
                f"Timeline should start from {test_date} or later, but starts from {result['Date'].min()}"

            # Find the first prediction point
            first_prediction = result.iloc[0]

            # The first prediction should be close to the start date (within the same month)
            assert first_prediction['Date'].year == test_date.year, \
                f"First prediction year {first_prediction['Date'].year} should match start year {test_date.year}"
            assert first_prediction['Date'].month == test_date.month, \
                f"First prediction month {first_prediction['Date'].month} should match start month {test_date.month}"

            print(f"✓ Test passed for {test_date.strftime('%Y-%m-%d')}: First prediction at {first_prediction['Date'].strftime('%Y-%m-%d')}")

    def test_december_2024_specific_case(self):
        """Specific test for December 2024 issue reported by user"""
        # Create balance data similar to what user might have
        balance = pd.DataFrame({
            'Date': [
                datetime(2024, 6, 15),
                datetime(2024, 9, 20),
                datetime(2024, 12, 10),  # December 2024 - the problematic date
                datetime(2025, 1, 15)
            ],
            'Total': [5000, 5500, 6000, 6200]
        })

        budget_df = create_sample_budget_data()
        income_df = create_sample_income_data()

        budgets = [(datetime(2024, 4, 7), budget_df)]
        income = [(datetime(2024, 4, 7), income_df)]

        # Specifically test December 2024
        dec_2024_date = datetime(2024, 12, 10)
        dec_2024_balance = 6000

        result = generate_predicted_balance_timeline(
            balance,
            budgets,
            income,
            prediction_start_date=dec_2024_date,
            prediction_start_balance=dec_2024_balance
        )

        # Debug output
        print(f"\nDecember 2024 Test:")
        print(f"Requested start: {dec_2024_date.strftime('%Y-%m-%d')}")
        print(f"First 5 prediction dates:")
        for i in range(min(5, len(result))):
            print(f"  {i}: {result.iloc[i]['Date'].strftime('%Y-%m-%d')} - £{result.iloc[i]['Predicted Balance']:.2f}")

        # Check the first prediction date
        first_date = result['Date'].min()
        print(f"First prediction date: {first_date.strftime('%Y-%m-%d')}")

        # The first date should match the requested start date exactly
        assert first_date == dec_2024_date, \
            f"Expected start date {dec_2024_date.strftime('%Y-%m-%d')}, got {first_date.strftime('%Y-%m-%d')}"

    def test_prediction_end_date_matches_last_recording(self):
        """Test that predictions end at or near the last balance recording date"""
        # Create balance data with specific dates
        balance = pd.DataFrame({
            'Date': [
                datetime(2024, 6, 15),
                datetime(2024, 9, 20),
                datetime(2024, 12, 10),
                datetime(2025, 1, 15)  # Last recording
            ],
            'Total': [5000, 5500, 6000, 6200]
        })

        budget_df = create_sample_budget_data()
        income_df = create_sample_income_data()

        budgets = [(datetime(2024, 4, 7), budget_df)]
        income = [(datetime(2024, 4, 7), income_df)]

        # Test with second-to-last as start (default behavior)
        second_to_last_date = datetime(2024, 12, 10)
        last_recording_date = datetime(2025, 1, 15)

        result = generate_predicted_balance_timeline(
            balance,
            budgets,
            income,
            prediction_start_date=second_to_last_date,
            prediction_start_balance=6000
        )

        # Debug output
        print(f"\nEnd Date Test:")
        print(f"Last balance recording: {last_recording_date.strftime('%Y-%m-%d')}")
        print(f"Last 5 prediction dates:")
        for i in range(max(0, len(result) - 5), len(result)):
            print(f"  {i}: {result.iloc[i]['Date'].strftime('%Y-%m-%d')} - £{result.iloc[i]['Predicted Balance']:.2f}")

        last_prediction_date = result['Date'].max()
        print(f"Last prediction date: {last_prediction_date.strftime('%Y-%m-%d')}")

        # Check that the prediction timeline includes or ends near the last recording
        # The timeline should either:
        # 1. Include the exact last recording date, OR
        # 2. Have a prediction date very close to it (within a few days)

        dates_in_timeline = result['Date'].values

        # Check if last recording date is in the timeline
        has_exact_date = any(pd.Timestamp(d).date() == last_recording_date.date() for d in dates_in_timeline)

        if not has_exact_date:
            # Check if there's a date close to the last recording (within 5 days)
            closest_date = min(dates_in_timeline, key=lambda d: abs((pd.Timestamp(d) - last_recording_date).total_seconds()))
            days_difference = abs((pd.Timestamp(closest_date) - last_recording_date).days)

            print(f"Closest date to last recording: {pd.Timestamp(closest_date).strftime('%Y-%m-%d')} ({days_difference} days difference)")

            assert days_difference <= 5, \
                f"No prediction date near last recording {last_recording_date.strftime('%Y-%m-%d')}. Closest is {days_difference} days away."
        else:
            print(f"✓ Timeline includes exact last recording date: {last_recording_date.strftime('%Y-%m-%d')}")

        # CRITICAL: Check that NO predictions are made after the last recording
        dates_after_last = [d for d in dates_in_timeline if pd.Timestamp(d) > last_recording_date]
        if dates_after_last:
            print(f"\n❌ ERROR: Found {len(dates_after_last)} predictions AFTER last recording:")
            for d in dates_after_last:
                print(f"  - {pd.Timestamp(d).strftime('%Y-%m-%d')}")

        assert len(dates_after_last) == 0, \
            f"Predictions should NOT extend past last recording {last_recording_date.strftime('%Y-%m-%d')}. " \
            f"Found {len(dates_after_last)} dates after: {[pd.Timestamp(d).strftime('%Y-%m-%d') for d in dates_after_last]}"
