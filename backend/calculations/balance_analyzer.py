import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Tuple
from .models import Budget, Income
from .calculations import (
    fractional_months_between,
    budgeted_spending_between_dates,
    income_between_dates
)


def calculate_previous_total(balance: pd.DataFrame) -> pd.Series:
    """Calculate the previous total balance for each row."""
    return balance["Total"].shift(1)


def calculate_months_since_last_recording(dates: pd.Series) -> List[float]:
    """Calculate fractional months between consecutive recording dates."""
    date_pairs = list(zip(dates[1:], dates))
    return [np.nan] + [
        fractional_months_between(last_date, date) for date, last_date in date_pairs
    ]


def calculate_expected_income_since_last_recording(
    dates: pd.Series,
    income: List[Income]
) -> List[float]:
    """Calculate expected income between consecutive recording dates."""
    date_pairs = list(zip(dates[1:], dates))
    return [np.nan] + [
        income_between_dates(last_date, date, income) for date, last_date in date_pairs
    ]


def calculate_predicted_spend_since_last_recording(
    dates: pd.Series,
    budgets: List[Budget]
) -> List[float]:
    """Calculate predicted spending between consecutive recording dates."""
    date_pairs = list(zip(dates[1:], dates))
    return [np.nan] + [
        budgeted_spending_between_dates(last_date, date, budgets) for date, last_date in date_pairs
    ]


def calculate_actual_spend_since_last_recording(
    current_total: pd.Series,
    previous_total: pd.Series,
    expected_income: pd.Series
) -> pd.Series:
    """Calculate actual spending based on balance changes and income.

    Formula: actual_spend = previous_total + expected_income - current_total
    """
    return -current_total + previous_total + expected_income


def calculate_spending_deficit(
    predicted_spend: pd.Series,
    actual_spend: pd.Series
) -> pd.Series:
    """Calculate the difference between predicted and actual spending.

    Positive values indicate underspending (actual < predicted).
    Negative values indicate overspending (actual > predicted).
    """
    return predicted_spend - actual_spend


def calculate_spending_rate(
    spending: pd.Series,
    months: pd.Series
) -> pd.Series:
    """Calculate spending rate per month."""
    return spending / months


def calculate_predicted_total_from_last_recording(
    previous_total: pd.Series,
    expected_income: pd.Series,
    predicted_spend: pd.Series
) -> pd.Series:
    """Calculate what the balance should be based on predictions."""
    return previous_total + expected_income - predicted_spend


def calculate_predicted_total_deficit(
    actual_total: pd.Series,
    predicted_total: pd.Series
) -> pd.Series:
    """Calculate difference between actual and predicted balance."""
    return actual_total - predicted_total


def calculate_balance_change(
    current_total: pd.Series,
    previous_total: pd.Series
) -> pd.Series:
    """Calculate change in balance since last recording."""
    return current_total - previous_total


def calculate_saving_rate(
    balance_change: pd.Series,
    months: pd.Series
) -> pd.Series:
    """Calculate actual saving rate per month."""
    return balance_change / months


def calculate_predicted_saving_rate(
    expected_income: pd.Series,
    predicted_spend: pd.Series,
    months: pd.Series
) -> pd.Series:
    """Calculate predicted saving rate per month."""
    return (expected_income - predicted_spend) / months


def calculate_predicted_latest_total(
    balance: pd.DataFrame,
    latest_date: datetime,
    budgets: List[Budget],
    income: List[Income]
) -> List[float]:
    """Calculate what the latest balance should be if predictions were followed from each historical date."""
    return [
        total + income_between_dates(date, latest_date, income) -
        budgeted_spending_between_dates(date, latest_date, budgets)
        for _, (date, total) in balance[["Date", "Total"]].iterrows()
    ]


def calculate_latest_total_difference(
    latest_total: float,
    predicted_latest_total: pd.Series
) -> pd.Series:
    """Calculate difference between actual latest total and predicted from each historical point."""
    return latest_total - predicted_latest_total


