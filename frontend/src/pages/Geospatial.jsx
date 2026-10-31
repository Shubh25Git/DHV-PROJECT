/**
 * Geospatial.jsx — Q2.1–Q2.5 Regional & State analysis.
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchTopStates, fetchGeoDistributionTrend, fetchStateGrowth,
  fetchCompareStates, fetchNewlyAppearing,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const TABS = [
  'Q2.1 Top States',
  'Q2.2 Distribution Trend (2017–2025)',
  'Q2.3 State Growth',
  'Q2.4 Compare States',
  'Q2.5 Newly Appearing',
];

export default function Geospatial() {
  const { year, category, allYears, allStates } = useContext(FilterContext);
  const [tab, setTab] = useState(0);

  // Q2.1
  const { data: stateData, loading: sL } = useApi(
    () => fetchTopStates(year, category), [year, category]
  );

  // Q2.2
  const { data: trendData, loading: tL } = useApi(
    () => fetchGeoDistributionTrend(category, 100), [category]
  );

  // Q2.3
  const minYear = allYears[0] ?? 2017;
  const { data: growthData, loading: gL } = useApi(
    () => fetchStateGrowth(category, minYear, year), [category, minYear, year]
  );

  // Q2.4
  const [s1, setS1] = useState('Karnataka');
  const [s2, setS2] = useState('Tamil Nadu');
  const { data: compareData, loading: cL } = useApi(
    () => fetchCompareStates(s1, s2, category, year), [s1, s2, category, year]
  );

  // Q2.5
  const { data: newData, loading: nL } = useApi(
    () => fetchNewlyAppearing(category, minYear, year), [category, minYear, year]
  );

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">🗺️</span> Geospatial & Regional Analysis</div>
        <div className="section-desc">How geography shapes India's higher education rankings.</div>
      </div>

      <div className="tabs">
        {TABS.map((t, i) => (
          <button key={i} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
        ))}
      </div>

      {/* Q2.1 Top States */}
      {tab === 0 && (
        <div className="card">
          {sL ? <div className="loading-wrap"><div className="spinner" /></div> :
            stateData?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: stateData.map(r => r.state),
                      y: stateData.map(r => r.institution_count),
                      marker: {
                        color: stateData.map((_, i) => `hsl(${240 - i * 12}, 70%, ${60 - i * 2}%)`),
                      },
                      text: stateData.map(r => r.institution_count),
                      textposition: 'outside',
                    }]}
                    layout={{
                      title: { text: `States with Most Top-100 Institutions (${year} · ${category})`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { tickangle: -30 },
                      yaxis: { title: 'Institution Count' },
                      height: 400,
                    }}
                  />
                  <DataTable data={stateData} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {/* Q2.2 Geographical Distribution Trend */}
      {tab === 1 && (
        <div className="card">
          <div className="section-desc" style={{ marginBottom: 16 }}>
            Evolution of state-wise representation in the top 100 from 2017 to 2025 in {category}.
            States are sorted from highest to lowest overall top-100 institutional presence.
          </div>
          {tL ? <div className="loading-wrap"><div className="spinner" /></div> :
            trendData?.records?.length
              ? <>
                  {trendData.figure && (
                    <PlotlyChart
                      data={trendData.figure.data}
                      layout={{
                        ...trendData.figure.layout,
                        paper_bgcolor: 'transparent',
                        plot_bgcolor: 'transparent',
                        font: { color: '#f1f5f9' },
                        height: Math.max(480, (trendData.records.length || 20) * 24 + 140),
                      }}
                    />
                  )}
                  <div style={{ marginTop: 24 }}>
                    <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>
                      State Representation Counts by Year (2017–2025)
                    </div>
                    <DataTable data={trendData.records} />
                  </div>
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No trend data available.</h3></div>
          }
        </div>
      )}

      {/* Q2.3 State Growth */}
      {tab === 2 && (
        <div className="card">
          {gL ? <div className="loading-wrap"><div className="spinner" /></div> :
            growthData?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar', orientation: 'h',
                      x: growthData.slice(0, 15).map(r => r.growth),
                      y: growthData.slice(0, 15).map(r => r.state),
                      marker: { color: growthData.slice(0,15).map(r => r.growth >= 0 ? '#10b981' : '#ef4444') },
                    }]}
                    layout={{
                      title: { text: `State Representation Growth (${minYear}→${year})`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { title: 'Change in Top-100 Institutions' },
                      height: 460,
                    }}
                  />
                  <DataTable data={growthData} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {/* Q2.4 Compare States */}
      {tab === 3 && (
        <div className="card">
          <div className="control-row">
            {[['State 1', s1, setS1], ['State 2', s2, setS2]].map(([label, val, setter]) => (
              <div className="form-group" key={label}>
                <label className="form-label">{label}</label>
                <select className="form-select" value={val} onChange={e => setter(e.target.value)}>
                  {allStates.map(st => <option key={st} value={st}>{st}</option>)}
                </select>
              </div>
            ))}
          </div>
          {cL ? <div className="loading-wrap"><div className="spinner" /></div> :
            compareData?.summary?.length
              ? <>
                  <DataTable data={compareData.summary} />
                  <div style={{ marginTop: 20 }}>
                    <PlotlyChart
                      data={[
                        { type: 'bar', name: 'Avg Score',
                          x: compareData.summary.map(r => r.state),
                          y: compareData.summary.map(r => r.average_score),
                          marker: { color: ['#6366f1', '#22d3ee'] } },
                      ]}
                      layout={{
                        title: { text: `${s1} vs ${s2} — Average Score (${year})`, font: { color: '#f1f5f9', size: 14 } },
                        height: 320,
                      }}
                    />
                  </div>
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data for selected states.</h3></div>
          }
        </div>
      )}

      {/* Q2.5 Newly Appearing */}
      {tab === 4 && (
        <div className="card">
          {nL ? <div className="loading-wrap"><div className="spinner" /></div> :
            newData?.summary?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: newData.summary.map(r => r.state),
                      y: newData.summary.map(r => r.new_institutions_count),
                      marker: { color: '#a78bfa' },
                      text: newData.summary.map(r => r.new_institutions_count),
                      textposition: 'outside',
                    }]}
                    layout={{
                      title: { text: `New Entrants by State (${minYear}→${year})`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { tickangle: -30 },
                      height: 400,
                    }}
                  />
                  <DataTable data={newData.records?.slice(0, 30) || []} columns={['name','state','rank','score']} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No newly appearing institutions.</h3></div>
          }
        </div>
      )}
    </div>
  );
}
