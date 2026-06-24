import axios from 'axios';
import type {
  AccountBalance,
  BudgetFile,
  IncomeFile,
  PredictionResult,
  BalanceAnalysis,
  SawtoothPrediction,
} from '../types/index';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  health: () => apiClient.get('/api/health'),

  getBalance: () =>
    apiClient.get<AccountBalance[]>('/api/balance'),

  getBudgets: () =>
    apiClient.get<BudgetFile[]>('/api/budgets'),

  getIncome: () =>
    apiClient.get<IncomeFile[]>('/api/income'),

  getAllPredictions: () =>
    apiClient.get<PredictionResult[]>('/api/predictions/all'),

  getBalanceAnalysis: () =>
    apiClient.get<BalanceAnalysis>('/api/balance-analysis'),

  getBalanceAnalysisDetailed: () =>
    apiClient.get('/api/balance-analysis-detailed'),

  getAllSawtoothPredictions: () =>
    apiClient.get<SawtoothPrediction[]>('/api/predictions/sawtooth/all'),

  invalidateCache: () =>
    apiClient.post('/api/cache/invalidate'),
};

export default api;
