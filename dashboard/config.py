import os
from backend.calculations.models import DataConfig


def get_base_path() -> str:
    """Auto-detect the correct base path for data files."""
    # An explicit override wins: point BUDGET_DATA_DIR at a separate
    # (private) data repo to keep financial CSVs out of this code repo.
    env_path = os.environ.get("BUDGET_DATA_DIR")
    if env_path:
        return env_path
    # Check if we're in the dashboard directory
    if os.path.exists("budgets") and os.path.exists("income"):
        return "."
    # Check if data is in parent directory
    elif os.path.exists("../budgets") and os.path.exists("../income"):
        return ".."
    # Check if we're in the project root
    elif os.path.exists("./budgets") and os.path.exists("./income"):
        return "."
    else:
        # Default to parent directory
        return ".."


# Default configuration for the dashboard
DEFAULT_CONFIG = DataConfig(base_path=get_base_path())


# Application settings
APP_CONFIG = {
    "page_title": "Personal Budget Dashboard",
    "page_icon": "💰",
    "layout": "wide"
}
