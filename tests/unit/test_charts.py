import pytest
import pandas as pd
import plotly.graph_objects as go
from dashboard.visualization.charts import (
    create_budget_pie_chart,
    create_balance_trend_chart,
    create_saving_rate_chart,
    create_prediction_chart
)
from ..fixtures.sample_data import create_sample_budget_data, create_sample_balance_data


class TestCharts:
    def test_create_budget_pie_chart(self):
        budget_df = create_sample_budget_data()
        fig = create_budget_pie_chart(budget_df)

        assert isinstance(fig, go.Figure)

        # Should have a title
        assert fig.layout.title.text == 'Monthly Expenditure by Category'

        # Should have pie chart data
        assert len(fig.data) > 0
        assert isinstance(fig.data[0], go.Pie)

    def test_create_balance_trend_chart(self):
        balance = create_sample_balance_data()
        balance['Total'] = balance.drop(columns=['Date']).sum(axis=1)

        # Add minimal required columns for the chart
        balance['predicted total from last recording'] = balance['Total'] * 0.9

        fig = create_balance_trend_chart(balance)

        assert isinstance(fig, go.Figure)

        # Should have a title and labels
        assert fig.layout.title.text == 'Balance Tracking'
        assert fig.layout.xaxis.title.text == 'Date'
        assert fig.layout.yaxis.title.text == 'Balance (£)'

        # Should have at least one trace (Actual Balance)
        assert len(fig.data) >= 1

    def test_create_saving_rate_chart(self):
        balance = create_sample_balance_data()
        balance['Total'] = balance.drop(columns=['Date']).sum(axis=1)

        # Add required columns for the chart
        balance['saving rate since last recording'] = [None, 100, 200]
        balance['predicted saving rate'] = [None, 150, 180]

        fig = create_saving_rate_chart(balance)

        assert isinstance(fig, go.Figure)

        assert fig.layout.title.text == 'Monthly Saving Rate'
        assert fig.layout.xaxis.title.text == 'Date'
        assert fig.layout.yaxis.title.text == 'Monthly Saving Rate (£)'

        # Should have at least one trace
        assert len(fig.data) >= 1

    def test_create_prediction_chart(self):
        balance = create_sample_balance_data()
        balance['Total'] = balance.drop(columns=['Date']).sum(axis=1)

        # Create simple predicted timeline
        predicted_timeline = pd.DataFrame({
            'Date': balance['Date'],
            'Predicted Balance': balance['Total'] * 1.1
        })

        fig = create_prediction_chart(balance, predicted_timeline)

        assert isinstance(fig, go.Figure)

        assert 'Balance Predictions' in fig.layout.title.text
        assert fig.layout.xaxis.title.text == 'Date'
        assert fig.layout.yaxis.title.text == 'Balance (£)'

        # Should have at least two traces (Actual and Predicted)
        assert len(fig.data) >= 2

    def test_create_prediction_chart_with_start_date(self):
        balance = create_sample_balance_data()
        balance['Total'] = balance.drop(columns=['Date']).sum(axis=1)

        # Create simple predicted timeline
        predicted_timeline = pd.DataFrame({
            'Date': balance['Date'],
            'Predicted Balance': balance['Total'] * 1.1
        })

        prediction_start_date = balance['Date'].iloc[0]
        fig = create_prediction_chart(balance, predicted_timeline, prediction_start_date)

        assert isinstance(fig, go.Figure)

        # Should have two traces (Predicted and Actual)
        assert len(fig.data) == 2
