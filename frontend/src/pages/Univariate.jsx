/**
 * Univariate.jsx — Q3.1–Q3.5 single-variable distribution analysis.
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchScoreDistribution, fetchRankDistribution, fetchSummaryStats,
  fetchQuartiles, fetchSpreadByCategory,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const TABS = [
  'Q3.1 Score Histogram',
  'Q3.2 Rank Distribution',
  'Q3.3 Summary Stats',
  'Q3.4 Quartile Breakdown',
  'Q3.5 Category Spread',
];

export default function Univariate() {
  const { year, category } = useContext(FilterContext);
  const [tab, setTab] = useState(0);

  const { data: distData, loading: dL } = useApi(
    () => fetchScoreDistribution(year, category), [year, category]
  );
  const { data: rankData, loading: rL } = useApi(
    () => fetchRankDistribution(year, category), [year, category]
  );
  const { data: stats, loading: sL } = useApi(
    () => fetchSummaryStats(year, category), [year, category]
  );
  const { data: quartiles, loading: qL } = useApi(
    () => fetchQuartiles(year, category), [year, category]
  );
  const { data: spread, loading: spL } = useApi(
    () => fetchSpreadByCategory(year), [year]
  );

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">📉</span> Univariate Analysis</div>
        <div className="section-desc">Score and rank distributions for a single year and category.</div>
      </div>

      <div className="tabs">
        {TABS.map((t, i) => (
          <button key={i} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
        ))}
      </div>

      {/* Q3.1 Histogram */}
      {tab === 0 && (
        <div className="card">
          {dL ? <div className="loading-wrap"><div className="spinner" /></div> :
            distData?.scores?.length
              ? <PlotlyChart
                  data={[{
                    type: 'histogram',
                    x: distData.scores,
                    nbinsx: 30,
                    marker: { color: 'rgba(99,102,241,0.75)', line: { color: '#6366f1', width: 1 } },
                  }]}
                  layout={{
                    title: { text: `NIRF Score Distribution — ${category} ${year}`, font: { color: '#f1f5f9', size: 14 } },
                    xaxis: { title: 'Score' },
                    yaxis: { title: 'Count' },
                    bargap: 0.05,
                  }}
                />
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {/* Q3.2 Rank Distribution */}
      {tab === 1 && (
        <div className="card">
          <div className="section-desc" style={{ marginBottom: 16 }}>
            Distribution of overall ranks grouped into meaningful rank tiers (Top 10, 11–25, 26–50, 51–100, 101–150, 151+).
          </div>
          {rL ? <div className="loading-wrap"><div className="spinner" /></div> :
            rankData?.bands?.length
              ? <>
                  <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))', marginBottom: 20 }}>
                    <div className="kpi-card">
                      <div className="kpi-label">Total Ranked</div>
                      <div className="kpi-value" style={{ color: '#6366f1', fontSize: '1.4rem' }}>{rankData.total_ranked}</div>
                    </div>
                    {rankData.bands.map(b => (
                      <div className="kpi-card" key={b.band}>
                        <div className="kpi-label">{b.band}</div>
                        <div className="kpi-value" style={{ fontSize: '1.4rem' }}>{b.count}</div>
                      </div>
                    ))}
                  </div>

                  {rankData.figure && (
                    <PlotlyChart
                      data={rankData.figure.data}
                      layout={{
                        ...rankData.figure.layout,
                        paper_bgcolor: 'transparent',
                        plot_bgcolor: 'transparent',
                        font: { color: '#f1f5f9' },
                        height: 420,
                      }}
                    />
                  )}

                  {rankData.records?.length > 0 && (
                    <div style={{ marginTop: 24 }}>
                      <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>
                        Ranked Institutions ({rankData.records.length})
                      </div>
                      <DataTable data={rankData.records} columns={['name', 'rank', 'score', 'state']} />
                    </div>
                  )}
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No rank distribution data.</h3></div>
          }
        </div>
      )}

      {/* Q3.3 Summary Stats */}
      {tab === 2 && (
        <div className="card">
          {sL ? <div className="loading-wrap"><div className="spinner" /></div> :
            stats
              ? <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))' }}>
                  {Object.entries(stats).map(([k, v]) => (
                    <div className="kpi-card" key={k}>
                      <div className="kpi-label">{k.replace(/_/g,' ')}</div>
                      <div className="kpi-value" style={{ fontSize: '1.4rem' }}>{typeof v === 'number' ? v.toFixed(2) : v}</div>
                    </div>
                  ))}
                </div>
              : <div className="empty-state"><div className="icon">📭</div><h3>No stats.</h3></div>
          }
        </div>
      )}

      {/* Q3.4 Quartiles */}
      {tab === 3 && (
        <div className="card">
          {qL ? <div className="loading-wrap"><div className="spinner" /></div> :
            quartiles?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'pie',
                      labels: quartiles.map(r => r.quartile),
                      values: quartiles.map(r => r.count),
                      hole: 0.45,
                      marker: { colors: ['#6366f1','#22d3ee','#10b981','#f59e0b'] },
                    }]}
                    layout={{
                      title: { text: `Score Quartile Distribution — ${category} ${year}`, font: { color: '#f1f5f9', size: 14 } },
                      height: 380,
                    }}
                  />
                  <DataTable data={quartiles} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {/* Q3.5 Category Spread */}
      {tab === 4 && (
        <div className="card">
          {spL ? <div className="loading-wrap"><div className="spinner" /></div> :
            spread?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: spread.map(r => r.category),
                      y: spread.map(r => r.std),
                      name: 'Std Dev',
                      marker: { color: '#a78bfa' },
                    }]}
                    layout={{
                      title: { text: `Score Spread (Std Dev) by Category — ${year}`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { tickangle: -30 },
                      yaxis: { title: 'Std Dev of Score' },
                      height: 400,
                    }}
                  />
                  <DataTable data={spread} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}
    </div>
  );
}
