/**
 * DynamicExplorer.jsx — Level 2: Dynamic Analysis Explorer Redesign
 * Professional, clean, modern light-themed ad-hoc analytics builder.
 * Real NIRF dataset values (2017–2025) with complete multi-chart support.
 */

import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import Plot from 'react-plotly.js';
import Plotly from 'plotly.js-dist-min';
import { fetchDynamicData } from '../api';
import './DynamicExplorer.css';

// Variable options definitions
const AXIS_VARIABLES = [
  { value: 'state', label: 'State' },
  { value: 'year', label: 'Year' },
  { value: 'institution', label: 'Institution' },
  { value: 'score', label: 'Overall Score' },
  { value: 'tlr', label: 'TLR' },
  { value: 'rpc', label: 'RPC' },
  { value: 'go', label: 'GO' },
  { value: 'oi', label: 'OI' },
  { value: 'perception', label: 'PR' },
  { value: 'rank', label: 'Rank' },
];

const Y_VARIABLES = [
  { value: 'score', label: 'Overall Score' },
  { value: 'rank', label: 'Rank' },
  { value: 'tlr', label: 'TLR' },
  { value: 'rpc', label: 'RPC' },
  { value: 'go', label: 'GO' },
  { value: 'oi', label: 'OI' },
  { value: 'perception', label: 'PR' },
  { value: 'count', label: 'Institution Count' },
];

const AGG_OPTIONS = [
  { value: 'mean', label: 'Mean' },
  { value: 'median', label: 'Median' },
  { value: 'individual', label: 'Individual values' },
  { value: 'count', label: 'Count' },
  { value: 'min', label: 'Minimum' },
  { value: 'max', label: 'Maximum' },
  { value: 'std', label: 'Standard deviation' },
];

const CATEGORIES = [
  'Engineering',
  'Overall',
  'Management',
  'University',
  'College',
  'Pharmacy',
  'Medical',
  'Dental',
  'Law',
  'Architecture',
  'Agriculture',
  'Research',
];

const YEAR_OPTIONS = [
  '2021 – 2025',
  '2017 – 2025',
  '2020 – 2025',
  '2025',
  '2024',
  '2023',
  '2022',
  '2021',
  '2020',
  '2019',
  '2018',
  '2017',
];

const TOP_N_OPTIONS = [
  { value: 5, label: 'Top 5' },
  { value: 10, label: 'Top 10' },
  { value: 20, label: 'Top 20' },
  { value: 50, label: 'Top 50' },
  { value: 100, label: 'Top 100' },
  { value: 0, label: 'All' },
];

const CHART_TYPES = [
  { id: 'Bar Chart', label: 'Bar Chart', icon: '📊' },
  { id: 'Line Chart', label: 'Line Chart', icon: '📈' },
  { id: 'Scatter Plot', label: 'Scatter Plot', icon: '📉' },
  { id: 'Box Plot', label: 'Box Plot', icon: '📦' },
  { id: 'Histogram', label: 'Histogram', icon: '📶' },
  { id: 'Map (Choropleth)', label: 'Map (Choropleth)', icon: '🗺️' },
  { id: 'Heatmap', label: 'Heatmap', icon: '▦' },
];

const YEAR_COLORS = {
  2017: '#94A3B8',
  2018: '#818CF8',
  2019: '#6366F1',
  2020: '#4F46E5',
  2021: '#2563EB',
  2022: '#38BDF8',
  2023: '#22C55E',
  2024: '#FB923C',
  2025: '#EF4444',
};

const PALETTE = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#EC4899', '#6366F1'];

const DEFAULT_STATE = {
  yearRange: '2021 – 2025',
  category: 'Engineering',
  selectedStates: ['Karnataka', 'Tamil Nadu'],
  selectedInstitutions: [],
  topN: 100,
  analysisType: 'Comparison',
  xVar: 'state',
  yVar: 'score',
  aggFunc: 'mean',
  chartType: 'Bar Chart',
  groupBy: 'year',
  sortBy: 'val_desc',
  showDataLabels: true,
  showErrorBars: false,
  viewAsPercentage: false,
};

