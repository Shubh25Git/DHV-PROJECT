/**
 * Multivariate.jsx — Q5 multivariate profiling analysis.
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchTopProfiles,
  fetchHighResearchLowTeaching,
  fetchHighTeachingLowPerception,
  fetchImprovedScoreDecliningParams,
  fetchStrongestWeakestGap,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const PARAMS = ['tlr', 'rpc', 'go', 'oi', 'perception'];

export default function Multivariate() {
  const { year, category, allYears = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025] } = useContext(FilterContext);

  const [startYear, setStartYear] = useState(2017);
  const [endYear, setEndYear] = useState(2024);

  const { data: profiles, loading: pL } = useApi(() => fetchTopProfiles(year, category, 5), [year, category]);
  const { data: hrlt, loading: hL }     = useApi(() => fetchHighResearchLowTeaching(year, category), [year, category]);
  const { data: htlp, loading: htL }    = useApi(() => fetchHighTeachingLowPerception(year, category), [year, category]);
  const { data: impData, loading: impL } = useApi(
    () => fetchImprovedScoreDecliningParams(category, startYear, endYear),
    [category, startYear, endYear]
  );
  const { data: gap, loading: gL }      = useApi(() => fetchStrongestWeakestGap(year, category), [year, category]);

  const handleStartYearChange = (e) => {
    const newStart = parseInt(e.target.value, 10);
    setStartYear(newStart);
    if (endYear <= newStart) {
      const laterYears = allYears.filter(y => y > newStart);
      if (laterYears.length > 0) {
        setEndYear(laterYears[laterYears.length - 1]);
      }
    }
  };

  const handleEndYearChange = (e) => {
    setEndYear(parseInt(e.target.value, 10));
  };

  // Build radar data from profiles
  const radarData = profiles?.map(inst => ({
    type: 'scatterpolar',
    r: PARAMS.map(p => inst[p] ?? 0),
    theta: PARAMS.map(p => p.toUpperCase()),
    fill: 'toself',
    name: inst.name?.length > 30 ? inst.name.slice(0, 28) + '…' : inst.name,
    opacity: 0.7,
  })) ?? [];

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">🕸️</span> Multivariate Analysis</div>
        <div className="section-desc">Multi-parameter profiling and cross-dimensional comparisons.</div>
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* Q5.1 Radar */}
        <div className="card">
          <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 16 }}>
            Q5.1 — Top 5 Parameter Radar
          </div>
          {pL ? <div className="loading-wrap"><div className="spinner" /></div> :
            radarData.length
              ? <PlotlyChart
                  data={radarData}
                  layout={{
                    polar: {
                      bgcolor: 'transparent',
                      radialaxis: { visible: true, range: [0, 100], gridcolor: 'rgba(255,255,255,0.08)', color: '#94a3b8' },
                      angularaxis: { gridcolor: 'rgba(255,255,255,0.08)', color: '#94a3b8' },
                    },
                    title: { text: `Top 5 Profile Radar — ${category} ${year}`, font: { color: '#f1f5f9', size: 14 } },
                    height: 400,
                    showlegend: true,
                  }}
                />
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>

        {/* Q5.2 High Research Low Teaching */}
        <div className="card">
          <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 16 }}>
            Q5.2 — High Research, Low Teaching Institutions
          </div>
          <div className="section-desc" style={{ marginBottom: 12 }}>
            RPC ≥ 75th percentile & TLR ≤ 50th percentile in {year}
          </div>
          {hL ? <div className="loading-wrap"><div className="spinner" /></div> :
            hrlt?.length
              ? <DataTable data={hrlt} columns={['name','state','rank','rpc','tlr','score']} />
              : <div className="empty-state"><div className="icon">✅</div><h3>No institutions met this threshold.</h3></div>
          }
        </div>
      </div>

      {/* Q5.3 High Teaching, Low Perception */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 8 }}>
          Q5.3 — High Teaching Scores but Low Perception Institutions
        </div>
        <div className="section-desc" style={{ marginBottom: 16 }}>
          Institutions with TLR ≥ 75th percentile and Peer Perception (PR) ≤ 50th percentile in {category} ({year}).
        </div>

        {htL ? <div className="loading-wrap"><div className="spinner" /></div> :
          htlp ? (
            <>
              <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', marginBottom: 20 }}>
                <div className="kpi-card">
                  <div className="kpi-label">TLR 75th %ile Cutoff</div>
                  <div className="kpi-value" style={{ color: '#6366f1', fontSize: '1.4rem' }}>{htlp.tlr_threshold}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">PR 50th %ile Cutoff</div>
                  <div className="kpi-value" style={{ color: '#06b6d4', fontSize: '1.4rem' }}>{htlp.perception_threshold}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">Qualifying Institutions</div>
                  <div className="kpi-value" style={{ color: '#f59e0b', fontSize: '1.4rem' }}>{htlp.count}</div>
                </div>
              </div>

              {htlp.figure && (
                <PlotlyChart
                  data={htlp.figure.data}
                  layout={{
                    ...htlp.figure.layout,
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    font: { color: '#f1f5f9' },
                    height: 420,
                  }}
                />
              )}

              {htlp.records?.length > 0 ? (
                <div style={{ marginTop: 24 }}>
                  <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>
                    Qualifying Outliers ({htlp.records.length})
                  </div>
                  <DataTable data={htlp.records} columns={['name', 'rank', 'score', 'tlr', 'perception']} />
                </div>
              ) : (
                <div className="empty-state" style={{ marginTop: 16 }}>
                  <div className="icon">✅</div>
                  <h3>No institutions met both thresholds for high teaching and low perception.</h3>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state"><div className="icon">📭</div><h3>No data available.</h3></div>
          )
        }
      </div>

      {/* Q5.4 Improving Overall Scores Despite Declining Parameters */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
          <div>
            <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 4 }}>
              Q5.4 — Improving Overall Scores Despite Declining Parameters
            </div>
            <div className="section-desc">
              Institutions whose overall score increased while experiencing a decline in at least one NIRF parameter.
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <label style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Start Year:</label>
              <select
                className="select"
                value={startYear}
                onChange={handleStartYearChange}
                style={{ background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: 6, padding: '4px 10px' }}
              >
                {allYears.slice(0, -1).map(y => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <label style={{ fontSize: '0.85rem', color: '#94a3b8' }}>End Year:</label>
              <select
                className="select"
                value={endYear}
                onChange={handleEndYearChange}
                style={{ background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: 6, padding: '4px 10px' }}
              >
                {allYears.filter(y => y > startYear).map(y => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {impL ? <div className="loading-wrap"><div className="spinner" /></div> :
          impData ? (
            <>
              <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', marginBottom: 20 }}>
                <div className="kpi-card">
                  <div className="kpi-label">Base Period</div>
                  <div className="kpi-value" style={{ color: '#6366f1', fontSize: '1.4rem' }}>{startYear} → {endYear}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">Category</div>
                  <div className="kpi-value" style={{ color: '#06b6d4', fontSize: '1.4rem' }}>{category}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">Qualifying Institutions</div>
                  <div className="kpi-value" style={{ color: '#10b981', fontSize: '1.4rem' }}>{impData.count}</div>
                </div>
              </div>

              {impData.figure && (
                <PlotlyChart
                  data={impData.figure.data}
                  layout={{
                    ...impData.figure.layout,
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    font: { color: '#f1f5f9' },
                    height: Math.max(420, (impData.records?.length || 5) * 28 + 120),
                  }}
                />
              )}

              {impData.records?.length > 0 ? (
                <div style={{ marginTop: 24 }}>
                  <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>
                    Qualifying Institutions ({impData.records.length})
                  </div>
                  <DataTable
                    data={impData.records}
                    columns={['name', 'score_improvement', 'start_score', 'end_score', 'declined_parameters', 'num_declined']}
                  />
                </div>
              ) : (
                <div className="empty-state" style={{ marginTop: 16 }}>
                  <div className="icon">ℹ️</div>
                  <h3>No institutions improved overall score with declining parameters between {startYear} and {endYear}.</h3>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state"><div className="icon">📭</div><h3>No data available.</h3></div>
          )
        }
      </div>

      {/* Q5.5 Strongest vs Weakest gap */}
      <div className="card">
        <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 16 }}>
          Q5.5 — Largest Strongest vs Weakest Parameter Gap
        </div>
        {gL ? <div className="loading-wrap"><div className="spinner" /></div> :
          gap?.length
            ? <>
                <PlotlyChart
                  data={[{
                    type: 'bar',
                    x: gap.slice(0, 15).map(r => r.name?.length > 35 ? r.name.slice(0,33)+'…' : r.name),
                    y: gap.slice(0, 15).map(r => r.gap),
                    marker: { color: '#f59e0b' },
                    text: gap.slice(0,15).map(r => r.gap.toFixed(1)),
                    textposition: 'outside',
                  }]}
                  layout={{
                    title: { text: `Parameter Gap (Best − Worst) — ${category} ${year}`, font: { color: '#f1f5f9', size: 14 } },
                    xaxis: { tickangle: -30 },
                    yaxis: { title: 'Score Gap' },
                    height: 420,
                  }}
                />
                <DataTable data={gap.slice(0, 15)} />
              </>
            : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
        }
      </div>
    </div>
  );
}