def calculate_balance_analysis(balance: pd.DataFrame, budgets: List[Budget], income: List[Income]) -> pd.DataFrame:
    """Calculate comprehensive balance analysis with predictions and actuals.

    This function orchestrates all balance analysis calculations by calling
    individual calculation functions for each metric.
    """
    balance = balance.copy()
    dates = balance["Date"]

    # Basic calculations
    balance["previous total"] = calculate_previous_total(balance)
    balance["months since last recording"] = calculate_months_since_last_recording(dates)

    # Income and spending calculations
    balance["expected income since last recording"] = calculate_expected_income_since_last_recording(dates, income)
    balance["predicted spend since last recording"] = calculate_predicted_spend_since_last_recording(dates, budgets)
    balance["actual spend since last recording"] = calculate_actual_spend_since_last_recording(
        balance["Total"],
        balance["previous total"],
        balance["expected income since last recording"]
    )

    # Deficit and rate calculations
    balance["spending deficit"] = calculate_spending_deficit(
        balance["predicted spend since last recording"],
        balance["actual spend since last recording"]
    )
    balance["predicted spending rate since last recording (£/m)"] = calculate_spending_rate(
        balance["predicted spend since last recording"],
        balance["months since last recording"]
    )
    balance["actual spending rate since last recording (£/m)"] = calculate_spending_rate(
        balance["actual spend since last recording"],
        balance["months since last recording"]
    )

    # Balance predictions
    balance["predicted total from last recording"] = calculate_predicted_total_from_last_recording(
        balance["previous total"],
        balance["expected income since last recording"],
        balance["predicted spend since last recording"]
    )
    balance["predicted total deficit"] = calculate_predicted_total_deficit(
        balance["Total"],
        balance["predicted total from last recording"]
    )

    # Saving rate calculations
    balance["balance change"] = calculate_balance_change(balance["Total"], balance["previous total"])
    balance["saving rate since last recording"] = calculate_saving_rate(
        balance["balance change"],
        balance["months since last recording"]
    )
    balance["predicted saving rate"] = calculate_predicted_saving_rate(
        balance["expected income since last recording"],
        balance["predicted spend since last recording"],
        balance["months since last recording"]
    )

    # Latest total predictions
    latest_date = balance["Date"].max()
    latest_total = balance.loc[balance["Date"] == latest_date]["Total"].iloc[0]
    balance["predicted latest total"] = calculate_predicted_latest_total(balance, latest_date, budgets, income)
    balance["latest total difference"] = calculate_latest_total_difference(
        latest_total,
        balance["predicted latest total"]
    )

    return balance


def generate_predicted_balance_timeline(
    balance: pd.DataFrame,
    budgets: List[Budget],
    income: List[Income],
    prediction_start_date: datetime = None,
    prediction_start_balance: float = None
) -> pd.DataFrame:
    """Generate predicted balance timeline.

    Args:
        balance: DataFrame with historical balance data
        budgets: List of budget data
        income: List of income data
        prediction_start_date: Optional date to start predictions from (defaults to second-to-last recording)
        prediction_start_balance: Optional starting balance (defaults to balance at prediction_start_date)
    """
    if prediction_start_date is None:
        # Default to second-to-last recording
        sorted_dates = balance["Date"].sort_values()
        if len(sorted_dates) >= 2:
            prediction_start_date = sorted_dates.iloc[-2]
        else:
            prediction_start_date = sorted_dates.iloc[0]

    if prediction_start_balance is None:
        prediction_start_balance = balance.loc[balance["Date"] == prediction_start_date, "Total"].values[0]

    last_recording_date = balance["Date"].max()
    end_date = last_recording_date  # Don't predict past the last recording

    # Generate daily predictions from start to end
    dates = pd.date_range(start=prediction_start_date, end=end_date, freq='D').tolist()

    # Calculate predicted balances for each date
    predicted_balances = []
    previous_date = None
    current_balance = prediction_start_balance

    for date in dates:
        if previous_date is None:
            # First entry is the starting point
            predicted_balances.append(prediction_start_balance)
            previous_date = date
        else:
            # Calculate predicted balance for this date
            predicted_income = income_between_dates(previous_date, date, income)
            spend = budgeted_spending_between_dates(previous_date, date, budgets)
            current_balance += predicted_income - spend
            predicted_balances.append(current_balance)
            previous_date = date

    return pd.DataFrame({
        "Date": dates,
        "Predicted Balance": predicted_balances
    })

