import streamlit as st
from config import DEFAULT_CONFIG, APP_CONFIG
from data.loaders import load_all_data
from backend.calculations.balance_analyzer import calculate_balance_analysis
from ui.components import (
    render_metrics_row,
    render_budget_breakdown_tab,
    render_saving_analysis_tab,
    render_predictions_tab,
    render_raw_data_expander,
    render_error_messages
)

st.set_page_config(**APP_CONFIG)

st.title("💰 Personal Budget Dashboard")

try:
    budgets, income, balance = load_all_data(DEFAULT_CONFIG)

    if not budgets:
        st.error("No budget CSV files found. Please add budget files to the budgets/ directory.")
        st.stop()

    if not income:
        st.error("No income CSV files found. Please add income files to the income/ directory.")
        st.stop()

    current_budget_date, current_budget = budgets[-1]
    current_income_date, current_income = income[-1]

    render_metrics_row(current_budget, current_income, balance, current_budget_date, current_income_date)

    balance_analysis = calculate_balance_analysis(balance, budgets, income)

    tab1, tab2, tab3 = st.tabs(["📊 Budget Breakdown", "💹 Saving Analysis", "🔮 Predictions"])

    with tab1:
        render_budget_breakdown_tab(current_budget)

    with tab2:
        render_saving_analysis_tab(balance_analysis)

    with tab3:
        render_predictions_tab(balance, budgets, income)

    render_raw_data_expander(budgets, income, balance)

except FileNotFoundError as e:
    st.error(f"Data files not found: {str(e)}")
    render_error_messages()

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your data files and try again.")
