from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    version: str


class AccountBalance(BaseModel):
    date: str
    accounts: Dict[str, float]  # Dynamic accounts: {account_name: balance}
    total: float


class BudgetItem(BaseModel):
    name: str
    schedule: str
    cost: float
    category: str


class BudgetFile(BaseModel):
    date: str
    items: List[BudgetItem]
    total: float


class IncomeItem(BaseModel):
    name: str
    schedule: str
    income: float
    category: str


class IncomeFile(BaseModel):
    date: str
    items: List[IncomeItem]
    total: float


class PredictionTimeline(BaseModel):
    dates: List[str]
    balances: List[float]


class PredictionResult(BaseModel):
    startDate: str
    startBalance: float
    timeline: PredictionTimeline


class BalanceAnalysis(BaseModel):
    savingRate: float
    averageMonthlySpending: float
    predictedVsActual: Dict[str, float]


class SawtoothTimeline(BaseModel):
    dates: List[str]
    balances: List[float]
    incomeEvents: List[float]
    spendingEvents: List[float]


class SawtoothPrediction(BaseModel):
    startDate: str
    startBalance: float
    timeline: SawtoothTimeline
