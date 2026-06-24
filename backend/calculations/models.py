from typing import Tuple
from datetime import datetime
import pandas as pd
from dataclasses import dataclass


Budget = Tuple[datetime, pd.DataFrame]
Income = Tuple[datetime, pd.DataFrame]


@dataclass(frozen=True)
class DataConfig:
    base_path: str = ".."
    budgets_dir: str = "budgets"
    income_dir: str = "income"
    balance_file: str = "balence_record.csv"
