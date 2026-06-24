import React from 'react';
import Plot from 'react-plotly.js';

interface SavingRateData {
  dates: string[];
  actualSavingRate: (number | null)[];
  predictedSavingRate: (number | null)[];
  actualSpendingRate: (number | null)[];
  predictedSpendingRate: (number | null)[];
}

interface SavingRateChartProps {
  data: SavingRateData;
}

const SavingRateChart: React.FC<SavingRateChartProps> = ({ data }) => {
  return (
    <div style={{ width: '100%' }}>
      <h3>Saving Rate Over Time</h3>
      <Plot
        data={[
          {
            x: data.dates,
            y: data.actualSavingRate,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Actual Saving Rate',
            line: { color: '#2ca02c', width: 3 },
            marker: { size: 8 },
            hovertemplate: '<b>Date:</b> %{x}<br><b>Actual:</b> £%{y:,.2f}/mo<extra></extra>',
          },
          {
            x: data.dates,
            y: data.predictedSavingRate,
            type: 'scatter',
            mode: 'lines',
            name: 'Predicted Saving Rate',
            line: { color: '#ff7f0e', width: 2, dash: 'dot' },
            hovertemplate: '<b>Date:</b> %{x}<br><b>Predicted:</b> £%{y:,.2f}/mo<extra></extra>',
          },
        ]}
        layout={{
          title: 'Saving Rate (£/month)',
          xaxis: {
            title: 'Date',
            type: 'date',
          },
          yaxis: {
            title: 'Saving Rate (£/month)',
            tickformat: ',.2f',
          },
          hovermode: 'x unified',
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
        style={{ width: '100%', height: '50vh' }}
        useResizeHandler={true}
      />

      <h3 style={{ marginTop: '3rem' }}>Spending Rate Over Time</h3>
      <Plot
        data={[
          {
            x: data.dates,
            y: data.actualSpendingRate,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Actual Spending Rate',
            line: { color: '#d62728', width: 3 },
            marker: { size: 8 },
            hovertemplate: '<b>Date:</b> %{x}<br><b>Actual:</b> £%{y:,.2f}/mo<extra></extra>',
          },
          {
            x: data.dates,
            y: data.predictedSpendingRate,
            type: 'scatter',
            mode: 'lines',
            name: 'Predicted Spending Rate',
            line: { color: '#ff7f0e', width: 2, dash: 'dot' },
            hovertemplate: '<b>Date:</b> %{x}<br><b>Predicted:</b> £%{y:,.2f}/mo<extra></extra>',
          },
        ]}
        layout={{
          title: 'Spending Rate (£/month)',
          xaxis: {
            title: 'Date',
            type: 'date',
          },
          yaxis: {
            title: 'Spending Rate (£/month)',
            tickformat: ',.2f',
          },
          hovermode: 'x unified',
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
        style={{ width: '100%', height: '50vh' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default SavingRateChart;
