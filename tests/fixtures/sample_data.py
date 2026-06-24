import pandas as pd
from datetime import datetime
import os
import tempfile
from typing import Tuple
from backend.calculations.models import Budget, Income, DataConfig


def create_sample_budget_data() -> pd.DataFrame:
    """Create anonymized test budget data with generic items and amounts."""
    return pd.DataFrame({
        'schedule': ['monthly', 'monthly', 'monthly', 'monthly'],
        'cost': [800.00, 150.50, 50.25, 100.75],
        'category': ['housing', 'utilities', 'utilities', 'services']
    }, index=['Housing', 'Utility A', 'Utility B', 'Service Fee'])


def create_sample_income_data() -> pd.DataFrame:
    """Create anonymized test income data with generic sources."""
    return pd.DataFrame({
        'schedule': ['monthly'],
        'income': [3500.00],
        'category': ['Employment']
    }, index=['Primary Income'])


def create_sample_balance_data() -> pd.DataFrame:
    """Create anonymized test balance data with generic bank accounts."""
    return pd.DataFrame({
        'Date': pd.to_datetime(['2024-01-15', '2024-02-15', '2024-03-15']),
        'Bank A': [10000.00, 10500.00, 11000.00],
        'Bank B': [5000.00, 5200.00, 5400.00],
        'Bank C': [500.00, 550.00, 600.00],
        'Bank D': [100.00, 120.00, 140.00]
    })


def create_test_data_config() -> Tuple[DataConfig, str]:
    temp_dir = tempfile.mkdtemp()
    config = DataConfig(base_path=temp_dir)

    # Create directories
    os.makedirs(os.path.join(temp_dir, "budgets"))
    os.makedirs(os.path.join(temp_dir, "income"))

    # Create sample budget files
    budget_data = create_sample_budget_data()
    budget_data.to_csv(os.path.join(temp_dir, "budgets", "2024-04-07-budget.csv"), index_label="item")

    # Create sample income files
    income_data = create_sample_income_data()
    income_data.to_csv(os.path.join(temp_dir, "income", "2024-04-07-income.csv"), index_label="item")

    # Create sample balance file
    balance_data = create_sample_balance_data()
    balance_data.to_csv(os.path.join(temp_dir, "balence_record.csv"), index=False)

    return config, temp_dir


def cleanup_test_data(temp_dir: str):
    import shutil
    shutil.rmtree(temp_dir)
