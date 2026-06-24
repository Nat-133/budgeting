export interface AccountBalance {
  date: string;
  accounts: Record<string, number>;  // Dynamic accounts: {account_name: balance}
  total: number;
}

export interface BudgetItem {
  name: string;
  schedule: string;
  cost: number;
  category: string;
}

export interface BudgetFile {
  date: string;
  items: BudgetItem[];
  total: number;
}

export interface IncomeItem {
  name: string;
  schedule: string;
  income: number;
  category: string;
}

export interface IncomeFile {
  date: string;
  items: IncomeItem[];
  total: number;
}

export interface PredictionTimeline {
  dates: string[];
  balances: number[];
}

export interface PredictionResult {
  startDate: string;
  startBalance: number;
  timeline: PredictionTimeline;
}

export interface BalanceAnalysis {
  savingRate: number;
  averageMonthlySpending: number;
  predictedVsActual: {
    deficit: number;
  };
}

export interface SawtoothTimeline {
  dates: string[];
  balances: number[];
  incomeEvents: number[];
  spendingEvents: number[];
}

export interface SawtoothPrediction {
  startDate: string;
  startBalance: number;
  timeline: SawtoothTimeline;
}
