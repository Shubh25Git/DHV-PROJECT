/**
 * Transitions.jsx — Q7 ranking transitions & institutional mobility.
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchBandToTop50,
  fetchTop10EntriesExits, fetchBandRetention,
  fetchLargestShifts, fetchMobilitySummary,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const TABS = [
  'Q7.1 Band 51–100 → Top 50',
  'Q7.2 Top 10 Entries & Exits',
  'Q7.3 Band Retention',
  'Q7.4 Largest Shifts',
  'Q7.5 Mobility Summary',
];

export default function Transitions() {
  const { category, allYears } = useContext(FilterContext);
  const [tab, setTab] = useState(0);

  const years = allYears.length >= 2 ? allYears : [2023, 2024];
  const [y1, setY1] = useState(years[years.length - 2] ?? 2023);
  const [y2, setY2] = useState(years[years.length - 1] ?? 2024);

  const { data: bandData, loading: l0 } = useApi(() => fetchBandToTop50(category, y1, y2), [category, y1, y2]);
  const { data: t10, loading: l1 }      = useApi(() => fetchTop10EntriesExits(category, y1, y2), [category, y1, y2]);
  const { data: ret, loading: l2 }      = useApi(() => fetchBandRetention(category, y1, y2), [category, y1, y2]);
  const { data: shft, loading: l3 }     = useApi(() => fetchLargestShifts(category, y1, y2), [category, y1, y2]);
  const { data: mob, loading: l4 }      = useApi(() => fetchMobilitySummary(category, y1, y2), [category, y1, y2]);

  const yearPickers = (
    <div className="control-row">
      {[['Base Year', y1, setY1], ['Compare Year', y2, setY2]].map(([label, val, setter]) => (
        <div className="form-group" key={label}>
          <label className="form-label">{label}</label>
          <select className="form-select" value={val} onChange={e => setter(+e.target.value)}>
            {allYears.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      ))}
    </div>
  );

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">🔄</span> Ranking Transitions & Mobility</div>
        <div className="section-desc">How institutions move between rank bands year to year.</div>
      </div>

      <div className="tabs">
        {TABS.map((t, i) => (
          <button key={i} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
        ))}
      </div>

      {/* Q7.1 Band 51–100 to Top 50 */}
      {tab === 0 && (
        <div className="card">
          {yearPickers}
          {y1 === y2 ? (
            <div className="error-box" style={{ marginBottom: 16 }}>
              Please select two different years to compare transitions.
            </div>
          ) : l0 ? (
            <div className="loading-wrap"><div className="spinner" /></div>
          ) : bandData?.records?.length ? (
            <>
              <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 20 }}>
                <div className="kpi-card">
                  <div className="kpi-label">Transitioned to Top 50 🎯</div>
                  <div className="kpi-value" style={{ color: 'var(--success)' }}>{bandData.transition_count}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">Base Year Band ({y1})</div>
                  <div className="kpi-value" style={{ fontSize: '1.25rem' }}>Ranks 51–100</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">Outcome Band ({y2})</div>
                  <div className="kpi-value" style={{ fontSize: '1.25rem', color: 'var(--accent)' }}>Top 50 (Rank ≤ 50)</div>
                </div>
              </div>

              <PlotlyChart
                data={bandData.figure?.data || [{
                  type: 'scatter',
                  mode: 'markers+text',
                  x: bandData.records.map(r => r.rank_year1),
                  y: bandData.records.map(r => r.rank_year2),
                  text: bandData.records.map(r => r.name),
                  textposition: 'top center',
                  marker: {
                    size: 10,
                    color: '#10b981',
                    line: { color: '#ffffff', width: 1.5 }
                  },
                  hovertemplate: '<b>%{text}</b><br>Rank in ' + y1 + ': %{x}<br>Rank in ' + y2 + ': %{y}<extra></extra>'
                }]}
                layout={{
                  ...(bandData.figure?.layout || {}),
                  title: {
                    text: `Institutions Moving from 51–100 (${y1}) to Top 50 (${y2}) — ${category}`,
                    font: { color: '#f1f5f9', size: 14 }
                  },
                  xaxis: { title: `Rank in ${y1} (Lower number is better)`, autorange: 'reversed' },
                  yaxis: { title: `Rank in ${y2} (Lower number is better)`, autorange: 'reversed' },
                  height: 420,
                }}
              />

              <div style={{ marginTop: 20 }}>
                <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: 10 }}>
                  📋 Qualifying Institutions ({bandData.transition_count})
                </div>
                <DataTable
                  data={bandData.records}
                  columns={['name', 'rank_year1', 'score_year1', 'rank_year2', 'score_year2']}
                />
              </div>
            </>
          ) : (
            <div className="empty-state">
              <div className="icon">📭</div>
              <h3>No institutions moved from the 51–100 band in {y1} to the Top 50 in {y2} in {category}.</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Try selecting different years or another category to see band transitions.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Q7.2 Entries & Exits */}
      {tab === 1 && (
        <div className="card">
          {yearPickers}
          {l1 ? <div className="loading-wrap"><div className="spinner" /></div> :
            t10
              ? <div className="grid-2">
                  <div>
                    <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: 10, color: 'var(--success)' }}>
                      ✅ New Entrants in Top 10 ({y2})
                    </div>
                    {t10.entries?.length
                      ? t10.entries.map(e => <div key={e} style={{ padding: '6px 0', borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>• {e}</div>)
                      : <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No new entrants.</p>}
                  </div>
                  <div>
                    <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: 10, color: 'var(--danger)' }}>
                      ❌ Exited Top 10 ({y1}→{y2})
                    </div>
                    {t10.exits?.length
                      ? t10.exits.map(e => <div key={e} style={{ padding: '6px 0', borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>• {e}</div>)
                      : <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No exits.</p>}
                  </div>
                </div>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {/* Q7.3 Band Retention */}
      {tab === 2 && (
        <div className="card">
          {yearPickers}
          {l2 ? <div className="loading-wrap"><div className="spinner" /></div> :
            ret
              ? <>
                  <div className="kpi-card" style={{ maxWidth: 220, marginBottom: 20 }}>
                    <div className="kpi-label">Overall Band Retention</div>
                    <div className="kpi-value">{ret.overall_pct?.toFixed(1)}%</div>
                  </div>
                  <DataTable data={ret.bands} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {/* Q7.4 Largest Shifts */}
      {tab === 3 && (
        <div className="card">
          {yearPickers}
          {l3 ? <div className="loading-wrap"><div className="spinner" /></div> :
            shft
              ? <div className="grid-2">
                  <div>
                    <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: 10, color: 'var(--success)' }}>
                      ⬆️ Largest Upward Moves
                    </div>
                    <DataTable data={shft.upward} columns={['name','rank_prev','rank_curr','rank_shift']} />
                  </div>
                  <div>
                    <div className="section-title" style={{ fontSize: '0.9rem', marginBottom: 10, color: 'var(--danger)' }}>
                      ⬇️ Largest Downward Moves
                    </div>
                    <DataTable data={shft.downward} columns={['name','rank_prev','rank_curr','rank_shift']} />
                  </div>
                </div>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {/* Q7.5 Mobility Summary */}
      {tab === 4 && (
        <div className="card">
          {yearPickers}
          {l4 ? <div className="loading-wrap"><div className="spinner" /></div> :
            mob
              ? <>
                  <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 20 }}>
                    <div className="kpi-card">
                      <div className="kpi-label">Moved Up ⬆️</div>
                      <div className="kpi-value" style={{ color: 'var(--success)' }}>{mob.moved_up}</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-label">Stayed Same ↔️</div>
                      <div className="kpi-value">{mob.stayed_same}</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-label">Moved Down ⬇️</div>
                      <div className="kpi-value" style={{ color: 'var(--danger)' }}>{mob.moved_down}</div>
                    </div>
                  </div>
                  <PlotlyChart
                    data={[{
                      type: 'pie',
                      labels: ['Moved Up', 'Stayed Same', 'Moved Down'],
                      values: [mob.moved_up, mob.stayed_same, mob.moved_down],
                      hole: 0.45,
                      marker: { colors: ['#10b981', '#94a3b8', '#ef4444'] },
                    }]}
                    layout={{
                      title: { text: `Mobility Summary — ${category} (${y1}→${y2})`, font: { color: '#f1f5f9', size: 14 } },
                      height: 360,
                    }}
                  />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}
    </div>
  );
}
