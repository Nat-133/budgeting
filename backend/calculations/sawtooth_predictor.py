"""Sawtooth Balance Prediction Model

This module implements a more realistic balance prediction where:
- Income is discrete: arrives on the 1st of each month (step function)
- Spending is continuous: distributed uniformly throughout each month (linear decrease)

This creates a sawtooth pattern where balance jumps up on the 1st,
then gradually decreases throughout the month.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple
import calendar

from .models import Budget, Income
from .calculations import (
    budgeted_spending_between_dates,
    income_between_dates
)


def get_monthly_income(income_data: List[Income], target_date: datetime) -> float:
    """Calculate total monthly income at a given date.

    Uses the most recent income plan that is valid at the target date.

    Args:
        income_data: List of (datetime, DataFrame) tuples with income plans
        target_date: The date to calculate income for

    Returns:
        Total monthly income amount
    """
    # Find the most recent income plan before or at target_date
    applicable_plans = [(plan_date, df) for plan_date, df in income_data if plan_date <= target_date]

    if not applicable_plans:
        return 0.0

    # Get the most recent plan
    _, income_df = max(applicable_plans, key=lambda x: x[0])

    # Sum all monthly income (assuming schedule is already monthly)
    return income_df['income'].sum()


def get_monthly_spending(budget_data: List[Budget], target_date: datetime) -> float:
    """Calculate total monthly spending at a given date.

    Uses the most recent budget plan that is valid at the target date.

    Args:
        budget_data: List of (datetime, DataFrame) tuples with budget plans
        target_date: The date to calculate spending for

    Returns:
        Total monthly spending amount
    """
    # Find the most recent budget plan before or at target_date
    applicable_plans = [(plan_date, df) for plan_date, df in budget_data if plan_date <= target_date]

    if not applicable_plans:
        return 0.0

    # Get the most recent plan
    _, budget_df = max(applicable_plans, key=lambda x: x[0])

    # Sum all monthly costs (assuming schedule is already monthly)
    return budget_df['cost'].sum()


def get_days_in_month(year: int, month: int) -> int:
    """Get the number of days in a given month."""
    return calendar.monthrange(year, month)[1]


def calculate_spending_for_day(
    year: int,
    month: int,
    day: int,
    monthly_spending: float
) -> float:
    """Calculate spending for a single day, distributed uniformly across the month.

    Args:
        year: Year
        month: Month (1-12)
        day: Day of month (1-31)
        monthly_spending: Total spending for the month

    Returns:
        Spending amount for that day
    """
    days_in_month = get_days_in_month(year, month)
    return monthly_spending / days_in_month


def is_first_of_month(current_date: datetime) -> bool:
    """Check if the current date is the first day of a month."""
    return current_date.day == 1


def generate_sawtooth_balance_timeline(
    balance: pd.DataFrame,
    budgets: List[Budget],
    income: List[Income],
    prediction_start_date: datetime = None,
    prediction_start_balance: float = None
) -> pd.DataFrame:
    """Generate predicted balance timeline with sawtooth pattern.

    The pattern emerges from:
    - Income arriving discretely on the 1st of each month (causes jumps up)
    - Spending distributed continuously throughout the month (causes gradual decline)

    Args:
        balance: DataFrame with historical balance data
        budgets: List of budget data
        income: List of income data
        prediction_start_date: Date to start predictions from (defaults to last recording)
        prediction_start_balance: Starting balance (defaults to balance at prediction_start_date)

    Returns:
        DataFrame with columns: Date, Predicted Balance, Income Event, Spending Event
        Prediction always runs from start_date to the last recorded balance date
    """
    if prediction_start_date is None:
        # Default to last recording
        prediction_start_date = balance["Date"].max()

    if prediction_start_balance is None:
        prediction_start_balance = balance.loc[
            balance["Date"] == prediction_start_date, "Total"
        ].values[0]

    # Calculate end date - predict up to the last recorded balance date
    last_recording_date = balance["Date"].max()
    end_date = last_recording_date

    # Generate daily predictions
    dates = pd.date_range(start=prediction_start_date, end=end_date, freq='D')

    predicted_balances = []
    income_events = []
    spending_events = []
    current_balance = prediction_start_balance

    for current_date in dates:
        # Check if income arrives (1st of month)
        if is_first_of_month(current_date) and current_date > prediction_start_date:
            monthly_income = get_monthly_income(income, current_date)
            current_balance += monthly_income
            income_events.append(monthly_income)
        else:
            income_events.append(0.0)

        # Calculate daily spending (continuous throughout month)
        monthly_spending = get_monthly_spending(budgets, current_date)
        daily_spending = calculate_spending_for_day(
            current_date.year,
            current_date.month,
            current_date.day,
            monthly_spending
        )
        current_balance -= daily_spending
        spending_events.append(daily_spending)

        predicted_balances.append(current_balance)

    return pd.DataFrame({
        "Date": dates,
        "Predicted Balance": predicted_balances,
        "Income Event": income_events,
        "Spending Event": spending_events
    })


def calculate_balance_at_date(
    start_date: datetime,
    start_balance: float,
    target_date: datetime,
    budgets: List[Budget],
    income: List[Income]
) -> float:
    """Calculate the predicted balance at a specific target date using sawtooth model.

    This is useful for testing and validation without generating the full timeline.

    Args:
        start_date: Starting date for prediction
        start_balance: Balance at start_date
        target_date: Date to calculate balance for
        budgets: List of budget data
        income: List of income data

    Returns:
        Predicted balance at target_date
    """
    if target_date < start_date:
        raise ValueError("target_date must be >= start_date")

    current_balance = start_balance
    current_date = start_date

    # Iterate through each day
    while current_date <= target_date:
        # Add income on 1st of month
        if is_first_of_month(current_date) and current_date > start_date:
            monthly_income = get_monthly_income(income, current_date)
            current_balance += monthly_income

        # Subtract daily spending
        monthly_spending = get_monthly_spending(budgets, current_date)
        daily_spending = calculate_spending_for_day(
            current_date.year,
            current_date.month,
            current_date.day,
            monthly_spending
        )
        current_balance -= daily_spending

        current_date += timedelta(days=1)

    return current_balance
