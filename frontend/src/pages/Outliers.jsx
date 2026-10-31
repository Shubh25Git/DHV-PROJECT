/**
 * Outliers.jsx — Q8 outlier detection and performance gaps.
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchResearchOutliers,
  fetchResearchTeachingGap,
  fetchScoreChangeOutliers,
  fetchStrongParamPoorRank,
  fetchRankVolatility,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const TABS = [
  'Q8.1 Research Outliers',
  'Q8.2 Research vs Teaching Gap',
  'Q8.3 Score Change Outliers',
  'Q8.4 Strong Param & Poor Rank',
  'Q8.5 Rank Volatility',
];

const PARAMS = [
  { value: 'rpc', label: 'Research & Professional Practice (RPC)' },
  { value: 'tlr', label: 'Teaching, Learning & Resources (TLR)' },
  { value: 'go', label: 'Graduation Outcomes (GO)' },
  { value: 'oi', label: 'Outreach & Inclusivity (OI)' },
  { value: 'perception', label: 'Peer Perception (PR)' },
];

export default function Outliers() {
  const { year, category, allYears } = useContext(FilterContext);
  const [tab, setTab] = useState(0);
  const [selectedParam, setSelectedParam] = useState('rpc');

  const prevYear = allYears[allYears.length - 2] ?? year - 1;

  const { data: resOut, loading: l1 } = useApi(() => fetchResearchOutliers(year, category), [year, category]);
  const { data: gapData, loading: lGap } = useApi(() => fetchResearchTeachingGap(year, category, 15), [year, category]);
  const { data: scOut, loading: l2 }  = useApi(() => fetchScoreChangeOutliers(category, prevYear, year), [category, prevYear, year]);
  const { data: strongParamData, loading: lStrong } = useApi(
    () => fetchStrongParamPoorRank(year, category, selectedParam, 75, 50),
    [year, category, selectedParam]
  );
  const { data: vol, loading: l3 }    = useApi(() => fetchRankVolatility(category, 4), [category]);

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">⚠️</span> Outlier Detection & Performance Gaps</div>
        <div className="section-desc">Institutions whose performance deviates significantly from expected patterns.</div>
      </div>

      <div className="tabs">
        {TABS.map((t, i) => (
          <button key={i} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
        ))}
      </div>

      {/* Q8.1 Research Outliers */}
      {tab === 0 && (
        <div className="card">
          <div className="section-desc" style={{ marginBottom: 16 }}>
            Institutions with unusually high RPC (Research) scores relative to their overall score — identified via regression residuals.
          </div>
          {l1 ? <div className="loading-wrap"><div className="spinner" /></div> :
            resOut?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'scatter', mode: 'markers',
                      x: resOut.map(r => r.score),
                      y: resOut.map(r => r.rpc),
                      text: resOut.map(r => r.name),
                      hovertemplate: '<b>%{text}</b><br>Score: %{x}<br>RPC: %{y}<extra></extra>',
                      marker: { color: '#f59e0b', size: 9, opacity: 0.8 },
                    }]}
                    layout={{
                      title: { text: `Research Score Outliers — ${category} ${year}`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { title: 'Overall Score' },
                      yaxis: { title: 'RPC Score' },
                      height: 400,
                    }}
                  />
                  <DataTable data={resOut} columns={['name','state','rank','score','rpc','tlr']} />
                </>
              : <div className="empty-state"><div className="icon">✅</div><h3>No significant outliers detected.</h3></div>
          }
        </div>
      )}

      {/* Q8.2 Research vs Teaching Gap */}
      {tab === 1 && (
        <div className="card">
          <div className="section-desc" style={{ marginBottom: 16 }}>
            Top institutions with the largest gap between Research (RPC) and Teaching (TLR) scores (RPC − TLR).
            Positive gap indicates institutions whose research output noticeably leads over their teaching score.
          </div>
          {lGap ? <div className="loading-wrap"><div className="spinner" /></div> :
            gapData?.records?.length
              ? <>
                  {gapData.figure && (
                    <PlotlyChart
                      data={gapData.figure.data}
                      layout={{
                        ...gapData.figure.layout,
                        paper_bgcolor: 'transparent',
                        plot_bgcolor: 'transparent',
                        font: { color: '#f1f5f9' },
                      }}
                    />
                  )}
                  <div style={{ marginTop: 24 }}>
                    <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>
                      Performance Gap Data (Top {gapData.records.length})
                    </div>
                    <DataTable
                      data={gapData.records}
                      columns={['name', 'rank', 'score', 'rpc', 'tlr', 'research_teaching_gap']}
                    />
                  </div>
                </>
              : <div className="empty-state"><div className="icon">✅</div><h3>No significant research-teaching gap found.</h3></div>
          }
        </div>
      )}

      {/* Q8.3 Score Change Outliers */}
      {tab === 2 && (
        <div className="card">
          <div className="section-desc" style={{ marginBottom: 16 }}>
            Institutions with year-over-year score changes with Z-score ≥ 2 (unusually large changes). Period: {prevYear}→{year}.
          </div>
          {l2 ? <div className="loading-wrap"><div className="spinner" /></div> :
            scOut?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: scOut.map(r => r.name?.length > 30 ? r.name.slice(0,28)+'…' : r.name),
                      y: scOut.map(r => r.score_change),
                      marker: { color: scOut.map(r => r.score_change > 0 ? '#10b981' : '#ef4444') },
                      text: scOut.map(r => r.z_score?.toFixed(2)),
                      hovertemplate: '<b>%{x}</b><br>Score Change: %{y}<br>Z-score: %{text}<extra></extra>',
                    }]}
                    layout={{
                      title: { text: `Score Change Outliers (Z ≥ 2) — ${prevYear}→${year}`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { tickangle: -30 },
                      yaxis: { title: 'Score Change' },
                      height: 420,
                    }}
                  />
                  <DataTable data={scOut} columns={['name','s1','s2','score_change','z_score']} />
                </>
              : <div className="empty-state"><div className="icon">✅</div><h3>No outlier score changes detected.</h3></div>
          }
        </div>
      )}

      {/* Q8.4 Strong Parameter & Poor Rank */}
      {tab === 3 && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
            <div className="section-desc" style={{ margin: 0 }}>
              Institutions with parameter score ≥ 75th percentile but overall rank &gt; 50 (strong subject performance despite lower overall rank).
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Parameter:</label>
              <select
                className="select"
                value={selectedParam}
                onChange={e => setSelectedParam(e.target.value)}
                style={{ background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: 6, padding: '4px 10px' }}
              >
                {PARAMS.map(p => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>
          </div>

          {lStrong ? <div className="loading-wrap"><div className="spinner" /></div> :
            strongParamData ? (
              <>
                <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', marginBottom: 20 }}>
                  <div className="kpi-card">
                    <div className="kpi-label">Selected Parameter</div>
                    <div className="kpi-value" style={{ color: '#6366f1', fontSize: '1.4rem' }}>{selectedParam.toUpperCase()}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">75th %ile Cutoff</div>
                    <div className="kpi-value" style={{ color: '#ec4899', fontSize: '1.4rem' }}>{strongParamData.param_threshold}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Rank Cutoff</div>
                    <div className="kpi-value" style={{ color: '#06b6d4', fontSize: '1.4rem' }}>&gt; 50</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Qualifying Outliers</div>
                    <div className="kpi-value" style={{ color: '#f59e0b', fontSize: '1.4rem' }}>{strongParamData.count}</div>
                  </div>
                </div>

                {strongParamData.figure && (
                  <PlotlyChart
                    data={strongParamData.figure.data}
                    layout={{
                      ...strongParamData.figure.layout,
                      paper_bgcolor: 'transparent',
                      plot_bgcolor: 'transparent',
                      font: { color: '#f1f5f9' },
                      height: 440,
                    }}
                  />
                )}

                {strongParamData.records?.length > 0 ? (
                  <div style={{ marginTop: 24 }}>
                    <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>
                      Strong {selectedParam.toUpperCase()} Outliers Ranked &gt; 50 ({strongParamData.records.length})
                    </div>
                    <DataTable
                      data={strongParamData.records}
                      columns={['name', 'rank', 'score', selectedParam, 'state']}
                    />
                  </div>
                ) : (
                  <div className="empty-state" style={{ marginTop: 16 }}>
                    <div className="icon">ℹ️</div>
                    <h3>No institutions ranked &gt; 50 have a {selectedParam.toUpperCase()} score ≥ 75th percentile ({strongParamData.param_threshold}).</h3>
                  </div>
                )}
              </>
            ) : (
              <div className="empty-state"><div className="icon">📭</div><h3>No data available.</h3></div>
            )
          }
        </div>
      )}

      {/* Q8.5 Rank Volatility */}
      {tab === 4 && (
        <div className="card">
          <div className="section-desc" style={{ marginBottom: 16 }}>
            Institutions with the highest standard deviation of rank across all years they appeared (min 4 years).
          </div>
          {l3 ? <div className="loading-wrap"><div className="spinner" /></div> :
            vol?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: vol.slice(0,15).map(r => r.name?.length > 30 ? r.name.slice(0,28)+'…' : r.name),
                      y: vol.slice(0,15).map(r => r.rank_std),
                      marker: {
                        color: vol.slice(0,15).map((_, i) => `hsl(${360 - i * 18}, 70%, 60%)`),
                      },
                      text: vol.slice(0,15).map(r => r.rank_std?.toFixed(1)),
                      textposition: 'outside',
                    }]}
                    layout={{
                      title: { text: `Rank Volatility (Std Dev) — ${category}`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { tickangle: -30 },
                      yaxis: { title: 'Rank Std Dev' },
                      height: 420,
                    }}
                  />
                  <DataTable data={vol.slice(0,20)} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}
    </div>
  );
}