export default function DynamicExplorer() {
  // Theme state: 'light' | 'dark'
  const [theme, setTheme] = useState('light');

  // Filter States
  const [yearRange, setYearRange] = useState(DEFAULT_STATE.yearRange);
  const [category, setCategory] = useState(DEFAULT_STATE.category);
  const [selectedStates, setSelectedStates] = useState(DEFAULT_STATE.selectedStates);
  const [selectedInstitutions, setSelectedInstitutions] = useState(DEFAULT_STATE.selectedInstitutions);
  const [topN, setTopN] = useState(DEFAULT_STATE.topN);

  // Analysis Configuration States
  const [analysisType, setAnalysisType] = useState(DEFAULT_STATE.analysisType);
  const [xVar, setXVar] = useState(DEFAULT_STATE.xVar);
  const [yVar, setYVar] = useState(DEFAULT_STATE.yVar);
  const [aggFunc, setAggFunc] = useState(DEFAULT_STATE.aggFunc);
  const [chartType, setChartType] = useState(DEFAULT_STATE.chartType);
  const [groupBy, setGroupBy] = useState(DEFAULT_STATE.groupBy);
  const [sortBy, setSortBy] = useState(DEFAULT_STATE.sortBy);
  const [showDataLabels, setShowDataLabels] = useState(DEFAULT_STATE.showDataLabels);
  const [showErrorBars, setShowErrorBars] = useState(DEFAULT_STATE.showErrorBars);
  const [viewAsPercentage, setViewAsPercentage] = useState(DEFAULT_STATE.viewAsPercentage);

  // Data state
  const [dataRecords, setDataRecords] = useState([]);
  const [availableStates, setAvailableStates] = useState([]);
  const [availableInstitutions, setAvailableInstitutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Dropdown Popovers
  const [statePopoverOpen, setStatePopoverOpen] = useState(false);
  const [stateSearch, setStateSearch] = useState('');
  const [instPopoverOpen, setInstPopoverOpen] = useState(false);
  const [instSearch, setInstSearch] = useState('');

  // Table pagination & sorting
  const [tablePage, setTablePage] = useState(1);
  const pageSize = 10;
  const [tableSortCol, setTableSortCol] = useState('rank');
  const [tableSortAsc, setTableSortAsc] = useState(true);

  // Reference to graph DOM element
  const plotDivRef = useRef(null);
  const stateBoxRef = useRef(null);
  const instBoxRef = useRef(null);

  // Close popovers on click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (stateBoxRef.current && !stateBoxRef.current.contains(e.target)) {
        setStatePopoverOpen(false);
      }
      if (instBoxRef.current && !instBoxRef.current.contains(e.target)) {
        setInstPopoverOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Parse start and end years
  const { startYear, endYear } = useMemo(() => {
    if (yearRange.includes('–') || yearRange.includes('-')) {
      const parts = yearRange.split(/[–-]/).map((s) => parseInt(s.trim(), 10));
      return { startYear: parts[0] || 2021, endYear: parts[1] || 2025 };
    }
    const single = parseInt(yearRange, 10);
    return { startYear: single || 2025, endYear: single || 2025 };
  }, [yearRange]);

  // Execute data query
  const executeQuery = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        category,
        start_year: startYear,
        end_year: endYear,
        states: selectedStates.length ? selectedStates : undefined,
        institutions: selectedInstitutions.length ? selectedInstitutions : undefined,
        top_n: topN > 0 ? topN : undefined,
      };

      const res = await fetchDynamicData(payload);
      if (res) {
        const records = res.data || res.records || [];
        setDataRecords(records);
        if (res.available_states?.length) {
          setAvailableStates(res.available_states);
        }
        if (res.available_institutions?.length) {
          setAvailableInstitutions(res.available_institutions);
        }
      }
    } catch (err) {
      console.error('Dynamic fetch error:', err);
      setError(err?.message || 'Failed to load dynamic data.');
    } finally {
      setLoading(false);
    }
  }, [category, startYear, endYear, selectedStates, selectedInstitutions, topN]);

  // Automatically update data and institution options whenever filters change
  useEffect(() => {
    executeQuery();
  }, [executeQuery]);

  // Handle Analysis Type preset changes
  const handleAnalysisTypeChange = (type) => {
    setAnalysisType(type);
    if (type === 'Comparison') {
      setXVar('state');
      setYVar('score');
      setChartType('Bar Chart');
      setGroupBy('year');
    } else if (type === 'Trend') {
      setXVar('year');
      setYVar('score');
      setChartType('Line Chart');
      setGroupBy('state');
    } else if (type === 'Distribution') {
      setXVar('state');
      setYVar('score');
      setChartType('Box Plot');
      setGroupBy('None');
    } else if (type === 'Correlation') {
      setXVar('tlr');
      setYVar('score');
      setChartType('Scatter Plot');
      setGroupBy('state');
    } else if (type === 'Ranking') {
      setXVar('institution');
      setYVar('rank');
      setChartType('Bar Chart');
      setGroupBy('None');
      setSortBy('rank_asc');
    } else if (type === 'Geographical') {
      setXVar('state');
      setYVar('score');
      setChartType('Map (Choropleth)');
      setGroupBy('None');
    }
  };

  // Reset to default
  const handleReset = () => {
    setYearRange(DEFAULT_STATE.yearRange);
    setCategory(DEFAULT_STATE.category);
    setSelectedStates(DEFAULT_STATE.selectedStates);
    setSelectedInstitutions(DEFAULT_STATE.selectedInstitutions);
    setTopN(DEFAULT_STATE.topN);
    setAnalysisType(DEFAULT_STATE.analysisType);
    setXVar(DEFAULT_STATE.xVar);
    setYVar(DEFAULT_STATE.yVar);
    setAggFunc(DEFAULT_STATE.aggFunc);
    setChartType(DEFAULT_STATE.chartType);
    setGroupBy(DEFAULT_STATE.groupBy);
    setSortBy(DEFAULT_STATE.sortBy);
    setShowDataLabels(DEFAULT_STATE.showDataLabels);
    setShowErrorBars(DEFAULT_STATE.showErrorBars);
    setViewAsPercentage(DEFAULT_STATE.viewAsPercentage);
    setTablePage(1);
  };

  // Chip remove helpers
  const removeState = (stateToRemove) => {
    setSelectedStates((prev) => prev.filter((s) => s !== stateToRemove));
  };

  const removeInstitution = (instToRemove) => {
    setSelectedInstitutions((prev) => prev.filter((i) => i !== instToRemove));
  };

  const toggleState = (st) => {
    setSelectedStates((prev) =>
      prev.includes(st) ? prev.filter((s) => s !== st) : [...prev, st]
    );
  };

  const toggleInstitution = (inst) => {
    setSelectedInstitutions((prev) =>
      prev.includes(inst) ? prev.filter((i) => i !== inst) : [...prev, inst]
    );
  };

  // Filtered state/inst list for popovers
  const filteredStates = useMemo(() => {
    if (!stateSearch.trim()) return availableStates;
    return availableStates.filter((s) =>
      s.toLowerCase().includes(stateSearch.toLowerCase())
    );
  }, [availableStates, stateSearch]);

  const filteredInstitutions = useMemo(() => {
    if (!instSearch.trim()) return availableInstitutions;
    return availableInstitutions.filter((i) =>
      i.toLowerCase().includes(instSearch.toLowerCase())
    );
  }, [availableInstitutions, instSearch]);

  // Aggregation helper
  const computeAgg = (arr, func) => {
    if (!arr || !arr.length) return 0;
    if (func === 'count') return arr.length;
    if (func === 'min') return Math.min(...arr);
    if (func === 'max') return Math.max(...arr);
    const sum = arr.reduce((a, b) => a + b, 0);
    if (func === 'mean') return sum / arr.length;
    if (func === 'median') {
      const sorted = [...arr].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    }
    if (func === 'std') {
      const mean = sum / arr.length;
      const squareDiffs = arr.map((value) => Math.pow(value - mean, 2));
      const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / arr.length;
      return Math.sqrt(avgSquareDiff);
    }
    return sum / arr.length;
  };

  // Calculate Pearson correlation coefficient
  const calculateCorrelation = (xArr, yArr) => {
    const pairs = [];
    for (let i = 0; i < xArr.length; i++) {
      const x = Number(xArr[i]);
      const y = Number(yArr[i]);
      if (!isNaN(x) && !isNaN(y)) {
        pairs.push([x, y]);
      }
    }
    const n = pairs.length;
    if (n < 2) return null;
    const sumX = pairs.reduce((acc, p) => acc + p[0], 0);
    const sumY = pairs.reduce((acc, p) => acc + p[1], 0);
    const sumXY = pairs.reduce((acc, p) => acc + p[0] * p[1], 0);
    const sumX2 = pairs.reduce((acc, p) => acc + p[0] * p[0], 0);
    const sumY2 = pairs.reduce((acc, p) => acc + p[1] * p[1], 0);
    const num = n * sumXY - sumX * sumY;
    const den = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    if (den === 0) return null;
    return num / den;
  };

  // Generate Plotly Series based on configuration
  const { chartData, chartLayout, chartTitle, chartSubtitle } = useMemo(() => {
    const isDark = theme === 'dark';
    const textColor = isDark ? '#F1F5F9' : '#1E293B';
    const mutedColor = isDark ? '#94A3B8' : '#64748B';
    const gridColor = isDark ? 'rgba(255,255,255,0.08)' : '#F1F5F9';
    const bgPaper = isDark ? '#111827' : '#FFFFFF';

    const yVarLabel = Y_VARIABLES.find((v) => v.value === yVar)?.label || yVar;
    const xVarLabel = AXIS_VARIABLES.find((v) => v.value === xVar)?.label || xVar;
    const aggLabel = AGG_OPTIONS.find((a) => a.value === aggFunc)?.label || 'Average';
    const pctSuffix = viewAsPercentage ? '%' : '';

    let title = `${aggLabel} ${yVarLabel} by ${xVarLabel} (${category}, ${startYear}${
      startYear !== endYear ? ' – ' + endYear : ''
    })`;
    let subtitle = `${aggLabel} ${yVarLabel.toLowerCase()} across all ${category.toLowerCase()} institutions in selected filters.`;

    if (!dataRecords.length) {
      return {
        chartData: [],
        chartLayout: {
          paper_bgcolor: bgPaper,
          plot_bgcolor: bgPaper,
          annotations: [
            {
              text: loading ? 'Loading real NIRF data...' : 'No records found for current filters.',
              showarrow: false,
              font: { color: mutedColor, size: 14 },
            },
          ],
        },
        chartTitle: title,
        chartSubtitle: subtitle,
      };
    }

    const effectiveGroup = groupBy === 'None' ? null : groupBy;

    // --- 1. BAR CHART ---
    if (chartType === 'Bar Chart') {
      if (effectiveGroup === 'year' && xVar === 'state') {
        // Grouped by Year across States (matches reference screenshot)
        const distinctStates = selectedStates.length
          ? selectedStates
          : Array.from(new Set(dataRecords.map((d) => d.state))).filter(Boolean);

        if (sortBy === 'val_desc' || sortBy === 'val_asc') {
          const stateMeans = distinctStates.map((st) => {
            const vals = dataRecords
              .filter((d) => d.state === st)
              .map((d) => Number(d[yVar]))
              .filter((v) => !isNaN(v));
            return { state: st, avg: computeAgg(vals, aggFunc) };
          });
          stateMeans.sort((a, b) =>
            sortBy === 'val_desc' ? b.avg - a.avg : a.avg - b.avg
          );
          distinctStates.splice(0, distinctStates.length, ...stateMeans.map((s) => s.state));
        }

        const distinctYears = Array.from(
          new Set(dataRecords.map((d) => Number(d.year)))
        ).sort((a, b) => a - b);

        const traces = distinctYears.map((yr) => {
          const yVals = distinctStates.map((st) => {
            const vals = dataRecords
              .filter((d) => d.state === st && Number(d.year) === yr)
              .map((d) => Number(d[yVar]))
              .filter((v) => !isNaN(v));
            return Number(computeAgg(vals, aggFunc).toFixed(1));
          });

          const stdErrors = distinctStates.map((st) => {
            const vals = dataRecords
              .filter((d) => d.state === st && Number(d.year) === yr)
              .map((d) => Number(d[yVar]))
              .filter((v) => !isNaN(v));
            return Number(computeAgg(vals, 'std').toFixed(1));
          });

          return {
            type: 'bar',
            name: String(yr),
            x: distinctStates,
            y: yVals,
            text: showDataLabels ? yVals.map((v) => (v > 0 ? `${v}${pctSuffix}` : '')) : undefined,
            textposition: 'outside',
            textfont: {
              color: isDark ? '#E2E8F0' : '#1E293B',
              size: 11,
              weight: 600,
            },
            marker: {
              color: YEAR_COLORS[yr] || '#2563EB',
              line: { width: 0 },
            },
            error_y: showErrorBars
              ? {
                  type: 'data',
                  array: stdErrors,
                  visible: true,
                  color: isDark ? '#94A3B8' : '#64748B',
                }
              : undefined,
            hovertemplate: `<b>%{x}</b> (${yr})<br>${yVarLabel}: %{y}${pctSuffix}<extra></extra>`,
          };
        });

        const maxY = Math.max(...traces.flatMap((t) => t.y), 100);

        return {
          chartData: traces,
          chartLayout: {
            barmode: 'group',
            bargroupgap: 0.15,
            bargap: 0.3,
            paper_bgcolor: bgPaper,
            plot_bgcolor: bgPaper,
            margin: { t: 30, r: 24, b: 50, l: 56 },
            xaxis: {
              title: { text: xVarLabel, font: { color: mutedColor, size: 12 } },
              tickfont: { color: textColor, size: 12 },
              gridcolor: 'transparent',
              linecolor: gridColor,
            },
            yaxis: {
              title: { text: `Average ${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
              tickfont: { color: mutedColor, size: 11 },
              gridcolor: gridColor,
              zerolinecolor: gridColor,
              ticksuffix: pctSuffix,
              range: [0, Math.min(105, maxY + 15)],
            },
            legend: {
              orientation: 'h',
              x: 0.5,
              xanchor: 'center',
              y: 1.12,
              font: { color: mutedColor, size: 11 },
            },
          },
          chartTitle: title,
          chartSubtitle: subtitle,
        };
      } else {
        // Generic Bar Chart across distinct X values
        const distinctX = Array.from(new Set(dataRecords.map((d) => d[xVar]))).filter(Boolean);
        const aggValues = distinctX.map((xVal) => {
          const vals = dataRecords
            .filter((d) => d[xVar] === xVal)
            .map((d) => Number(d[yVar]))
            .filter((v) => !isNaN(v));
          return {
            x: xVal,
            y: Number(computeAgg(vals, aggFunc).toFixed(1)),
            std: Number(computeAgg(vals, 'std').toFixed(1)),
          };
        });

        if (sortBy === 'val_desc') aggValues.sort((a, b) => b.y - a.y);
        if (sortBy === 'val_asc') aggValues.sort((a, b) => a.y - b.y);
        if (sortBy === 'rank_asc') aggValues.sort((a, b) => a.y - b.y);
        if (sortBy === 'rank_desc') aggValues.sort((a, b) => b.y - a.y);
        if (sortBy === 'alpha') aggValues.sort((a, b) => String(a.x).localeCompare(String(b.x)));

        const topAgg = aggValues.slice(0, 30); // Prevent overflow if hundreds of institutions

        const trace = {
          type: 'bar',
          x: topAgg.map((d) => d.x),
          y: topAgg.map((d) => d.y),
          text: showDataLabels ? topAgg.map((d) => `${d.y}${pctSuffix}`) : undefined,
          textposition: 'outside',
          textfont: { color: textColor, size: 11, weight: 600 },
          marker: { color: '#2563EB' },
          error_y: showErrorBars
            ? {
                type: 'data',
                array: topAgg.map((d) => d.std),
                visible: true,
                color: isDark ? '#94A3B8' : '#64748B',
              }
            : undefined,
          hovertemplate: `<b>%{x}</b><br>${yVarLabel}: %{y}${pctSuffix}<extra></extra>`,
        };

        const isRank = yVar === 'rank';
        return {
          chartData: [trace],
          chartLayout: {
            paper_bgcolor: bgPaper,
            plot_bgcolor: bgPaper,
            margin: { t: 30, r: 24, b: topAgg.length > 8 ? 80 : 50, l: 56 },
            xaxis: {
              title: { text: xVarLabel, font: { color: mutedColor, size: 12 } },
              tickfont: { color: textColor, size: 11 },
              tickangle: topAgg.length > 6 ? -30 : 0,
              gridcolor: 'transparent',
            },
            yaxis: {
              title: { text: `${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
              tickfont: { color: mutedColor, size: 11 },
              gridcolor: gridColor,
              ticksuffix: pctSuffix,
              autorange: isRank ? 'reversed' : true,
            },
          },
          chartTitle: title,
          chartSubtitle: subtitle,
        };
      }
    }

    // --- 2. LINE CHART ---
    if (chartType === 'Line Chart') {
      const distinctYears = Array.from(
        new Set(dataRecords.map((d) => Number(d.year)))
      ).sort((a, b) => a - b);

      const groupKey = effectiveGroup || (xVar === 'year' ? 'state' : null);

      if (groupKey && groupKey !== 'year') {
        const distinctGroups = Array.from(
          new Set(dataRecords.map((d) => d[groupKey]))
        ).filter(Boolean).slice(0, 8); // Top 8 lines for clarity

        const traces = distinctGroups.map((grp, idx) => {
          const lineY = distinctYears.map((yr) => {
            const vals = dataRecords
              .filter((d) => d[groupKey] === grp && Number(d.year) === yr)
              .map((d) => Number(d[yVar]))
              .filter((v) => !isNaN(v));
            return Number(computeAgg(vals, aggFunc).toFixed(1));
          });
          return {
            type: 'scatter',
            mode: 'lines+markers',
            name: String(grp),
            x: distinctYears,
            y: lineY,
            line: { width: 3, color: PALETTE[idx % PALETTE.length] },
            marker: { size: 7 },
            text: showDataLabels ? lineY.map((v) => `${v}${pctSuffix}`) : undefined,
            textposition: 'top center',
            hovertemplate: `<b>${grp}</b> (%{x})<br>${yVarLabel}: %{y}${pctSuffix}<extra></extra>`,
          };
        });

        return {
          chartData: traces,
          chartLayout: {
            paper_bgcolor: bgPaper,
            plot_bgcolor: bgPaper,
            margin: { t: 30, r: 24, b: 50, l: 56 },
            xaxis: {
              title: { text: 'Year', font: { color: mutedColor, size: 12 } },
              tickvals: distinctYears,
              gridcolor: gridColor,
            },
            yaxis: {
              title: { text: `${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
              gridcolor: gridColor,
              ticksuffix: pctSuffix,
            },
            legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: 1.12 },
          },
          chartTitle: `Trajectory of ${yVarLabel} over Time (${category})`,
          chartSubtitle: `Multi-year trend by ${groupKey} from ${startYear} to ${endYear}.`,
        };
      } else {
        // Overall Single Line trend across years
        const lineY = distinctYears.map((yr) => {
          const vals = dataRecords
            .filter((d) => Number(d.year) === yr)
            .map((d) => Number(d[yVar]))
            .filter((v) => !isNaN(v));
          return Number(computeAgg(vals, aggFunc).toFixed(1));
        });

        const trace = {
          type: 'scatter',
          mode: 'lines+markers',
          name: category,
          x: distinctYears,
          y: lineY,
          line: { width: 3, color: '#2563EB' },
          marker: { size: 8 },
          text: showDataLabels ? lineY.map((v) => `${v}${pctSuffix}`) : undefined,
          textposition: 'top center',
        };

        return {
          chartData: [trace],
          chartLayout: {
            paper_bgcolor: bgPaper,
            plot_bgcolor: bgPaper,
            margin: { t: 30, r: 24, b: 50, l: 56 },
            xaxis: {
              title: { text: 'Year', font: { color: mutedColor, size: 12 } },
              tickvals: distinctYears,
              gridcolor: gridColor,
            },
            yaxis: {
              title: { text: `${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
              gridcolor: gridColor,
              ticksuffix: pctSuffix,
            },
          },
          chartTitle: `Overall ${yVarLabel} Trend (${category}, ${startYear} – ${endYear})`,
          chartSubtitle: `Annual trend across filtered institutions.`,
        };
      }
    }

    // --- 3. SCATTER PLOT & CORRELATION ---
    if (chartType === 'Scatter Plot') {
      const xVals = dataRecords.map((d) => Number(d[xVar])).filter((v) => !isNaN(v));
      const yVals = dataRecords.map((d) => Number(d[yVar])).filter((v) => !isNaN(v));
      const r = calculateCorrelation(xVals, yVals);
      const rStr = r !== null ? `Pearson r = ${r.toFixed(3)} (${Math.abs(r) >= 0.7 ? 'Strong' : Math.abs(r) >= 0.4 ? 'Moderate' : 'Weak'} ${r >= 0 ? 'positive' : 'negative'} correlation)` : 'N/A';

      const trace = {
        type: 'scatter',
        mode: 'markers',
        x: dataRecords.map((d) => Number(d[xVar])),
        y: dataRecords.map((d) => Number(d[yVar])),
        text: dataRecords.map(
          (d) => `${d.institution || d.name}<br>State: ${d.state}<br>Year: ${d.year}`
        ),
        hovertemplate: `<b>%{text}</b><br>${xVarLabel}: %{x}<br>${yVarLabel}: %{y}${pctSuffix}<extra></extra>`,
        marker: {
          color: dataRecords.map((d) => YEAR_COLORS[d.year] || '#2563EB'),
          size: 8,
          opacity: 0.85,
          line: { width: 1, color: '#FFFFFF' },
        },
      };

      return {
        chartData: [trace],
        chartLayout: {
          paper_bgcolor: bgPaper,
          plot_bgcolor: bgPaper,
          margin: { t: 30, r: 24, b: 50, l: 56 },
          xaxis: {
            title: { text: xVarLabel, font: { color: mutedColor, size: 12 } },
            gridcolor: gridColor,
          },
          yaxis: {
            title: { text: `${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
            gridcolor: gridColor,
            ticksuffix: pctSuffix,
          },
        },
        chartTitle: `Correlation: ${xVarLabel} vs ${yVarLabel}`,
        chartSubtitle: `${rStr} across ${dataRecords.length} records.`,
      };
    }

    // --- 4. BOX PLOT ---
    if (chartType === 'Box Plot') {
      const groupVar = xVar === 'state' ? 'state' : xVar === 'year' ? 'year' : 'state';
      const distinctGroups = Array.from(new Set(dataRecords.map((d) => d[groupVar]))).filter(Boolean);

      const traces = distinctGroups.map((grp, idx) => {
        const vals = dataRecords
          .filter((d) => d[groupVar] === grp)
          .map((d) => Number(d[yVar]))
          .filter((v) => !isNaN(v));
        return {
          type: 'box',
          name: String(grp),
          y: vals,
          boxpoints: 'outliers',
          marker: { color: PALETTE[idx % PALETTE.length] },
        };
      });

      return {
        chartData: traces,
        chartLayout: {
          paper_bgcolor: bgPaper,
          plot_bgcolor: bgPaper,
          margin: { t: 30, r: 24, b: 50, l: 56 },
          yaxis: {
            title: { text: `${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
            gridcolor: gridColor,
            ticksuffix: pctSuffix,
          },
        },
        chartTitle: `Distribution of ${yVarLabel} by ${groupVar === 'state' ? 'State' : 'Year'}`,
        chartSubtitle: `Box plots showing median, IQR, and score dispersion across groups.`,
      };
    }

    // --- 5. HISTOGRAM ---
    if (chartType === 'Histogram') {
      const numVals = dataRecords.map((d) => Number(d[yVar])).filter((v) => !isNaN(v));
      const trace = {
        type: 'histogram',
        x: numVals,
        marker: { color: '#2563EB', line: { color: '#FFFFFF', width: 1 } },
        autobinx: true,
      };

      return {
        chartData: [trace],
        chartLayout: {
          paper_bgcolor: bgPaper,
          plot_bgcolor: bgPaper,
          margin: { t: 30, r: 24, b: 50, l: 56 },
          xaxis: {
            title: { text: `${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
            gridcolor: gridColor,
          },
          yaxis: {
            title: { text: 'Institution Count', font: { color: mutedColor, size: 12 } },
            gridcolor: gridColor,
          },
        },
        chartTitle: `Frequency Distribution of ${yVarLabel}`,
        chartSubtitle: `Histogram showing distribution across ${numVals.length} institutions (mean: ${(computeAgg(numVals, 'mean')).toFixed(1)}).`,
      };
    }

    // --- 6. MAP (CHOROPLETH / GEOGRAPHICAL) ---
    if (chartType === 'Map (Choropleth)') {
      const distinctStates = Array.from(new Set(dataRecords.map((d) => d.state))).filter(Boolean);
      const stateStats = distinctStates.map((st) => {
        const vals = dataRecords
          .filter((d) => d.state === st)
          .map((d) => Number(d[yVar]))
          .filter((v) => !isNaN(v));
        return {
          state: st,
          value: Number(computeAgg(vals, aggFunc).toFixed(1)),
          count: vals.length,
        };
      });

      stateStats.sort((a, b) => b.value - a.value);

      const trace = {
        type: 'bar',
        x: stateStats.map((s) => s.value),
        y: stateStats.map((s) => s.state),
        orientation: 'h',
        text: stateStats.map((s) => `${s.value}${pctSuffix}`),
        textposition: 'outside',
        marker: {
          color: stateStats.map((s) => s.value),
          colorscale: 'Blues',
          reversescale: false,
        },
        hovertemplate: '<b>%{y}</b><br>Score: %{x}<extra></extra>',
      };

      return {
        chartData: [trace],
        chartLayout: {
          paper_bgcolor: bgPaper,
          plot_bgcolor: bgPaper,
          margin: { t: 30, r: 40, b: 50, l: 120 },
          xaxis: {
            title: { text: `${aggLabel} ${yVarLabel}${pctSuffix ? ' (%)' : ''}`, font: { color: mutedColor, size: 12 } },
            gridcolor: gridColor,
            ticksuffix: pctSuffix,
          },
          yaxis: {
            title: { text: 'State', font: { color: mutedColor, size: 12 } },
            autorange: 'reversed',
            gridcolor: 'transparent',
          },
        },
        chartTitle: `Geographical ${yVarLabel} by State (${category})`,
        chartSubtitle: `Regional comparison across ${stateStats.length} states colored by intensity.`,
      };
    }

    // --- 7. HEATMAP ---
    if (chartType === 'Heatmap') {
      const distinctStates = (selectedStates.length ? selectedStates : Array.from(new Set(dataRecords.map((d) => d.state)))).filter(Boolean);
      const distinctYears = Array.from(new Set(dataRecords.map((d) => Number(d.year)))).sort((a, b) => a - b);

      const zMatrix = distinctStates.map((st) => {
        return distinctYears.map((yr) => {
          const vals = dataRecords
            .filter((d) => d.state === st && Number(d.year) === yr)
            .map((d) => Number(d[yVar]))
            .filter((v) => !isNaN(v));
          return vals.length ? Number(computeAgg(vals, aggFunc).toFixed(1)) : null;
        });
      });

      const trace = {
        type: 'heatmap',
        z: zMatrix,
        x: distinctYears.map(String),
        y: distinctStates,
        colorscale: 'YlGnBu',
        hoverongaps: false,
        text: zMatrix.map((row) => row.map((v) => (v !== null ? `${v}${pctSuffix}` : '—'))),
        texttemplate: '%{text}',
        textfont: { size: 11 },
        hovertemplate: '<b>State:</b> %{y}<br><b>Year:</b> %{x}<br><b>Score:</b> %{z}<extra></extra>',
      };

      return {
        chartData: [trace],
        chartLayout: {
          paper_bgcolor: bgPaper,
          plot_bgcolor: bgPaper,
          margin: { t: 30, r: 40, b: 50, l: 120 },
          xaxis: {
            title: { text: 'Year', font: { color: mutedColor, size: 12 } },
            gridcolor: 'transparent',
          },
          yaxis: {
            title: { text: 'State', font: { color: mutedColor, size: 12 } },
            gridcolor: 'transparent',
            autorange: 'reversed',
          },
        },
        chartTitle: `Heatmap: ${yVarLabel} across States and Years`,
        chartSubtitle: `Matrix intensity showing performance evolution from ${startYear} to ${endYear}.`,
      };
    }

    // Default fallback
    return {
      chartData: [],
      chartLayout: { paper_bgcolor: bgPaper, plot_bgcolor: bgPaper },
      chartTitle: title,
      chartSubtitle: subtitle,
    };
  }, [
    dataRecords,
    xVar,
    yVar,
    aggFunc,
    chartType,
    groupBy,
    sortBy,
    showDataLabels,
    showErrorBars,
    viewAsPercentage,
    theme,
    selectedStates,
    category,
    startYear,
    endYear,
    loading,
  ]);

  // Sort and paginate filtered data table
  const sortedTableData = useMemo(() => {
    const list = [...dataRecords];
    list.sort((a, b) => {
      let va = a[tableSortCol];
      let vb = b[tableSortCol];
      if (!isNaN(Number(va)) && !isNaN(Number(vb))) {
        va = Number(va);
        vb = Number(vb);
      } else {
        va = String(va || '').toLowerCase();
        vb = String(vb || '').toLowerCase();
      }
      if (va < vb) return tableSortAsc ? -1 : 1;
      if (va > vb) return tableSortAsc ? 1 : -1;
      return 0;
    });
    return list;
  }, [dataRecords, tableSortCol, tableSortAsc]);

  const totalPages = Math.max(1, Math.ceil(sortedTableData.length / pageSize));
  const paginatedData = useMemo(() => {
    const start = (tablePage - 1) * pageSize;
    return sortedTableData.slice(start, start + pageSize);
  }, [sortedTableData, tablePage, pageSize]);

  const handleSortTable = (col) => {
    if (tableSortCol === col) {
      setTableSortAsc(!tableSortAsc);
    } else {
      setTableSortCol(col);
      setTableSortAsc(true);
    }
  };

  // Robust CSV Download using Blob (prevents URL length overflow)
  const handleDownloadCSV = () => {
    if (!dataRecords.length) return;
    const headers = [
      'Rank',
      'Institution',
      'State',
      'Year',
      'Category',
      'Overall Score',
      'TLR',
      'RPC',
      'GO',
      'OI',
      'PR',
    ];
    const rows = dataRecords.map((d) => [
      d.rank ?? '',
      `"${(d.institution || d.name || '').replace(/"/g, '""')}"`,
      `"${(d.state || '').replace(/"/g, '""')}"`,
      d.year ?? '',
      `"${(d.category || category).replace(/"/g, '""')}"`,
      d.score ?? '',
      d.tlr ?? '',
      d.rpc ?? '',
      d.go ?? '',
      d.oi ?? '',
      d.perception ?? '',
    ]);
    const csvContent = [headers.join(','), ...rows.map((e) => e.join(','))].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `nirf_dynamic_${category}_${startYear}_${endYear}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Robust Chart Download using Plotly module
  const handleDownloadChart = () => {
    if (plotDivRef.current && Plotly && Plotly.downloadImage) {
      Plotly.downloadImage(plotDivRef.current, {
        format: 'png',
        width: 1200,
        height: 600,
        filename: `nirf_dynamic_chart_${category}_${startYear}_${endYear}`,
      });
    } else {
      const btn = document.querySelector('.modebar-btn[data-title*="Download"]');
      if (btn) btn.click();
    }
  };

  return (
    <div className={`de-container ${theme === 'dark' ? 'theme-dark' : 'theme-light'}`}>
      {/* ── Page Header ── */}
      <header className="de-header">
        <div className="de-header-left">
          <div className="de-title-row">
            <h1 className="de-title">Dynamic Analysis Explorer</h1>
            <span className="de-level-badge">Level 2</span>
          </div>
          <p className="de-subtitle">
            Build custom analysis on the fly — choose filters, variables, and chart type to explore any question.
          </p>
        </div>

        <div className="de-header-actions">
          {/* Theme switcher */}
          <div className="de-theme-toggle-wrap">
            <span className="de-theme-label">Theme</span>
            <div className="de-theme-pill">
              <button
                type="button"
                className={`de-theme-btn ${theme === 'light' ? 'active' : ''}`}
                onClick={() => setTheme('light')}
                title="Light Theme"
              >
                ☀️
              </button>
              <button
                type="button"
                className={`de-theme-btn ${theme === 'dark' ? 'active' : ''}`}
                onClick={() => setTheme('dark')}
                title="Dark Theme"
              >
                🌙
              </button>
            </div>
          </div>

          {/* Reset Button */}
          <button type="button" className="de-btn-reset" onClick={handleReset}>
            <span>↺</span> Reset
          </button>

          {/* Generate Analysis Button */}
          <button
            type="button"
            className="de-btn-generate"
            onClick={executeQuery}
            disabled={loading}
          >
            <span>▶</span> {loading ? 'Generating...' : 'Generate Analysis'}
          </button>
        </div>
      </header>

      {/* ── Section 1: Data Filters Card ── */}
      <section className="de-card">
        <div className="de-card-header">
          <div className="de-card-title-row">
            <span className="de-step-badge blue">1</span>
            <h2 className="de-card-title">Select Data Filters</h2>
          </div>
          <p className="de-card-subtitle">Filter the dataset to the institutions you want to analyze.</p>
        </div>

        <div className="de-filters-grid">
          {/* Year Filter */}
          <div className="de-control-group">
            <label className="de-label">Year</label>
            <select
              className="de-select"
              value={yearRange}
              onChange={(e) => setYearRange(e.target.value)}
            >
              {YEAR_OPTIONS.map((yr) => (
                <option key={yr} value={yr}>
                  {yr}
                </option>
              ))}
            </select>
          </div>

          {/* Category Filter */}
          <div className="de-control-group">
            <label className="de-label">Category</label>
            <select
              className="de-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* State Multi-select with chips */}
          <div className="de-control-group" ref={stateBoxRef}>
            <label className="de-label">State</label>
            <div
              className={`de-chip-input-box ${statePopoverOpen ? 'open' : ''}`}
              onClick={() => setStatePopoverOpen(!statePopoverOpen)}
            >
              {selectedStates.map((st) => (
                <span key={st} className="de-chip">
                  {st}
                  <button
                    type="button"
                    className="de-chip-remove"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeState(st);
                    }}
                  >
                    ✕
                  </button>
                </span>
              ))}
              {selectedStates.length === 0 && (
                <span className="de-chip-placeholder">Select state(s)</span>
              )}
            </div>

            {statePopoverOpen && (
              <div className="de-popover">
                <div className="de-popover-search">
                  <input
                    type="text"
                    placeholder="Search states..."
                    value={stateSearch}
                    onChange={(e) => setStateSearch(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="de-popover-list">
                  {filteredStates.map((st) => (
                    <label key={st} className="de-popover-item">
                      <input
                        type="checkbox"
                        checked={selectedStates.includes(st)}
                        onChange={() => toggleState(st)}
                      />
                      <span>{st}</span>
                    </label>
                  ))}
                  {filteredStates.length === 0 && (
                    <div style={{ padding: '8px 12px', color: '#94a3b8', fontSize: '0.8rem' }}>
                      No states match
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Institution(s) Multi-select with chips */}
          <div className="de-control-group" ref={instBoxRef}>
            <label className="de-label">Institution(s)</label>
            <div
              className={`de-chip-input-box ${instPopoverOpen ? 'open' : ''}`}
              onClick={() => setInstPopoverOpen(!instPopoverOpen)}
            >
              {selectedInstitutions.map((inst) => (
                <span key={inst} className="de-chip">
                  {inst.length > 18 ? inst.substring(0, 16) + '…' : inst}
                  <button
                    type="button"
                    className="de-chip-remove"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeInstitution(inst);
                    }}
                  >
                    ✕
                  </button>
                </span>
              ))}
              {selectedInstitutions.length === 0 && (
                <span className="de-chip-placeholder">Select institutions (optional)</span>
              )}
            </div>

            {instPopoverOpen && (
              <div className="de-popover">
                <div className="de-popover-search">
                  <input
                    type="text"
                    placeholder="Search institutions..."
                    value={instSearch}
                    onChange={(e) => setInstSearch(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="de-popover-list">
                  {filteredInstitutions.slice(0, 80).map((inst) => (
                    <label key={inst} className="de-popover-item">
                      <input
                        type="checkbox"
                        checked={selectedInstitutions.includes(inst)}
                        onChange={() => toggleInstitution(inst)}
                      />
                      <span>{inst}</span>
                    </label>
                  ))}
                  {filteredInstitutions.length === 0 && (
                    <div style={{ padding: '8px 12px', color: '#94a3b8', fontSize: '0.8rem' }}>
                      No institutions match
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Top N Filter */}
          <div className="de-control-group">
            <label className="de-label">Top N (optional)</label>
            <select
              className="de-select"
              value={topN}
              onChange={(e) => setTopN(Number(e.target.value))}
            >
              {TOP_N_OPTIONS.map((opt) => (
                <option key={opt.label} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {/* ── Section 2: Analysis Configuration Card ── */}
      <section className="de-card">
        <div className="de-card-header">
          <div className="de-card-title-row">
            <span className="de-step-badge green">2</span>
            <h2 className="de-card-title">Choose Analysis Configuration</h2>
          </div>
          <p className="de-card-subtitle">Select variables and analysis settings.</p>
        </div>

        {/* Configuration Row 1 */}
        <div className="de-config-row-1">
          {/* Analysis Type */}
          <div className="de-control-group">
            <label className="de-label">Analysis Type</label>
            <select
              className="de-select"
              value={analysisType}
              onChange={(e) => handleAnalysisTypeChange(e.target.value)}
            >
              <option value="Comparison">Comparison</option>
              <option value="Trend">Trend</option>
              <option value="Distribution">Distribution</option>
              <option value="Correlation">Correlation</option>
              <option value="Ranking">Ranking</option>
              <option value="Geographical">Geographical</option>
            </select>
          </div>

          {/* X-axis */}
          <div className="de-control-group">
            <label className="de-label">X-axis</label>
            <select
              className="de-select"
              value={xVar}
              onChange={(e) => setXVar(e.target.value)}
            >
              {AXIS_VARIABLES.map((v) => (
                <option key={v.value} value={v.value}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>

          {/* Y-axis */}
          <div className="de-control-group">
            <label className="de-label">Y-axis</label>
            <select
              className="de-select"
              value={yVar}
              onChange={(e) => setYVar(e.target.value)}
            >
              {Y_VARIABLES.map((v) => (
                <option key={v.value} value={v.value}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>

          {/* Aggregation */}
          <div className="de-control-group">
            <label className="de-label">Aggregation</label>
            <select
              className="de-select"
              value={aggFunc}
              onChange={(e) => setAggFunc(e.target.value)}
            >
              {AGG_OPTIONS.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </select>
          </div>

          {/* Chart Types Selectable Bar */}
          <div className="de-control-group">
            <label className="de-label">Chart Type</label>
            <div className="de-chart-types-bar">
              {CHART_TYPES.map((ct) => (
                <button
                  key={ct.id}
                  type="button"
                  className={`de-chart-btn ${chartType === ct.id ? 'active' : ''}`}
                  onClick={() => setChartType(ct.id)}
                  title={ct.label}
                >
                  <span className="de-chart-icon">{ct.icon}</span>
                  <span className="de-chart-label">{ct.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Configuration Row 2: Secondary Controls & Switches */}
        <div className="de-config-row-2">
          {/* Group By */}
          <div className="de-config-group-sm">
            <label className="de-label">Group By (optional)</label>
            <select
              className="de-select"
              value={groupBy}
              onChange={(e) => setGroupBy(e.target.value)}
            >
              <option value="None">None</option>
              <option value="year">Year</option>
              <option value="category">Category</option>
              <option value="state">State</option>
              <option value="institution">Institution</option>
            </select>
          </div>

          {/* Sort By */}
          <div className="de-config-group-sm">
            <label className="de-label">Sort By</label>
            <select
              className="de-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="val_desc">Value (Descending)</option>
              <option value="val_asc">Value (Ascending)</option>
              <option value="rank_asc">Rank (Ascending)</option>
              <option value="rank_desc">Rank (Descending)</option>
              <option value="alpha">Alphabetical</option>
            </select>
          </div>

          {/* Switches */}
          <div className="de-switches-group">
            <div
              className="de-switch-item"
              onClick={() => setShowDataLabels(!showDataLabels)}
            >
              <div className={`de-switch-track ${showDataLabels ? 'active' : ''}`}>
                <div className="de-switch-thumb" />
              </div>
              <span className="de-switch-label">Show data labels</span>
            </div>

            <div
              className="de-switch-item"
              onClick={() => setShowErrorBars(!showErrorBars)}
            >
              <div className={`de-switch-track ${showErrorBars ? 'active' : ''}`}>
                <div className="de-switch-thumb" />
              </div>
              <span className="de-switch-label">Show error bars (Std. Dev.)</span>
            </div>

            <div
              className="de-switch-item"
              onClick={() => setViewAsPercentage(!viewAsPercentage)}
            >
              <div className={`de-switch-track ${viewAsPercentage ? 'active' : ''}`}>
                <div className="de-switch-thumb" />
              </div>
              <span className="de-switch-label">View as percentage</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Section 3: Visualization Card (Full Width) ── */}
      <section className="de-card de-viz-card">
        <div className="de-viz-header">
          <div className="de-viz-title-row">
            <span className="de-viz-icon">📊</span>
            <div>
              <h3 className="de-viz-title">{chartTitle}</h3>
              <p className="de-viz-desc">{chartSubtitle}</p>
            </div>
          </div>
        </div>

        <div className="de-chart-container">
          <Plot
            data={chartData}
            layout={{
              ...chartLayout,
              autosize: true,
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            }}
            onInitialized={(fig, graphDiv) => {
              plotDivRef.current = graphDiv;
            }}
            onUpdate={(fig, graphDiv) => {
              plotDivRef.current = graphDiv;
            }}
            style={{ width: '100%', height: '440px' }}
            useResizeHandler
          />
        </div>
      </section>

      {/* ── Section 4: Filtered Data Table Card ── */}
      <section className="de-card">
        <div className="de-table-header-row">
          <div className="de-table-title-wrap">
            <span className="de-table-icon">▦</span>
            <h3 className="de-table-title">Filtered Data (Top 10 shown)</h3>
          </div>

          <div className="de-table-actions">
            <button
              type="button"
              className="de-btn-action"
              onClick={handleDownloadCSV}
              title="Download CSV"
            >
              <span>📥</span> Download CSV
            </button>
            <button
              type="button"
              className="de-btn-action"
              onClick={handleDownloadChart}
              title="Download Chart"
            >
              <span>📷</span> Download Chart
            </button>
          </div>
        </div>

        {/* Table Content */}
        <div className="de-table-responsive">
          <table className="de-table">
            <thead>
              <tr>
                <th onClick={() => handleSortTable('rank')}>
                  Rank {tableSortCol === 'rank' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('institution')}>
                  Institution {tableSortCol === 'institution' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('state')}>
                  State {tableSortCol === 'state' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('year')}>
                  Year {tableSortCol === 'year' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('score')}>
                  Overall Score {tableSortCol === 'score' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('tlr')}>
                  TLR {tableSortCol === 'tlr' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('rpc')}>
                  RPC {tableSortCol === 'rpc' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('go')}>
                  GO {tableSortCol === 'go' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('oi')}>
                  OI {tableSortCol === 'oi' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
                <th onClick={() => handleSortTable('perception')}>
                  PR {tableSortCol === 'perception' ? (tableSortAsc ? '▲' : '▼') : ''}
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, idx) => (
                <tr key={`${row.institution || row.name}-${row.year}-${idx}`}>
                  <td className="de-rank-cell">{row.rank ?? '—'}</td>
                  <td style={{ fontWeight: 500 }}>{row.institution || row.name || '—'}</td>
                  <td>{row.state ?? '—'}</td>
                  <td>{row.year ?? '—'}</td>
                  <td style={{ fontWeight: 600 }}>
                    {row.score != null ? Number(row.score).toFixed(1) : '—'}
                  </td>
                  <td>{row.tlr != null ? Number(row.tlr).toFixed(1) : '—'}</td>
                  <td>{row.rpc != null ? Number(row.rpc).toFixed(1) : '—'}</td>
                  <td>{row.go != null ? Number(row.go).toFixed(1) : '—'}</td>
                  <td>{row.oi != null ? Number(row.oi).toFixed(1) : '—'}</td>
                  <td>{row.perception != null ? Number(row.perception).toFixed(1) : '—'}</td>
                </tr>
              ))}
              {paginatedData.length === 0 && (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                    {loading ? 'Loading real NIRF data...' : 'No data available for the selected filters.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Row */}
        <div className="de-pagination-row">
          <div className="de-pagination-controls">
            <button
              type="button"
              className="de-page-btn"
              disabled={tablePage <= 1}
              onClick={() => setTablePage((p) => Math.max(1, p - 1))}
            >
              ‹
            </button>
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1).map((pg) => (
              <button
                key={pg}
                type="button"
                className={`de-page-btn ${tablePage === pg ? 'active' : ''}`}
                onClick={() => setTablePage(pg)}
              >
                {pg}
              </button>
            ))}
            {totalPages > 7 && <span style={{ padding: '0 4px', color: '#94a3b8' }}>…</span>}
            {totalPages > 7 && (
              <button
                type="button"
                className={`de-page-btn ${tablePage === totalPages ? 'active' : ''}`}
                onClick={() => setTablePage(totalPages)}
              >
                {totalPages}
              </button>
            )}
            <button
              type="button"
              className="de-page-btn"
              disabled={tablePage >= totalPages}
              onClick={() => setTablePage((p) => Math.min(totalPages, p + 1))}
            >
              ›
            </button>
          </div>

          <div className="de-pagination-count">
            Showing{' '}
            {sortedTableData.length > 0 ? (tablePage - 1) * pageSize + 1 : 0} –{' '}
            {Math.min(tablePage * pageSize, sortedTableData.length)} of{' '}
            {sortedTableData.length} institutions
          </div>
        </div>
      </section>
    </div>
  );
}
