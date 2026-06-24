import pytest
import pandas as pd
from datetime import datetime
from dashboard.data.loaders import (
    remove_readme,
    parse_budget_date,
    get_budget,
    get_income,
    load_balance_data,
    load_all_data
)
from ..fixtures.sample_data import create_test_data_config, cleanup_test_data


class TestDataLoaders:
    def test_remove_readme(self):
        file_list = ["2024-01-01-budget.csv", "readme.md", "2024-02-01-budget.csv"]
        result = remove_readme(file_list)
        assert result == ["2024-01-01-budget.csv", "2024-02-01-budget.csv"]

    def test_parse_budget_date(self):
        filename = "2024-04-07-budget.csv"
        result = parse_budget_date(filename)
        expected = datetime(2024, 4, 7)
        assert result == expected

    def test_get_budget(self):
        config, temp_dir = create_test_data_config()
        try:
            date, df = get_budget("2024-04-07-budget.csv", config)

            assert date == datetime(2024, 4, 7)
            assert isinstance(df, pd.DataFrame)
            assert "cost" in df.columns
            assert "Housing" in df.index
            assert df.loc["Housing", "cost"] == 800.00
        finally:
            cleanup_test_data(temp_dir)

    def test_get_income(self):
        config, temp_dir = create_test_data_config()
        try:
            date, df = get_income("2024-04-07-income.csv", config)

            assert date == datetime(2024, 4, 7)
            assert isinstance(df, pd.DataFrame)
            assert "income" in df.columns
            assert "Primary Income" in df.index
            assert df.loc["Primary Income", "income"] == 3500.00
        finally:
            cleanup_test_data(temp_dir)

    def test_load_balance_data(self):
        config, temp_dir = create_test_data_config()
        try:
            balance = load_balance_data(config)

            assert isinstance(balance, pd.DataFrame)
            assert "Date" in balance.columns
            assert "Total" in balance.columns
            assert len(balance) == 3
            assert balance["Total"].iloc[0] > 15000  # Should sum all accounts
        finally:
            cleanup_test_data(temp_dir)

    def test_load_all_data(self):
        config, temp_dir = create_test_data_config()
        try:
            budgets, income, balance = load_all_data(config)

            assert len(budgets) == 1
            assert len(income) == 1
            assert isinstance(balance, pd.DataFrame)

            # Check structure of returned data
            budget_date, budget_df = budgets[0]
            assert budget_date == datetime(2024, 4, 7)
            assert isinstance(budget_df, pd.DataFrame)

            income_date, income_df = income[0]
            assert income_date == datetime(2024, 4, 7)
            assert isinstance(income_df, pd.DataFrame)
        finally:
            cleanup_test_data(temp_dir)
