import os
from typing import Tuple
from datetime import datetime
import pandas as pd
from dataclasses import dataclass, field

# Load a repo-root .env (if present) so BUDGET_DATA_DIR can live in a file
# instead of being exported manually. Loaded here because this module is the
# common import for both the FastAPI backend and the Streamlit dashboard.
try:
    from dotenv import load_dotenv

    _REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(_REPO_ROOT, ".env"))
except ImportError:
    pass


Budget = Tuple[datetime, pd.DataFrame]
Income = Tuple[datetime, pd.DataFrame]


@dataclass(frozen=True)
class DataConfig:
    # Point BUDGET_DATA_DIR at a separate (private) data repo to keep
    # financial CSVs out of this public code repo. Falls back to "..".
    base_path: str = field(default_factory=lambda: os.environ.get("BUDGET_DATA_DIR", ".."))
    budgets_dir: str = "budgets"
    income_dir: str = "income"
    balance_file: str = "balance_record.csv"
