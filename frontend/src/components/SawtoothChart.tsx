import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import type { SawtoothPrediction, AccountBalance } from '../types/index';

interface SawtoothChartProps {
  predictions: SawtoothPrediction[];
  balance: AccountBalance[];
}

const SawtoothChart: React.FC<SawtoothChartProps> = ({
  predictions,
  balance,
}) => {
  // Default to second-to-last balance point
  const defaultIndex = balance.length >= 2 ? balance.length - 2 : 0;
  const [selectedIndex, setSelectedIndex] = useState(defaultIndex);

  if (!predictions || predictions.length === 0) {
    return <div>Loading sawtooth predictions...</div>;
  }

  const selectedPrediction = predictions[selectedIndex];

  // Handle click on balance point
  const handlePointClick = (event: any) => {
    if (event.points && event.points.length > 0) {
      const point = event.points[0];
      // Only handle clicks on the actual balance line (trace index 1)
      // Trace 0 is the prediction line, trace 1 is the actual balance
      if (point.curveNumber === 1) {
        const pointIndex = point.pointIndex;
        setSelectedIndex(pointIndex);
      }
    }
  };

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <h3>Sawtooth Balance Prediction</h3>
      <p>
        <strong>Predicting from:</strong> {selectedPrediction.startDate} (£
        {selectedPrediction.startBalance.toFixed(2)})
      </p>
      <p style={{ color: '#666', fontSize: '14px' }}>
        Click any blue point to see predictions from that date
      </p>
      <p style={{ color: '#666', fontSize: '14px', marginBottom: '20px' }}>
        This model shows income arriving discretely on the 1st of each month (causing upward jumps),
        while spending is distributed uniformly throughout the month (causing gradual declines).
      </p>

      <Plot
        data={[
          // Sawtooth prediction line (orange, solid)
          {
            x: selectedPrediction.timeline.dates,
            y: selectedPrediction.timeline.balances,
            type: 'scatter',
            mode: 'lines',
            name: 'Sawtooth Prediction',
            line: {
              color: 'rgb(255, 127, 14)',
              width: 2,
            },
            hovertemplate: '<b>Date:</b> %{x}<br><b>Predicted:</b> £%{y:,.2f}<extra></extra>',
          },
          // Actual balance line (blue, with markers)
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
          title: `Sawtooth Balance Prediction (from ${selectedPrediction.startDate})`,
          xaxis: {
            title: 'Date',
            type: 'date',
          },
          yaxis: {
            title: 'Balance (£)',
            tickformat: ',.2f',
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

      <div style={{
        marginTop: '20px',
        padding: '16px',
        backgroundColor: '#f0f9ff',
        borderLeft: '4px solid #3b82f6',
        borderRadius: '4px'
      }}>
        <h4 style={{ margin: '0 0 8px 0', color: '#1e40af' }}>About This Model</h4>
        <ul style={{ margin: 0, paddingLeft: '20px', color: '#1e40af' }}>
          <li>Income is modeled as <strong>discrete events</strong> occurring on the 1st of each month</li>
          <li>Spending is modeled as <strong>continuous</strong>, distributed uniformly across each month</li>
          <li>This creates a "sawtooth" pattern: balance jumps up on payday, then gradually decreases</li>
          <li>This model is more realistic than assuming both income and spending are continuous</li>
        </ul>
      </div>
    </div>
  );
};

export default SawtoothChart;
