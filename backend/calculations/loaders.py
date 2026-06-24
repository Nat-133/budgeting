import pandas as pd
import os
from datetime import datetime
from typing import List, Tuple
from .models import Budget, Income, DataConfig


def remove_readme(file_list: List[str]) -> List[str]:
    return [f for f in file_list if f != "readme.md"]


def get_budget_files(config: DataConfig = DataConfig()) -> List[str]:
    return remove_readme(os.listdir(os.path.join(config.base_path, config.budgets_dir)))


def get_income_files(config: DataConfig = DataConfig()) -> List[str]:
    return remove_readme(os.listdir(os.path.join(config.base_path, config.income_dir)))


def parse_budget_date(filename: str) -> datetime:
    return datetime.strptime(filename[:10], "%Y-%m-%d")


def get_budget(filename: str, config: DataConfig = DataConfig()) -> Budget:
    file_path = os.path.join(config.base_path, config.budgets_dir, filename)
    return (parse_budget_date(filename), pd.read_csv(file_path, index_col="item"))


def get_income(filename: str, config: DataConfig = DataConfig()) -> Income:
    file_path = os.path.join(config.base_path, config.income_dir, filename)
    return (parse_budget_date(filename), pd.read_csv(file_path, index_col="item"))


def load_balance_data(config: DataConfig = DataConfig()) -> pd.DataFrame:
    balance = pd.read_csv(os.path.join(config.base_path, config.balance_file))
    balance["Date"] = pd.to_datetime(balance["Date"], format='%Y-%m-%d')
    balance['Total'] = balance.drop(columns=['Date']).sum(axis=1)
    return balance


def load_all_data(config: DataConfig = DataConfig()) -> Tuple[List[Budget], List[Income], pd.DataFrame]:
    budget_files = get_budget_files(config)
    income_files = get_income_files(config)

    budgets = [get_budget(f, config) for f in budget_files]
    income = [get_income(f, config) for f in income_files]
    balance = load_balance_data(config)

    # Sort budgets and incomes by date (ascending order)
    budgets.sort(key=lambda x: x[0])
    income.sort(key=lambda x: x[0])

    return budgets, income, balance
