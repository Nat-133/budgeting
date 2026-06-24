# Budget Dashboard

A Streamlit web dashboard for visualizing and analyzing personal budgeting data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run app.py
```

## Features

- **Budget Breakdown**: Interactive pie charts showing spending by category and detailed budget items
- **Balance Trends**: Track actual vs predicted balance over time
- **Saving Analysis**: Analyze saving rates and spending patterns
- **Future Predictions**: Visualize predicted balance trends

## Data Requirements

The dashboard expects data files in the parent directory:
- `budgets/YYYY-MM-DD-budget.csv` files
- `income/YYYY-MM-DD-income.csv` files
- `balence_record.csv` file

## Usage

The dashboard will automatically load and analyze your budget data, providing interactive visualizations and insights into your financial patterns.