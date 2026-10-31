/**
 * Bivariate.jsx — Q4.1–Q4.5 correlation & scatter analysis.
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchRpcVsScore, fetchPerceptionVsScore,
  fetchAllParamsCorr, fetchTlrVsRpc,
  fetchTwoVariable, fetchCorrTrend,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

const TABS = [
  'Q4.1 RPC vs Score',
  'Q4.2 Perception vs Score',
  'Q4.3 Best Parameter Correlation',
  'Q4.4 TLR vs RPC',
  'Q4.5 Correlation Trend',
  '⭐ Dynamic 2-Variable',
];

const NUM_PARAMS = ['score','tlr','rpc','go','oi','perception','rank'];

function ScatterPanel({ r, data, xKey, yKey, title }) {
  if (!data?.length) return <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>;
  return (
    <>
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3,1fr)', marginBottom: 20 }}>
        <div className="kpi-card">
          <div className="kpi-label">Pearson r</div>
          <div className="kpi-value" style={{ fontSize: '1.6rem' }}>{r?.toFixed(3) ?? '—'}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Strength</div>
          <div className="kpi-value" style={{ fontSize: '1.2rem' }}>
            {Math.abs(r) > 0.7 ? 'Strong' : Math.abs(r) > 0.4 ? 'Moderate' : 'Weak'}
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Direction</div>
          <div className="kpi-value" style={{ fontSize: '1.2rem' }}>
            {r >= 0 ? '↑ Positive' : '↓ Negative'}
          </div>
        </div>
      </div>
      <PlotlyChart
        data={[{
          type: 'scatter', mode: 'markers',
          x: data.map(d => d[xKey]),
          y: data.map(d => d[yKey]),
          text: data.map(d => d.name),
          hovertemplate: '<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>',
          marker: { color: '#6366f1', size: 7, opacity: 0.75 },
        }]}
        layout={{
          title: { text: title, font: { color: '#f1f5f9', size: 14 } },
          xaxis: { title: xKey.toUpperCase() },
          yaxis: { title: yKey.toUpperCase() },
          height: 420,
        }}
      />
    </>
  );
}

export default function Bivariate() {
  const { year, category } = useContext(FilterContext);
  const [tab, setTab] = useState(0);
  const [v1, setV1] = useState('tlr');
  const [v2, setV2] = useState('score');

  const { data: rpcScore, loading: l1 } = useApi(() => fetchRpcVsScore(year, category), [year, category]);
  const { data: percScore, loading: l2 } = useApi(() => fetchPerceptionVsScore(year, category), [year, category]);
  const { data: allCorr, loading: l3 }  = useApi(() => fetchAllParamsCorr(year, category), [year, category]);
  const { data: tlrRpc, loading: l4 }   = useApi(() => fetchTlrVsRpc(year, category), [year, category]);
  const { data: corrTrend, loading: l5 } = useApi(() => fetchCorrTrend('rpc','score', category), [category]);
  const { data: dynData, loading: l6 }  = useApi(() => fetchTwoVariable(v1, v2, year, category), [v1, v2, year, category]);

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">🔗</span> Bivariate & Correlation Analysis</div>
        <div className="section-desc">Explore relationships between NIRF parameters using scatter plots and Pearson correlation.</div>
      </div>

      <div className="tabs">
        {TABS.map((t, i) => (
          <button key={i} className={`tab-btn ${tab === i ? 'active' : ''}`} onClick={() => setTab(i)}>{t}</button>
        ))}
      </div>

      {tab === 0 && (
        <div className="card">
          {l1 ? <div className="loading-wrap"><div className="spinner" /></div> :
            <ScatterPanel r={rpcScore?.r} data={rpcScore?.data} xKey="rpc" yKey="score"
              title={`RPC vs Overall Score — ${category} ${year} (r = ${rpcScore?.r?.toFixed(3)})`} />}
        </div>
      )}

      {tab === 1 && (
        <div className="card">
          {l2 ? <div className="loading-wrap"><div className="spinner" /></div> :
            <ScatterPanel r={percScore?.r} data={percScore?.data} xKey="perception" yKey="score"
              title={`Perception vs Overall Score — ${category} ${year} (r = ${percScore?.r?.toFixed(3)})`} />}
        </div>
      )}

      {tab === 2 && (
        <div className="card">
          {l3 ? <div className="loading-wrap"><div className="spinner" /></div> :
            allCorr?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: allCorr.map(r => r.parameter),
                      y: allCorr.map(r => r.correlation),
                      marker: { color: allCorr.map(r => r.correlation > 0 ? '#10b981' : '#ef4444') },
                      text: allCorr.map(r => r.correlation.toFixed(3)),
                      textposition: 'outside',
                    }]}
                    layout={{
                      title: { text: `Parameter Correlation with Overall Score — ${year}`, font: { color: '#f1f5f9', size: 14 } },
                      yaxis: { title: 'Pearson r', range: [-1.1, 1.1] },
                      height: 360,
                    }}
                  />
                  <DataTable data={allCorr} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {tab === 3 && (
        <div className="card">
          {l4 ? <div className="loading-wrap"><div className="spinner" /></div> :
            <ScatterPanel r={tlrRpc?.r} data={tlrRpc?.data} xKey="tlr" yKey="rpc"
              title={`TLR vs RPC — ${category} ${year} (r = ${tlrRpc?.r?.toFixed(3)})`} />}
        </div>
      )}

      {tab === 4 && (
        <div className="card">
          {l5 ? <div className="loading-wrap"><div className="spinner" /></div> :
            corrTrend?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'scatter', mode: 'lines+markers',
                      x: corrTrend.map(r => r.year),
                      y: corrTrend.map(r => r.r),
                      line: { color: '#22d3ee', width: 2 },
                      marker: { size: 8, color: '#22d3ee' },
                      name: 'r (RPC vs Score)',
                    }]}
                    layout={{
                      title: { text: `Correlation Trend (RPC vs Score) — ${category}`, font: { color: '#f1f5f9', size: 14 } },
                      xaxis: { title: 'Year' },
                      yaxis: { title: 'Pearson r', range: [0, 1] },
                    }}
                  />
                  <DataTable data={corrTrend} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      )}

      {tab === 5 && (
        <div className="card">
          <div className="control-row">
            {[['X Variable', v1, setV1], ['Y Variable', v2, setV2]].map(([label, val, setter]) => (
              <div className="form-group" key={label}>
                <label className="form-label">{label}</label>
                <select className="form-select" value={val} onChange={e => setter(e.target.value)}>
                  {NUM_PARAMS.map(p => <option key={p} value={p}>{p.toUpperCase()}</option>)}
                </select>
              </div>
            ))}
          </div>
          {l6 ? <div className="loading-wrap"><div className="spinner" /></div> :
            <ScatterPanel r={dynData?.r} data={dynData?.data} xKey={v1} yKey={v2}
              title={`${v1.toUpperCase()} vs ${v2.toUpperCase()} — ${category} ${year} (r = ${dynData?.r?.toFixed(3)})`} />
          }
        </div>
      )}
    </div>
  );
}
