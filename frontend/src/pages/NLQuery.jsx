/**
 * NLQuery.jsx — Ask NIRF Data (Level 3 Natural Language Query Interface)
 * Allows users to ask questions in plain English and renders the parsed
 * query intent, summary answer, Plotly visualizations, and data tables.
 */

import { useState, useContext } from 'react';
import { FilterContext } from '../App';
import { postNLQuery } from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const SAMPLE_QUESTIONS = [
  'Compare IIT Indore, IIT Madras, and IIT Bombay in Engineering in 2025.',
  'Did IIT Indore improve its rank every year in Engineering?',
  'What was IIT Indore\'s best rank in Engineering?',
  'Compare IIT Indore\'s TLR and RPC scores in Engineering in 2025.',
  'Did IIT Madras ever lose its #1 position in Engineering?',
  'When did IIT Indore first enter the top 10 in Engineering?',
  'What is the current rank of IIT Indore?',
  'Show the ranking trend of IIT Madras over time',
  'Which institutions showed the greatest improvement in rank?',
  'Compare Karnataka and Tamil Nadu in 2024',
];

function formatSummaryText(text) {
  if (!text) return null;
  const lines = text.split('\n');

  return (
    <div style={{ lineHeight: 1.7 }}>
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} style={{ height: 6 }} />;

        const isBullet = trimmed.startsWith('- ') || trimmed.startsWith('* ');
        const content = isBullet ? trimmed.substring(2) : trimmed;

        // Parse **bold text** tokens safely
        const tokens = content.split(/(\*\*.*?\*\*)/g).map((token, tIdx) => {
          if (token.startsWith('**') && token.endsWith('**')) {
            return (
              <strong key={tIdx} style={{ color: 'var(--text-primary)', fontWeight: 700 }}>
                {token.slice(2, -2)}
              </strong>
            );
          }
          return token;
        });

        if (isBullet) {
          return (
            <div key={idx} style={{ display: 'flex', gap: 8, paddingLeft: 12, marginBottom: 4 }}>
              <span style={{ color: 'var(--accent)' }}>•</span>
              <div>{tokens}</div>
            </div>
          );
        }

        return (
          <p key={idx} style={{ marginBottom: 6 }}>
            {tokens}
          </p>
        );
      })}
    </div>
  );
}

