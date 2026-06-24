import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import type { PredictionResult, AccountBalance } from '../types/index';

interface PredictionChartProps {
  balance: AccountBalance[];
  predictions: PredictionResult[];
}

const PredictionChart: React.FC<PredictionChartProps> = ({
  balance,
  predictions,
}) => {
  // Default to second-to-last balance point
  const defaultIndex = balance.length >= 2 ? balance.length - 2 : 0;
  const [selectedIndex, setSelectedIndex] = useState(defaultIndex);

  if (!balance || balance.length === 0 || !predictions || predictions.length === 0) {
    return <div>Loading predictions...</div>;
  }

  const selectedPrediction = predictions[selectedIndex];

  // Calculate max and min values across ALL predictions and actual balances
  const allPredictedBalances = predictions.flatMap(p => p.timeline.balances);
  const allActualBalances = balance.map(b => b.total);
  const allBalances = [...allPredictedBalances, ...allActualBalances];

  const maxBalance = Math.max(...allBalances);
  const minBalance = Math.min(...allBalances);

  // Add 5% padding to the range for better visualization
  const padding = (maxBalance - minBalance) * 0.05;
  const yAxisMax = maxBalance + padding;
  const yAxisMin = minBalance - padding;

  // Handle click on balance point
  const handlePointClick = (event: any) => {
    if (event.points && event.points.length > 0) {
      const pointIndex = event.points[0].pointIndex;
      setSelectedIndex(pointIndex);
    }
  };

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <h3>Predictions</h3>
      <p>
        <strong>Predicting from:</strong> {selectedPrediction.startDate} (£
        {selectedPrediction.startBalance.toFixed(2)})
      </p>
      <p style={{ color: '#666', fontSize: '14px' }}>
        Click any blue point to see predictions from that date
      </p>

      <Plot
        data={[
          // Prediction line (orange, dotted)
          {
            x: selectedPrediction.timeline.dates,
            y: selectedPrediction.timeline.balances,
            type: 'scatter',
            mode: 'lines',
            name: 'Predicted Balance',
            line: {
              color: 'rgb(255, 127, 14)',
              dash: 'dot',
              width: 2,
            },
            hovertemplate: '<b>Date:</b> %{x}<br><b>Predicted:</b> £%{y:,.2f}<extra></extra>',
          },
          // Actual balance line (blue, with markers on top)
          {
            x: balance.map((b) => b.date),
            y: balance.map((b) => b.total),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Actual Balance',
            line: {
              color: 'rgb(31, 119, 180)',
              width: 3,
            },
            marker: {
              size: 8,
              color: 'rgb(31, 119, 180)',
            },
            hovertemplate: '<b>Date:</b> %{x}<br><b>Actual:</b> £%{y:,.2f}<extra></extra>',
          },
        ]}
        layout={{
          title: `Balance Predictions (from ${selectedPrediction.startDate})`,
          xaxis: {
            title: 'Date',
            type: 'date',
          },
          yaxis: {
            title: 'Balance (£)',
            tickformat: ',.2f',
            range: [yAxisMin, yAxisMax],
            fixedrange: false,
          },
          hovermode: 'closest',
          showlegend: true,
          autosize: true,
          margin: {
            l: 80,
            r: 50,
            t: 80,
            b: 100,
          },
        }}
        config={{
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        }}
        style={{ width: '100%', height: '60vh' }}
        onClick={handlePointClick}
        useResizeHandler={true}
      />
    </div>
  );
};

export default PredictionChart;
