import streamlit as st
import pandas as pd
from typing import List, Tuple
from backend.calculations.models import Budget, Income
from visualization.charts import (
    create_budget_pie_chart,
    create_saving_rate_chart,
    create_prediction_chart
)
from visualization.formatters import apply_currency_formatting
from backend.calculations.balance_analyzer import generate_predicted_balance_timeline


def render_metrics_row(current_budget: pd.DataFrame, current_income: pd.DataFrame,
                      balance: pd.DataFrame, current_budget_date, current_income_date):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Current Monthly Budget",
            f"£{current_budget['cost'].sum():.2f}",
            f"From {current_budget_date.strftime('%Y-%m-%d')}"
        )

    with col2:
        st.metric(
            "Current Monthly Income",
            f"£{current_income['income'].sum():.2f}",
            f"From {current_income_date.strftime('%Y-%m-%d')}"
        )

    with col3:
        latest_balance = balance['Total'].iloc[-1]
        st.metric(
            "Latest Balance",
            f"£{latest_balance:.2f}",
            f"As of {balance['Date'].iloc[-1].strftime('%Y-%m-%d')}"
        )


def render_budget_breakdown_tab(current_budget: pd.DataFrame):
    st.subheader("Current Budget Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("By Category")
        fig = create_budget_pie_chart(current_budget)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Detailed Budget Items")
        budget_display = current_budget.copy()
        budget_display['cost'] = budget_display['cost'].apply(lambda x: f"£{x:.2f}")
        st.dataframe(budget_display, use_container_width=True)


def render_saving_analysis_tab(balance_analysis: pd.DataFrame):
    st.subheader("Saving Rate Analysis")

    fig = create_saving_rate_chart(balance_analysis)
    st.plotly_chart(fig, use_container_width=True)


@st.fragment
def render_predictions_tab(balance: pd.DataFrame, budgets: List[Budget], income: List[Income]):
    st.subheader("Future Balance Predictions")

    # Initialize session state for selected point
    if 'prediction_start_index' not in st.session_state:
        st.session_state.prediction_start_index = max(0, len(balance) - 2)

    try:
        # Sort balance data by date to ensure consistent indexing
        sorted_balance = balance.sort_values('Date').reset_index(drop=True)

        # Cache all predictions in session state (calculate once)
        cache_key = 'all_predictions_cache'
        if cache_key not in st.session_state:
            with st.spinner("📊 Pre-calculating all predictions... (one-time setup)"):
                all_predictions = {}
                for idx, row in sorted_balance.iterrows():
                    prediction_start_date = row['Date']
                    prediction_start_balance = row['Total']

                    predicted_timeline = generate_predicted_balance_timeline(
                        sorted_balance,
                        budgets,
                        income,
                        prediction_start_date=prediction_start_date,
                        prediction_start_balance=prediction_start_balance
                    )
                    all_predictions[idx] = (prediction_start_date, prediction_start_balance, predicted_timeline)

                st.session_state[cache_key] = all_predictions

        all_predictions = st.session_state[cache_key]

        # Get current selection
        selected_idx = st.session_state.prediction_start_index
        prediction_start_date, prediction_start_balance, predicted_timeline = all_predictions[selected_idx]

        # Create chart
        fig = create_prediction_chart(sorted_balance, predicted_timeline, prediction_start_date)

        # Display info
        st.info(f"📍 Predicting from: {prediction_start_date.strftime('%Y-%m-%d')} (Balance: £{prediction_start_balance:,.2f}) | Click any blue point to change")

        # Show chart with click events
        event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="prediction_chart")

        # Handle clicks
        if event and 'selection' in event:
            selection = event['selection']
            if 'points' in selection and selection['points']:
                point_data = selection['points'][0]
                # Actual Balance is trace 1 (second trace after prediction line)
                if point_data.get('curve_number') == 1:
                    point_index = point_data.get('point_index')
                    if point_index is not None and point_index < len(sorted_balance):
                        st.session_state.prediction_start_index = point_index
                        st.rerun()

    except Exception as e:
        st.error(f"Error generating predictions: {str(e)}")


def render_raw_data_expander(budgets: List[Budget], income: List[Income], balance: pd.DataFrame):
    with st.expander("📋 Raw Data"):
        st.subheader("Budget Files")
        for date, budget_df in budgets:
            st.write(f"**{date.strftime('%Y-%m-%d')}**")
            st.dataframe(budget_df, use_container_width=True)

        st.subheader("Income Files")
        for date, income_df in income:
            st.write(f"**{date.strftime('%Y-%m-%d')}**")
            st.dataframe(income_df, use_container_width=True)

        st.subheader("Balance Record")
        st.dataframe(balance, use_container_width=True)


def render_error_messages():
    st.error("Data files not found")
    st.info("Please ensure you have the following files in the parent directory:")
    st.markdown("- `budgets/YYYY-MM-DD-budget.csv` files")
    st.markdown("- `income/YYYY-MM-DD-income.csv` files")
    st.markdown("- `balence_record.csv` file")
