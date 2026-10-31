/**
 * Overview.jsx — Dashboard overview with KPI cards, top-10 table, and score histogram.
 */

import { useContext } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import { fetchMeta, fetchTopInstitutions, fetchScoreDistribution } from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

function KpiCard({ label, value, sub, color = 'var(--primary)' }) {
  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={{ backgroundImage: `linear-gradient(135deg, var(--text-primary), ${color})` }}>
        {value ?? '—'}
      </div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export default function Overview() {
  const { year, category } = useContext(FilterContext);

  const { data: meta }  = useApi(() => fetchMeta(), []);
  const { data: top10, loading: l1 } = useApi(
    () => fetchTopInstitutions(year, category, 10), [year, category]
  );
  const { data: distData, loading: l2 } = useApi(
    () => fetchScoreDistribution(year, category), [year, category]
  );

  const histTrace = distData?.scores?.length
    ? [{
        type: 'histogram',
        x: distData.scores,
        nbinsx: 25,
        marker: { color: 'rgba(99,102,241,0.7)', line: { color: '#6366f1', width: 1 } },
        name: 'Score Distribution',
      }]
    : [];

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">📊</span> Dashboard Overview</div>
        <div className="section-desc">
          Comprehensive view of NIRF rankings 2017–2025 · {category} · {year}
        </div>
      </div>

      {/* KPIs */}
      <div className="kpi-grid">
        <KpiCard label="Total Records"   value={meta?.total_records?.toLocaleString()} color="var(--primary)" />
        <KpiCard label="Institutions"    value={meta?.total_institutions?.toLocaleString()} color="var(--accent)" />
        <KpiCard label="States & UTs"    value={meta?.total_states} color="var(--success)" />
        <KpiCard label="Years Covered"   value={meta ? `${meta.year_range[0]}–${meta.year_range[1]}` : '—'} color="var(--warning)" />
        <KpiCard label="Categories"      value={meta?.total_categories} color="#a78bfa" />
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Top 10 Table */}
        <div className="card">
          <div className="section-title" style={{ marginBottom: 16, fontSize: '1rem' }}>
            🏆 Top 10 Institutions · {category} · {year}
          </div>
          {l1
            ? <div className="loading-wrap"><div className="spinner" /></div>
            : <DataTable
                data={top10 || []}
                columns={['rank','name','score','state','tlr','rpc']}
              />
          }
        </div>

        {/* Score histogram */}
        <div className="card">
          <div className="section-title" style={{ marginBottom: 16, fontSize: '1rem' }}>
            📉 Score Distribution · {category} · {year}
          </div>
          {l2
            ? <div className="loading-wrap"><div className="spinner" /></div>
            : histTrace.length
              ? <PlotlyChart
                  data={histTrace}
                  layout={{ xaxis: { title: 'NIRF Score' }, yaxis: { title: 'Number of Institutions' } }}
                />
              : <div className="empty-state"><div className="icon">📭</div><h3>No score data</h3></div>
          }
        </div>
      </div>
    </div>
  );
}
