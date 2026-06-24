import React from 'react';
import Plot from 'react-plotly.js';
import type { BudgetFile } from '../types/index';

interface BudgetPieChartProps {
  budget: BudgetFile;
}

const BudgetPieChart: React.FC<BudgetPieChartProps> = ({ budget }) => {
  // Build hierarchical data for sunburst chart
  const ids: string[] = ['Total'];        // Unique internal identifiers
  const labels: string[] = ['Total'];     // Display labels (can have duplicates)
  const parents: string[] = [''];
  const values: number[] = [0]; // Will be calculated
  const colors: string[] = ['rgba(255,255,255,0)'];

  // Vibrant color palette - assigned to categories in alphabetical order
  const colorPalette: string[] = [
    '#3498db', // Bright blue
    '#e74c3c', // Vibrant red
    '#2ecc71', // Emerald green
    '#f39c12', // Orange
    '#9b59b6', // Purple
    '#1abc9c', // Turquoise
    '#e91e63', // Pink
    '#f1c40f', // Yellow
    '#16a085', // Teal
    '#27ae60', // Forest green
    '#d35400', // Burnt orange
    '#c0392b', // Dark red
    '#8e44ad', // Deep purple
    '#2980b9', // Ocean blue
    '#d4ac0d', // Gold
    '#17a589', // Sea green
    '#a569bd', // Lavender
    '#ec7063', // Coral
    '#5dade2', // Sky blue
    '#58d68d', // Light green
  ];

  // Assign colors to categories alphabetically
  const getCategoryColor = (category: string): string => {
    const categories = Object.keys(categoriesMap).sort();
    const index = categories.indexOf(category);
    return colorPalette[index % colorPalette.length];
  };

  // Helper function to lighten a hex color
  const lightenColor = (hex: string, percent: number): string => {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.min(255, Math.floor((num >> 16) + (255 - (num >> 16)) * percent));
    const g = Math.min(255, Math.floor(((num >> 8) & 0x00FF) + (255 - ((num >> 8) & 0x00FF)) * percent));
    const b = Math.min(255, Math.floor((num & 0x0000FF) + (255 - (num & 0x0000FF)) * percent));
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
  };

  // Group items by category
  const categoriesMap: Record<string, typeof budget.items> = {};
  budget.items.forEach(item => {
    const category = item.category || 'other';
    if (!categoriesMap[category]) {
      categoriesMap[category] = [];
    }
    categoriesMap[category].push(item);
  });

  // Calculate total for root node
  let totalBudget = 0;

  // Add categories and their items
  Object.entries(categoriesMap).forEach(([category, items]) => {
    const categoryTotal = items.reduce((sum, item) => sum + item.cost, 0);
    totalBudget += categoryTotal;

    // Add category with base color (assigned alphabetically)
    const categoryId = `cat_${category}`;   // Unique ID for category
    const categoryLabel = `${category}`;    // Display label
    const baseColor = getCategoryColor(category);

    ids.push(categoryId);
    labels.push(categoryLabel);
    parents.push('Total');
    values.push(categoryTotal);
    colors.push(baseColor);

    // Add individual items within category with lighter shades
    items.forEach((item, idx) => {
      // Create unique ID but keep display label simple
      const itemId = `item_${category}_${idx}`;  // Unique internal ID
      ids.push(itemId);
      labels.push(item.name);  // Clean display label (can duplicate across categories)
      parents.push(categoryId);  // Reference parent by ID
      values.push(item.cost);

      // Create lighter shade based on item index (20% to 60% lighter)
      const lightenPercent = 0.3 + (idx / items.length) * 0.4;
      colors.push(lightenColor(baseColor, lightenPercent));
    });
  });

  // Set total value
  values[0] = totalBudget;

  return (
    <div style={{ width: '100%', minHeight: '600px' }}>
      <Plot
        data={[
          {
            type: 'sunburst' as any,
            ids: ids,           // Unique identifiers for hierarchy
            labels: labels,     // Display labels (can have duplicates)
            parents: parents,
            values: values,
            branchvalues: 'total' as any,
            marker: {
              colors: colors,
              line: {
                color: 'white',
                width: 3,
              },
            },
            hovertemplate: '<b>%{label}</b><br>£%{value:.2f}<br>%{percentParent}<extra></extra>',
            textinfo: 'label+percent parent',
            insidetextorientation: 'radial',
          } as any,
        ]}
        layout={{
          title: `Budget Breakdown (${budget.date})`,
          height: 600,
          width: undefined,
          autosize: true,
          margin: { l: 0, r: 0, t: 50, b: 0 },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
        }}
        config={{
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
          responsive: true,
        }}
        style={{ width: '100%', height: '600px' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default BudgetPieChart;
