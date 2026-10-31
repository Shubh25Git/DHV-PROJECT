/**
 * PlotlyChart.jsx — Thin wrapper around react-plotly.js.
 * Applies the dark NIRF dashboard theme to every chart automatically.
 */

import Plot from 'react-plotly.js';

const DARK_LAYOUT = {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { family: 'Inter, system-ui, sans-serif', color: '#94a3b8', size: 12 },
  xaxis: {
    gridcolor: 'rgba(255,255,255,0.06)',
    linecolor: 'rgba(255,255,255,0.08)',
    tickcolor: 'rgba(255,255,255,0.08)',
    zerolinecolor: 'rgba(255,255,255,0.08)',
  },
  yaxis: {
    gridcolor: 'rgba(255,255,255,0.06)',
    linecolor: 'rgba(255,255,255,0.08)',
    tickcolor: 'rgba(255,255,255,0.08)',
    zerolinecolor: 'rgba(255,255,255,0.08)',
  },
  legend: {
    bgcolor: 'rgba(17,24,39,0.8)',
    bordercolor: 'rgba(255,255,255,0.08)',
    borderwidth: 1,
    font: { color: '#94a3b8' },
  },
  margin: { t: 44, r: 20, b: 48, l: 52 },
};

const COLORS = [
  '#6366f1', '#22d3ee', '#10b981', '#f59e0b',
  '#ef4444', '#a78bfa', '#34d399', '#fb923c',
  '#60a5fa', '#f472b6',
];

export function colorScale() { return COLORS; }

export default function PlotlyChart({ data, layout = {}, style = {}, ...rest }) {
  const mergedLayout = {
    ...DARK_LAYOUT,
    ...layout,
    xaxis: { ...DARK_LAYOUT.xaxis, ...(layout.xaxis || {}) },
    yaxis: { ...DARK_LAYOUT.yaxis, ...(layout.yaxis || {}) },
    font: { ...DARK_LAYOUT.font, ...(layout.font || {}) },
    legend: { ...DARK_LAYOUT.legend, ...(layout.legend || {}) },
    margin: { ...DARK_LAYOUT.margin, ...(layout.margin || {}) },
    colorway: COLORS,
  };

  return (
    <Plot
      data={data}
      layout={mergedLayout}
      config={{ displayModeBar: true, displaylogo: false, responsive: true }}
      style={{ width: '100%', minHeight: 320, ...style }}
      useResizeHandler
      {...rest}
    />
  );
}