export default function NLQuery() {
  const { category: dashboardCategory } = useContext(FilterContext) || {};
  const [question, setQuestion] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runQuery = async (queryText) => {
    const q = (queryText ?? question).trim();
    if (!q) {
      setError('Please enter a question about NIRF rankings.');
      return;
    }

    setLoading(true);
    setError(null);
    setSubmittedQuery(q);

    try {
      const resp = await postNLQuery(q, dashboardCategory, null);
      setResult(resp);
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to process query. Please verify that the FastAPI backend is running.';
      setError(msg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    runQuery(question);
  };

  const handleChipClick = (sample) => {
    setQuestion(sample);
    runQuery(sample);
  };

  // Safely parse figure JSON from backend
  let chartData = null;
  let chartLayout = null;
  if (result?.figure_json) {
    try {
      const parsed =
        typeof result.figure_json === 'string'
          ? JSON.parse(result.figure_json)
          : result.figure_json;
      if (parsed && Array.isArray(parsed.data) && parsed.data.length > 0) {
        chartData = parsed.data;
        chartLayout = parsed.layout || {};
      }
    } catch (parseErr) {
      console.warn('Unable to parse figure_json from backend:', parseErr);
    }
  }

  const queryPlan = result?.query_plan || {};
  const hasTableData = Array.isArray(result?.data) && result.data.length > 0;

  return (
    <div>
      <div className="section-header">
        <div className="section-title">
          <span className="icon">💬</span> Ask NIRF Data (Natural Language Query)
        </div>
        <div className="section-desc">
          Ask conversational questions in plain English. The rule-based engine translates your question into analytical queries across rankings from 2017 to 2025.
        </div>
      </div>

      {/* Query Input Card */}
      <div className="card" style={{ marginBottom: 24 }}>
        <form onSubmit={handleSubmit}>
          <div className="nl-input-wrap">
            <input
              type="text"
              className="nl-input"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Which institution ranked first in Engineering in 2024? or Show the ranking trend of IIT Madras"
              disabled={loading}
              aria-label="Natural Language Question Input"
            />
            <button
              type="submit"
              className="nl-send-btn"
              disabled={loading || !question.trim()}
              title="Submit Question"
            >
              {loading ? '⏳' : '➔'}
            </button>
          </div>
        </form>

        {/* Example Question Chips */}
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            Suggested Questions:
          </div>
          <div className="sample-chip-grid">
            {SAMPLE_QUESTIONS.map((sq, i) => (
              <button
                key={i}
                type="button"
                className="sample-chip"
                onClick={() => handleChipClick(sq)}
                disabled={loading}
              >
                {sq}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="error-box" style={{ marginBottom: 24 }}>
          <strong>Query Error:</strong> {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-wrap">
          <div className="spinner" />
          <p>Analyzing NIRF rankings and preparing response…</p>
        </div>
      )}

      {/* Results View */}
      {!loading && result && (
        <div>
          {/* Query Understanding Metadata Badges */}
          <div className="card" style={{ marginBottom: 20, padding: '16px 20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginRight: 8 }}>
                  Query:
                </span>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                  &ldquo;{submittedQuery}&rdquo;
                </span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {result.intent && (
                  <span className="badge badge-primary">
                    Intent: {result.intent.replace(/_/g, ' ')}
                  </span>
                )}
                {queryPlan.category && (
                  <span className="badge badge-warning">
                    Category: {queryPlan.category}
                  </span>
                )}
                {queryPlan.primary_year ? (
                  <span className="badge badge-success">
                    Year: {queryPlan.primary_year}
                  </span>
                ) : queryPlan.start_year && queryPlan.end_year ? (
                  <span className="badge badge-success">
                    Years: {queryPlan.start_year}–{queryPlan.end_year}
                  </span>
                ) : null}
                {Array.isArray(queryPlan.institutions) && queryPlan.institutions.length > 1 ? (
                  <span className="badge badge-primary">
                    Institutions: {queryPlan.institutions.length > 2
                      ? queryPlan.institutions.slice(0, -1).join(', ') + ' & ' + queryPlan.institutions[queryPlan.institutions.length - 1]
                      : queryPlan.institutions.join(' vs ')}
                  </span>
                ) : queryPlan.institution ? (
                  <span className="badge badge-primary">
                    Institution: {queryPlan.institution}
                  </span>
                ) : null}
                {Array.isArray(queryPlan.states) && queryPlan.states.length > 0 && (
                  <span className="badge badge-warning">
                    States: {queryPlan.states.join(', ')}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Textual Summary Answer */}
          {result.summary_text && (
            <div className="summary-box">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, color: 'var(--accent)', fontWeight: 600, fontSize: '0.85rem' }}>
                <span>💡</span> Answer Summary
              </div>
              {formatSummaryText(result.summary_text)}
            </div>
          )}

          {/* Visualizations Section */}
          {chartData ? (
            <div className="card" style={{ marginBottom: 24 }}>
              <div className="section-title" style={{ fontSize: '1rem', marginBottom: 16 }}>
                📈 Visual Analysis
              </div>
              <PlotlyChart
                data={chartData}
                layout={{
                  ...chartLayout,
                  height: 420,
                  margin: { t: 40, r: 24, b: 50, l: 56 },
                }}
              />
            </div>
          ) : (
            <div className="card-sm" style={{ background: 'var(--bg-glass)', border: '1px dashed var(--border)', marginBottom: 24, padding: 14, color: 'var(--text-muted)', fontSize: '0.82rem' }}>
              ℹ️ No chart visualization generated for this specific query intent. Underlying details are provided in the summary and data table.
            </div>
          )}

          {/* Tabular Data Section */}
          {hasTableData && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <div className="section-title" style={{ fontSize: '1rem' }}>
                  📋 Underlying Dataset Records
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {result.data.length} records returned
                </span>
              </div>
              <DataTable data={result.data} maxRows={50} />
            </div>
          )}
        </div>
      )}

      {/* Initial Empty State before any query */}
      {!loading && !result && !error && (
        <div className="empty-state" style={{ padding: '60px 20px' }}>
          <div className="icon">💬</div>
          <h3>Ready to explore NIRF Rankings</h3>
          <p>
            Type a question in the box above or click on one of the suggested query chips to start.
          </p>
        </div>
      )}
    </div>
  );
}

