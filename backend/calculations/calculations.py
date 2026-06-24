import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import List, Tuple
import pandas as pd
from .models import Budget, Income


def fractional_months_between(last_recording_date: datetime, current_recording_date: datetime) -> float:
    delta = relativedelta(current_recording_date, last_recording_date)
    total_months = delta.years * 12 + delta.months
    days = delta.days

    if current_recording_date >= last_recording_date:
        intermediate_date = last_recording_date + relativedelta(months=total_months)
    else:
        intermediate_date = last_recording_date - relativedelta(months=abs(total_months))

    _, days_in_partial_month = calendar.monthrange(intermediate_date.year, intermediate_date.month)
    return total_months + (days / days_in_partial_month)


def budgeted_spending_between_dates(start_date: datetime, end_date: datetime, budgets: List[Budget]) -> float:
    """Calculate total budgeted spending between dates, returning a scalar sum.

    Args:
        start_date: Start date of the period
        end_date: End date of the period
        budgets: List of (datetime, DataFrame) tuples representing budgets

    Returns:
        Total spending as a float
    """
    itemized = budgeted_spending_between_dates_itemized(start_date, end_date, budgets)
    return itemized.sum() if len(itemized) > 0 else 0.0


def budgeted_spending_between_dates_itemized(start_date: datetime, end_date: datetime, budgets: List[Budget]) -> pd.Series:
    """Calculate budgeted spending between dates, returning itemized breakdown per budget item."""
    start = start_date.date() if isinstance(start_date, datetime) else start_date
    end = end_date.date() if isinstance(end_date, datetime) else end_date
    return sum_between_range(budgets, start, end)


def income_between_dates(start_date: datetime, end_date: datetime, incomes: List[Income]) -> float:
    """Calculate total income between dates, returning a scalar sum.

    Args:
        start_date: Start date of the period
        end_date: End date of the period
        incomes: List of (datetime, DataFrame) tuples representing income

    Returns:
        Total income as a float
    """
    itemized = income_between_dates_itemized(start_date, end_date, incomes)
    return itemized.sum() if len(itemized) > 0 else 0.0


def income_between_dates_itemized(start_date: datetime, end_date: datetime, incomes: List[Income]) -> pd.Series:
    """Calculate income between dates, returning itemized breakdown per income source."""
    start = start_date.date() if isinstance(start_date, datetime) else start_date
    end = end_date.date() if isinstance(end_date, datetime) else end_date
    return sum_between_range(incomes, start, end)


def _calculate_effective_date_ranges(
    cashflow_plans: List[Tuple[datetime, pd.DataFrame]],
    start: date,
    end: date
) -> List[Tuple[datetime, pd.DataFrame, date, date]]:
    """Calculate effective date ranges for each cashflow plan."""
    sorted_plans = sorted(cashflow_plans, key=lambda x: x[0])
    result = []

    for i, (plan_date, df) in enumerate(sorted_plans):
        plan_start = plan_date.date() if isinstance(plan_date, datetime) else plan_date
        effective_start = max(start, plan_start)
        effective_end = end

        if i + 1 < len(sorted_plans):
            next_plan_start = sorted_plans[i + 1][0]
            next_plan_start = next_plan_start.date() if isinstance(next_plan_start, datetime) else next_plan_start
            if next_plan_start < end:
                effective_end = min(effective_end, next_plan_start)

        if plan_start < end and effective_start < effective_end and effective_end > start:
            result.append((plan_date, df, effective_start, effective_end))

    return result


def _calculate_cashflow_for_range(
    plan_date: datetime,
    df: pd.DataFrame,
    effective_start: date,
    effective_end: date,
    is_income: bool
) -> pd.Series:
    """Calculate cashflow for a single plan within a date range."""
    start_dt = datetime.combine(effective_start, datetime.min.time())
    end_dt = datetime.combine(effective_end, datetime.min.time())
    months = fractional_months_between(start_dt, end_dt)
    value_column = "income" if is_income else "cost"
    return df[value_column] * months


def _combine_cashflow_series(series_list: List[pd.Series]) -> pd.Series:
    """Combine multiple cashflow Series, summing values for duplicate items."""
    if not series_list:
        return pd.Series(dtype=float)

    result = series_list[0].copy()
    for series in series_list[1:]:
        result = result.add(series, fill_value=0)

    return result


def sum_between_range(cashflowPlans: list[Budget] | list[Income], start: datetime.date, end: datetime.date) -> pd.Series:
    """Calculate total cashflow between dates, returning itemized breakdown."""
    cashflow_with_date_ranges = _calculate_effective_date_ranges(cashflowPlans, start, end)

    is_income = bool(cashflowPlans and "income" in cashflowPlans[0][1].columns)

    cashflow_totals = [
        _calculate_cashflow_for_range(plan_date, df, effective_start, effective_end, is_income)
        for plan_date, df, effective_start, effective_end in cashflow_with_date_ranges
    ]

    return _combine_cashflow_series(cashflow_totals)
