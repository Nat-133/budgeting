# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal budgeting analysis system built using Python. The project tracks income, expenses, and account balances over time, providing visualizations and analysis of financial patterns.
It is based upon a previous jupyter notebook version, but has now been ported to the new dashboard system.

## Core Architecture

### Data Structure
- **Budget CSV files** (`budgets/YYYY-MM-DD-budget.csv`): Monthly expense data with columns: item, schedule, cost, category
- **Income CSV files** (`income/YYYY-MM-DD-income.csv`): Monthly income data with columns: item, schedule, income, category
- **Balance record** (`balence_record.csv`): Account balance snapshots across multiple accounts (Nationwide, Secure trust bank, Monzo, Revolut)

### Main Analysis Notebook
The primary analysis is done in `budget.ipynb` which:

1. **Data Loading**: Parses dated budget and income CSV files using filename conventions
2. **Financial Calculations**:
   - Computes fractional months between dates using `fractional_months_between()`
   - Calculates expected spending/income between date ranges
   - Tracks actual vs predicted spending patterns
3. **Visualization**: Creates pie charts for budget categories and time-series plots for balance tracking
4. **Analysis Features**:
   - Spending deficit analysis (predicted vs actual)
   - Saving rate calculations
   - Balance prediction with confidence intervals

### Key Functions
- `get_budget(filename)` / `get_income(filename)`: Load and parse CSV files
- `budgeted_spending_between_dates()`: Calculate expected spending over date ranges
- `income_between_dates()`: Calculate expected income over date ranges
- `fractional_months_between()`: Precise month calculations accounting for partial months

## Development Environment

### Dependencies
The project uses these Python libraries (install via pip):
- pandas, numpy: Data manipulation and analysis
- matplotlib: Plotting and visualization
- ipydatagrid: Interactive grid widgets for Jupyter
- dateutil: Advanced date manipulation

### Running the Analysis
1. Ensure Jupyter is installed: `pip install jupyter`
2. Start Jupyter: `jupyter notebook` or `jupyter lab`
3. Open `budget.ipynb` and run cells sequentially

### Data Entry Workflow
1. Create new budget files in `budgets/` with format: `YYYY-MM-DD-budget.csv`
2. Create corresponding income files in `income/` with format: `YYYY-MM-DD-income.csv`
3. Update `balence_record.csv` with new account balance snapshots
4. Re-run notebook to generate updated analysis

## File Structure Notes
- `do_not_commit/` contains sensitive financial data that should never be committed
- Date formatting in filenames is critical for the parsing logic
- The notebook expects at least one budget and one income file to exist

## Known Issues
- There's a datetime/date type mismatch error in the balance analysis section that needs fixing
- The notebook contains some cells with calculation errors that interrupt the flow
