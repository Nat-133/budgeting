import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


def create_budget_pie_chart(budget_df: pd.DataFrame) -> go.Figure:
    """Create an interactive pie chart showing budget breakdown by category"""
    category_grouped = budget_df.groupby('category', sort=False)['cost'].sum()

    fig = go.Figure(data=[go.Pie(
        labels=category_grouped.index,
        values=category_grouped.values,
        hole=0,
        textposition='auto',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>£%{value:.2f}<br>%{percent}<extra></extra>'
    )])

    fig.update_layout(
        title='Monthly Expenditure by Category',
        showlegend=True,
        height=600
    )

    return fig


def create_balance_trend_chart(balance_analysis: pd.DataFrame) -> go.Figure:
    """Create an interactive line chart showing balance trends over time"""
    fig = go.Figure()

    # Actual Balance line
    fig.add_trace(go.Scatter(
        x=balance_analysis["Date"],
        y=balance_analysis["Total"],
        mode='lines+markers',
        name='Actual Balance',
        line=dict(width=2),
        marker=dict(size=8),
        hovertemplate='<b>Actual Balance</b><br>Date: %{x|%b %Y}<br>£%{y:.2f}<extra></extra>'
    ))

    # Predicted Balance line (if exists)
    if not balance_analysis["predicted total from last recording"].isna().all():
        fig.add_trace(go.Scatter(
            x=balance_analysis["Date"],
            y=balance_analysis["predicted total from last recording"],
            mode='lines',
            name='Predicted Balance',
            line=dict(dash='dash', width=2),
            opacity=0.7,
            hovertemplate='<b>Predicted Balance</b><br>Date: %{x|%b %Y}<br>£%{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        title="Balance Tracking",
        xaxis_title="Date",
        yaxis_title="Balance (£)",
        hovermode='x unified',
        height=600,
        xaxis=dict(
            tickformat='%b %Y',
            tickangle=45
        ),
        yaxis=dict(
            gridcolor='rgba(128, 128, 128, 0.2)'
        ),
        plot_bgcolor='white'
    )

    return fig


def create_saving_rate_chart(balance_analysis: pd.DataFrame) -> go.Figure:
    """Create an interactive line chart showing saving rate over time"""
    fig = go.Figure()

    valid_data = balance_analysis.dropna(subset=["saving rate since last recording"])

    if not valid_data.empty:
        # Actual Saving Rate
        fig.add_trace(go.Scatter(
            x=valid_data["Date"],
            y=valid_data["saving rate since last recording"],
            mode='lines+markers',
            name='Actual Saving Rate',
            line=dict(width=2),
            marker=dict(size=8),
            hovertemplate='<b>Actual Saving Rate</b><br>Date: %{x|%b %Y}<br>£%{y:.2f}/month<extra></extra>'
        ))

        # Predicted Saving Rate (if exists)
        if "predicted saving rate" in valid_data.columns:
            fig.add_trace(go.Scatter(
                x=valid_data["Date"],
                y=valid_data["predicted saving rate"],
                mode='lines',
                name='Predicted Saving Rate',
                line=dict(dash='dash', width=2),
                opacity=0.7,
                hovertemplate='<b>Predicted Saving Rate</b><br>Date: %{x|%b %Y}<br>£%{y:.2f}/month<extra></extra>'
            ))

    fig.update_layout(
        title="Monthly Saving Rate",
        xaxis_title="Date",
        yaxis_title="Monthly Saving Rate (£)",
        hovermode='x unified',
        height=600,
        xaxis=dict(
            tickformat='%b %Y',
            tickangle=45
        ),
        yaxis=dict(
            gridcolor='rgba(128, 128, 128, 0.2)'
        ),
        plot_bgcolor='white'
    )

    return fig


def create_prediction_chart(balance: pd.DataFrame, predicted_timeline: pd.DataFrame, prediction_start_date=None) -> go.Figure:
    """Create an interactive chart showing actual vs predicted balance

    Args:
        balance: Historical balance data
        predicted_timeline: Predicted balance timeline
        prediction_start_date: Date from which predictions start (highlighted on chart)
    """
    fig = go.Figure()

    # Predicted Balance Timeline (drawn first, so it's behind)
    fig.add_trace(go.Scatter(
        x=predicted_timeline["Date"],
        y=predicted_timeline["Predicted Balance"],
        mode='lines',
        name='Predicted Balance Timeline',
        line=dict(dash='dot', width=3, color='orange'),
        opacity=0.8,
        hovertemplate='<b>Predicted Balance</b><br>Date: %{x|%b %Y}<br>£%{y:.2f}<extra></extra>'
    ))

    # Actual Balance line (drawn second, so it's on top)
    fig.add_trace(go.Scatter(
        x=balance["Date"],
        y=balance["Total"],
        mode='lines+markers',
        name='Actual Balance',
        line=dict(width=2, color='#1f77b4'),  # Plotly default blue
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate='<b>Actual Balance</b><br>Date: %{x|%b %Y}<br>£%{y:.2f}<br><i>Click to predict from this point</i><extra></extra>'
    ))

    fig.update_layout(
        title="Balance Predictions - Click any point on the blue line to predict from that date",
        xaxis_title="Date",
        yaxis_title="Balance (£)",
        hovermode='closest',
        height=600,
        xaxis=dict(
            tickformat='%b %Y',
            tickangle=45
        ),
        yaxis=dict(
            gridcolor='rgba(128, 128, 128, 0.2)'
        ),
        plot_bgcolor='white',
        clickmode='event+select'
    )

    return fig
