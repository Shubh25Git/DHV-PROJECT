/**
 * TimeSeries.jsx — All 5 time-series analysis questions (Q1.1 – Q1.5).
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchInstitutions, fetchInstitutionTrend,
  fetchAverageScoreTrend, fetchImprovements,
  fetchDeclines, fetchConsistentTop,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const TABS = [
  'Q1.1 Institution Trajectory',
  'Q1.2 Biggest Improvements',
  'Q1.3 Biggest Declines',
  'Q1.4 Average Score Trend',
  'Q1.5 Consistent Top Institutions',
];

export default function TimeSeries() {
  const { year, category, allYears } = useContext(FilterContext);
  const [tab, setTab] = useState(0);

  // Q1.1
  const { data: instList } = useApi(() => fetchInstitutions(category), [category]);
  const [selectedInst, setSelectedInst] = useState('');
  const instQuery = selectedInst || (instList?.[0] ?? '');
  const { data: trendData, loading: tL } = useApi(
    () => instQuery ? fetchInstitutionTrend(instQuery, category) : Promise.resolve([]),
    [instQuery, category]
  );

  // Q1.2 & Q1.3
  const minYear = allYears[0] ?? 2017;
  const maxYear = allYears[allYears.length - 1] ?? 2024;
  const [startY, setStartY] = useState(minYear);
  const [endY, setEndY]     = useState(maxYear);

  const { data: impData, loading: iL } = useApi(
    () => fetchImprovements(category, startY, endY), [category, startY, endY]
  );
  const { data: decData, loading: dL } = useApi(
    () => fetchDeclines(category, startY, endY), [category, startY, endY]
  );

  // Q1.4
  const { data: avgTrend, loading: aL } = useApi(
    () => fetchAverageScoreTrend(category), [category]
  );

  // Q1.5
  const [minYears, setMinYears] = useState(5);
  const { data: consistData, loading: cL } = useApi(
    () => fetchConsistentTop(category, 10, minYears), [category, minYears]
  );

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">📈</span> Time-Series & Trend Analysis</div>
        <div className="section-desc">Track how institutions and category averages evolve from 2017 to 2025.</div>
      </div>

      <div className="tabs">
        {TABS.map((t, i) => (
          <button key={i} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
        ))}
      </div>

      {/* Q1.1 */}
      {tab === 0 && (
        <div className="card">
          <div className="control-row">
            <div className="form-group">
              <label className="form-label">Select Institution</label>
              <select className="form-select" style={{ minWidth: 300 }}
                value={selectedInst} onChange={e => setSelectedInst(e.target.value)}>
                {(instList || []).map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
          </div>
          {tL ? <div className="loading-wrap"><div className="spinner" /></div> : (
            trendData?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'scatter', mode: 'lines+markers',
                      x: trendData.map(r => r.year),
                      y: trendData.map(r => r.rank),
                      name: 'Rank',
                      line: { color: '#6366f1', width: 2 },
                      marker: { size: 8 },
                    }]}
                    layout={{
                      title: { text: `Rank Trajectory — ${instQuery}`, font: { color: '#f1f5f9', size: 14 } },
                      yaxis: { title: 'Rank', autorange: 'reversed' },
                      xaxis: { title: 'Year' },
                    }}
                  />
                  <DataTable data={trendData} columns={['year','rank','score','tlr','rpc']} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No trend data for this institution.</h3></div>
          )}
        </div>
      )}

      {/* Q1.2 Improvements */}
      {tab === 1 && (
        <div className="card">
          <div className="control-row">
            {['Start Year', 'End Year'].map((label, idx) => (
              <div className="form-group" key={label}>
                <label className="form-label">{label}</label>
                <select className="form-select"
                  value={idx === 0 ? startY : endY}
                  onChange={e => idx === 0 ? setStartY(+e.target.value) : setEndY(+e.target.value)}>
                  {allYears.map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
            ))}
          </div>
          {iL ? <div className="loading-wrap"><div className="spinner" /></div> : (
            impData?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar', orientation: 'h',
                      x: impData.map(r => r.rank_improvement),
                      y: impData.map(r => r.name),
                      marker: { color: '#10b981' },
                      name: 'Rank Improvement',
                    }]}
                    layout={{
                      title: { text: `Greatest Rank Improvements (${startY}→${endY})`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { title: 'Positions Climbed' },
                      yaxis: { autorange: 'reversed' },
                      height: 420,
                    }}
                  />
                  <DataTable data={impData} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data between these years.</h3></div>
          )}
        </div>
      )}

      {/* Q1.3 Declines */}
      {tab === 2 && (
        <div className="card">
          <div className="control-row">
            {['Start Year', 'End Year'].map((label, idx) => (
              <div className="form-group" key={label}>
                <label className="form-label">{label}</label>
                <select className="form-select"
                  value={idx === 0 ? startY : endY}
                  onChange={e => idx === 0 ? setStartY(+e.target.value) : setEndY(+e.target.value)}>
                  {allYears.map(y => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
            ))}
          </div>
          {dL ? <div className="loading-wrap"><div className="spinner" /></div> : (
            decData?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar', orientation: 'h',
                      x: decData.map(r => r.rank_decline),
                      y: decData.map(r => r.name),
                      marker: { color: '#ef4444' },
                      name: 'Rank Decline',
                    }]}
                    layout={{
                      title: { text: `Largest Rank Declines (${startY}→${endY})`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { title: 'Positions Dropped' },
                      height: 420,
                    }}
                  />
                  <DataTable data={decData} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          )}
        </div>
      )}

      {/* Q1.4 Average Score Trend */}
      {tab === 3 && (
        <div className="card">
          {aL ? <div className="loading-wrap"><div className="spinner" /></div> : (
            avgTrend?.length
              ? <>
                  <PlotlyChart
                    data={[
                      { type: 'scatter', mode: 'lines+markers', x: avgTrend.map(r=>r.year), y: avgTrend.map(r=>r.mean_score), name: 'Mean Score', line:{color:'#6366f1',width:2}, marker:{size:7} },
                      { type: 'scatter', mode: 'lines+markers', x: avgTrend.map(r=>r.year), y: avgTrend.map(r=>r.median_score), name: 'Median Score', line:{color:'#22d3ee',width:2,dash:'dot'}, marker:{size:7} },
                    ]}
                    layout={{
                      title: { text: `Average Score Trend — ${category}`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { title: 'Year' },
                      yaxis: { title: 'Score' },
                    }}
                  />
                  <DataTable data={avgTrend} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No trend data.</h3></div>
          )}
        </div>
      )}

      {/* Q1.5 Consistent Top */}
      {tab === 4 && (
        <div className="card">
          <div className="control-row">
            <div className="form-group">
              <label className="form-label">Min Years in Top 10</label>
              <select className="form-select" value={minYears} onChange={e => setMinYears(+e.target.value)}>
                {[2,3,4,5,6,7,8,9].map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
          </div>
          {cL ? <div className="loading-wrap"><div className="spinner" /></div> : (
            consistData?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: consistData.map(r => r.name),
                      y: consistData.map(r => r.frequency),
                      marker: { color: '#f59e0b' },
                      name: 'Years in Top 10',
                    }]}
                    layout={{
                      title: { text: `Consistently in Top 10 — ${category}`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { tickangle: -30 },
                      yaxis: { title: 'Years in Top 10' },
                      height: 380,
                    }}
                  />
                  <DataTable data={consistData} columns={['name','frequency']} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No institutions meet this threshold.</h3></div>
          )}
        </div>
      )}
    </div>
  );
}
