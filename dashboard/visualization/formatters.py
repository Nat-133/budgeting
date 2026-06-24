import pandas as pd
from typing import Any


def format_currency(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"£{value:.2f}"


def format_date(date) -> str:
    if pd.isna(date):
        return "N/A"
    return date.strftime('%Y-%m-%d')


def format_percentage(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def apply_currency_formatting(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    display_df = df.copy()
    for col in columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(format_currency)
    return display_df
