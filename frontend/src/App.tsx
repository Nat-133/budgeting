import { useState } from 'react';
import { useQuery, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import api from './api/client';
import PredictionChart from './components/PredictionChart';
import BudgetPieChart from './components/BudgetPieChart';
import SavingRateChart from './components/SavingRateChart';
import SawtoothChart from './components/SawtoothChart';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function Dashboard() {
  const [activeTab, setActiveTab] = useState('predictions');

  // Fetch all data
  const { data: balance, isLoading: balanceLoading } = useQuery({
    queryKey: ['balance'],
    queryFn: async () => {
      const response = await api.getBalance();
      return response.data;
    },
  });

  const { data: budgets, isLoading: budgetsLoading } = useQuery({
    queryKey: ['budgets'],
    queryFn: async () => {
      const response = await api.getBudgets();
      return response.data;
    },
  });

  const { data: income, isLoading: incomeLoading } = useQuery({
    queryKey: ['income'],
    queryFn: async () => {
      const response = await api.getIncome();
      return response.data;
    },
  });

  const { data: predictions, isLoading: predictionsLoading } = useQuery({
    queryKey: ['predictions'],
    queryFn: async () => {
      const response = await api.getAllPredictions();
      return response.data;
    },
  });

  const { data: analysis, isLoading: analysisLoading } = useQuery({
    queryKey: ['analysis'],
    queryFn: async () => {
      const response = await api.getBalanceAnalysis();
      return response.data;
    },
  });

  const { data: detailedAnalysis, isLoading: detailedAnalysisLoading } = useQuery({
    queryKey: ['detailedAnalysis'],
    queryFn: async () => {
      const response = await api.getBalanceAnalysisDetailed();
      return response.data;
    },
  });

  const { data: sawtoothPredictions, isLoading: sawtoothLoading } = useQuery({
    queryKey: ['sawtoothPredictions'],
    queryFn: async () => {
      const response = await api.getAllSawtoothPredictions();
      return response.data;
    },
  });

  const isLoading = balanceLoading || budgetsLoading || incomeLoading || predictionsLoading || analysisLoading || detailedAnalysisLoading || sawtoothLoading;

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading budget data...</p>
      </div>
    );
  }

  const latestBudget = budgets && budgets.length > 0 ? budgets[budgets.length - 1] : null;
  const latestIncome = income && income.length > 0 ? income[income.length - 1] : null;
  const latestBalance = balance && balance.length > 0 ? balance[balance.length - 1] : null;

  return (
    <div className="app">
      <header className="app-header">
        <h1>Budget Dashboard</h1>
        <p className="subtitle">Personal Finance Analysis</p>
      </header>

      <div className="metrics-container">
        <div className="metric-card">
          <h3>Monthly Budget</h3>
          <p className="metric-value">£{latestBudget?.total.toFixed(2) || '0.00'}</p>
          <p className="metric-date">{latestBudget?.date || 'N/A'}</p>
        </div>
        <div className="metric-card">
          <h3>Monthly Income</h3>
          <p className="metric-value">£{latestIncome?.total.toFixed(2) || '0.00'}</p>
          <p className="metric-date">{latestIncome?.date || 'N/A'}</p>
        </div>
        <div className="metric-card">
          <h3>Current Balance</h3>
          <p className="metric-value">£{latestBalance?.total.toFixed(2) || '0.00'}</p>
          <p className="metric-date">{latestBalance?.date || 'N/A'}</p>
        </div>
        <div className="metric-card">
          <h3>Avg Saving Rate</h3>
          <p className="metric-value">£{analysis?.savingRate.toFixed(2) || '0.00'}/mo</p>
          <p className="metric-date">Average</p>
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'predictions' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictions')}
        >
          Predictions
        </button>
        <button
          className={`tab ${activeTab === 'sawtooth' ? 'active' : ''}`}
          onClick={() => setActiveTab('sawtooth')}
        >
          Sawtooth Model
        </button>
        <button
          className={`tab ${activeTab === 'budget' ? 'active' : ''}`}
          onClick={() => setActiveTab('budget')}
        >
          Budget Breakdown
        </button>
        <button
          className={`tab ${activeTab === 'saving' ? 'active' : ''}`}
          onClick={() => setActiveTab('saving')}
        >
          Saving Analysis
        </button>
        <button
          className={`tab ${activeTab === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveTab('raw')}
        >
          Raw Data
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'predictions' && balance && predictions && (
          <PredictionChart balance={balance} predictions={predictions} />
        )}

        {activeTab === 'sawtooth' && sawtoothPredictions && balance && (
          <SawtoothChart predictions={sawtoothPredictions} balance={balance} />
        )}

        {activeTab === 'budget' && latestBudget && (
          <div className="budget-breakdown">
            <div className="budget-pie-container">
              <BudgetPieChart budget={latestBudget} />
            </div>
            <div className="budget-table-container">
              <h3>Budget Items ({latestBudget.date})</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Schedule</th>
                    <th>Cost</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  {latestBudget.items.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.name}</td>
                      <td>{item.schedule}</td>
                      <td>£{item.cost.toFixed(2)}</td>
                      <td>{item.category}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={2}><strong>Total</strong></td>
                    <td><strong>£{latestBudget.total.toFixed(2)}</strong></td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'saving' && detailedAnalysis && (
          <SavingRateChart data={detailedAnalysis} />
        )}

        {activeTab === 'raw' && balance && (
          <div className="raw-data">
            <h3>Balance Records</h3>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  {/* Dynamically render account column headers */}
                  {balance.length > 0 && Object.keys(balance[0].accounts).map((accountKey) => (
                    <th key={accountKey}>
                      {accountKey.split('_').map(word =>
                        word.charAt(0).toUpperCase() + word.slice(1)
                      ).join(' ')}
                    </th>
                  ))}
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {balance.map((record, idx) => (
                  <tr key={idx}>
                    <td>{record.date}</td>
                    {/* Dynamically render account values */}
                    {Object.entries(record.accounts).map(([accountKey, value]) => (
                      <td key={accountKey}>£{value.toFixed(2)}</td>
                    ))}
                    <td><strong>£{record.total.toFixed(2)}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

export default App;
