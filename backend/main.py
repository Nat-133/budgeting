from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
from datetime import datetime

from models import (
    HealthResponse,
    AccountBalance,
    BudgetFile,
    BudgetItem,
    IncomeFile,
    IncomeItem,
    PredictionResult,
    PredictionTimeline,
    BalanceAnalysis,
    SawtoothPrediction,
    SawtoothTimeline
)
from calculations.loaders import load_all_data, DataConfig
from calculations.balance_analyzer import calculate_balance_analysis, generate_predicted_balance_timeline
from calculations.sawtooth_predictor import generate_sawtooth_balance_timeline

app = FastAPI(title="Budget Dashboard API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for loaded data
_data_cache = None
_cache_timestamp = None


def get_data():
    """Load and cache budget/income/balance data"""
    global _data_cache, _cache_timestamp

    # Simple cache invalidation after 5 minutes
    import time
    current_time = time.time()
    if _data_cache is None or _cache_timestamp is None or (current_time - _cache_timestamp) > 300:
        config = DataConfig()
        _data_cache = load_all_data(config)
        _cache_timestamp = current_time

    return _data_cache


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/balance", response_model=List[AccountBalance])
async def get_balance():
    """Get all balance records with dynamic account detection"""
    try:
        budgets, income, balance = get_data()

        # Dynamically detect account columns (all columns except Date and Total)
        account_columns = [col for col in balance.columns if col not in ['Date', 'Total']]

        records = []
        for _, row in balance.iterrows():
            # Build accounts dictionary dynamically
            accounts = {}
            for col in account_columns:
                # Normalize column name: lowercase and replace spaces with underscores
                account_key = col.lower().replace(' ', '_')
                accounts[account_key] = float(row.get(col, 0))

            records.append({
                "date": row["Date"].strftime("%Y-%m-%d"),
                "accounts": accounts,
                "total": float(row["Total"])
            })

        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/budgets", response_model=List[BudgetFile])
async def get_budgets():
    """Get all budget files with items"""
    try:
        budgets, income, balance = get_data()

        budget_list = []
        for date, df in budgets:
            items = []
            for idx, row in df.iterrows():
                items.append({
                    "name": idx,
                    "schedule": row["schedule"],
                    "cost": float(row["cost"]),
                    "category": row["category"]
                })

            total = df["cost"].sum()
            budget_list.append({
                "date": date.strftime("%Y-%m-%d"),
                "items": items,
                "total": float(total)
            })

        return budget_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/income", response_model=List[IncomeFile])
async def get_income():
    """Get all income files with items"""
    try:
        budgets, income, balance = get_data()

        income_list = []
        for date, df in income:
            items = []
            for idx, row in df.iterrows():
                items.append({
                    "name": idx,
                    "schedule": row["schedule"],
                    "income": float(row["income"]),
                    "category": row["category"]
                })

            total = df["income"].sum()
            income_list.append({
                "date": date.strftime("%Y-%m-%d"),
                "items": items,
                "total": float(total)
            })

        return income_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/all", response_model=List[PredictionResult])
async def get_all_predictions():
    """Pre-calculate predictions for all balance recording points"""
    try:
        budgets, income, balance = get_data()

        predictions = []
        for _, row in balance.iterrows():
            start_date = row["Date"]
            start_balance = row["Total"]

            # Generate prediction timeline from this point
            timeline_df = generate_predicted_balance_timeline(
                balance,
                budgets,
                income,
                prediction_start_date=start_date,
                prediction_start_balance=start_balance
            )

            predictions.append({
                "startDate": start_date.strftime("%Y-%m-%d"),
                "startBalance": float(start_balance),
                "timeline": {
                    "dates": [d.strftime("%Y-%m-%d") for d in timeline_df["Date"]],
                    "balances": [float(b) for b in timeline_df["Predicted Balance"]]
                }
            })

        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/balance-analysis", response_model=BalanceAnalysis)
async def get_balance_analysis():
    """Get comprehensive balance analysis"""
    try:
        budgets, income, balance = get_data()

        analysis_df = calculate_balance_analysis(balance, budgets, income)

        # Calculate aggregate metrics
        avg_saving_rate = analysis_df["saving rate since last recording"].mean()
        avg_spending = analysis_df["actual spend since last recording"].mean()

        # Get latest predicted vs actual
        latest_deficit = analysis_df["predicted total deficit"].iloc[-1]

        return {
            "savingRate": float(avg_saving_rate) if pd.notna(avg_saving_rate) else 0.0,
            "averageMonthlySpending": float(avg_spending) if pd.notna(avg_spending) else 0.0,
            "predictedVsActual": {
                "deficit": float(latest_deficit) if pd.notna(latest_deficit) else 0.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/balance-analysis-detailed")
async def get_balance_analysis_detailed():
    """Get detailed balance analysis with time series data"""
    try:
        budgets, income, balance = get_data()

        analysis_df = calculate_balance_analysis(balance, budgets, income)

        # Return time series data
        return {
            "dates": [d.strftime("%Y-%m-%d") for d in analysis_df["Date"]],
            "actualSavingRate": [float(x) if pd.notna(x) else None for x in analysis_df["saving rate since last recording"]],
            "predictedSavingRate": [float(x) if pd.notna(x) else None for x in analysis_df["predicted saving rate"]],
            "actualSpendingRate": [float(x) if pd.notna(x) else None for x in analysis_df["actual spending rate since last recording (£/m)"]],
            "predictedSpendingRate": [float(x) if pd.notna(x) else None for x in analysis_df["predicted spending rate since last recording (£/m)"]],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cache/invalidate")
async def invalidate_cache():
    """Manually invalidate the data cache"""
    global _data_cache, _cache_timestamp
    _data_cache = None
    _cache_timestamp = None
    return {"status": "cache invalidated"}


@app.get("/api/predictions/sawtooth/all", response_model=List[SawtoothPrediction])
async def get_all_sawtooth_predictions():
    """Pre-calculate sawtooth predictions for all balance recording points.

    Each prediction runs from its starting point to the last recorded balance date.

    Returns:
        List of sawtooth predictions, one for each balance recording point
    """
    try:
        budgets, income, balance = get_data()

        predictions = []
        for _, row in balance.iterrows():
            start_date = row["Date"]
            start_balance = row["Total"]

            # Generate sawtooth timeline from this point to the last recorded date
            timeline_df = generate_sawtooth_balance_timeline(
                balance,
                budgets,
                income,
                prediction_start_date=start_date,
                prediction_start_balance=start_balance
            )

            predictions.append({
                "startDate": start_date.strftime("%Y-%m-%d"),
                "startBalance": float(start_balance),
                "timeline": {
                    "dates": [d.strftime("%Y-%m-%d") for d in timeline_df["Date"]],
                    "balances": [float(b) for b in timeline_df["Predicted Balance"]],
                    "incomeEvents": [float(i) for i in timeline_df["Income Event"]],
                    "spendingEvents": [float(s) for s in timeline_df["Spending Event"]]
                }
            })

        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
