/**
 * Statistics.jsx — Q6 distribution & statistical comparison.
 */

import { useContext, useState } from 'react';
import { FilterContext } from '../App';
import { useApi } from '../hooks/useApi';
import {
  fetchTop10VsRest, fetchDispersion,
  fetchParamVariability, fetchMedianIqrTrend,
  fetchStateScoreDistribution,
} from '../api';
import PlotlyChart from '../components/PlotlyChart';
import DataTable from '../components/DataTable';

export default function Statistics() {
  const { year, category } = useContext(FilterContext);
  const [minInst, setMinInst] = useState(3);

  const { data: t10Rest, loading: l1 } = useApi(() => fetchTop10VsRest(year, category), [year, category]);
  const { data: disp, loading: l2 }   = useApi(() => fetchDispersion(category), [category]);
  const { data: pVar, loading: l3 }   = useApi(() => fetchParamVariability(year, category), [year, category]);
  const { data: iqr, loading: l4 }    = useApi(() => fetchMedianIqrTrend(category), [category]);
  const { data: stateScoreData, loading: l5 } = useApi(
    () => fetchStateScoreDistribution(year, category, minInst),
    [year, category, minInst]
  );

  return (
    <div>
      <div className="section-header">
        <div className="section-title"><span className="icon">📋</span> Statistical Comparison</div>
        <div className="section-desc">Distribution analysis, dispersion, and variability across years and parameters.</div>
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* Q6.1 Top 10 vs Rest */}
        <div className="card">
          <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>Q6.1 — Top 10 vs Rest (Box)</div>
          {l1 ? <div className="loading-wrap"><div className="spinner" /></div> :
            t10Rest
              ? <>
                  <DataTable data={t10Rest.summary} />
                  <PlotlyChart
                    data={[
                      { type: 'box', y: t10Rest.top10_scores, name: 'Top 10', marker: { color: '#6366f1' } },
                      { type: 'box', y: t10Rest.rest_scores,  name: 'Rest',   marker: { color: '#94a3b8' } },
                    ]}
                    layout={{
                      title: { text: `Score Distribution: Top 10 vs Rest — ${year}`, font: { color: '#f1f5f9', size: 13 } },
                      yaxis: { title: 'Score' },
                      height: 360,
                    }}
                  />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>

        {/* Q6.3 Parameter Variability */}
        <div className="card">
          <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>Q6.3 — Parameter Variability (CV %)</div>
          {l3 ? <div className="loading-wrap"><div className="spinner" /></div> :
            pVar?.length
              ? <>
                  <PlotlyChart
                    data={[{
                      type: 'bar',
                      x: pVar.map(r => r.parameter.toUpperCase()),
                      y: pVar.map(r => r.coefficient_of_variation_pct),
                      marker: { color: '#22d3ee' },
                      text: pVar.map(r => r.coefficient_of_variation_pct?.toFixed(1) + '%'),
                      textposition: 'outside',
                    }]}
                    layout={{
                      title: { text: `Coefficient of Variation % — ${category} ${year}`, font: { color: '#f1f5f9', size: 13 } },
                      yaxis: { title: 'CV %' },
                      height: 320,
                    }}
                  />
                  <DataTable data={pVar} />
                </>
              : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
          }
        </div>
      </div>

      {/* Q6.2 Score Dispersion Over Years */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>Q6.2 — Score Dispersion Over Years</div>
        {l2 ? <div className="loading-wrap"><div className="spinner" /></div> :
          disp?.length
            ? <>
                <PlotlyChart
                  data={[
                    { type: 'scatter', mode: 'lines+markers', x: disp.map(r=>r.year), y: disp.map(r=>r.std), name: 'Std Dev', line:{color:'#6366f1'}, marker:{size:7} },
                    { type: 'scatter', mode: 'lines+markers', x: disp.map(r=>r.year), y: disp.map(r=>r.iqr), name: 'IQR', line:{color:'#22d3ee',dash:'dot'}, marker:{size:7} },
                  ]}
                  layout={{
                    title: { text: `Score Dispersion Over Years — ${category}`, font: { color: '#f1f5f9', size: 14 } },
                    xaxis: { title: 'Year' },
                    yaxis: { title: 'Spread (points)' },
                  }}
                />
                <DataTable data={disp} />
              </>
            : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
        }
      </div>

      {/* Q6.4 Median & IQR Trend */}
      <div className="card">
        <div className="section-title" style={{ fontSize: '0.95rem', marginBottom: 12 }}>Q6.4 — Median & IQR Trend</div>
        {l4 ? <div className="loading-wrap"><div className="spinner" /></div> :
          iqr?.length
            ? <>
                <PlotlyChart
                  data={[
                    { type: 'scatter', mode: 'lines+markers', x: iqr.map(r=>r.year), y: iqr.map(r=>r.median), name: 'Median', line:{color:'#f59e0b'}, marker:{size:7} },
                    { type: 'scatter', mode: 'lines+markers', x: iqr.map(r=>r.year), y: iqr.map(r=>r.iqr), name: 'IQR', line:{color:'#a78bfa',dash:'dot'}, marker:{size:7} },
                  ]}
                  layout={{
                    title: { text: `Median & IQR Over Years — ${category}`, font: { color: '#f1f5f9', size: 14 } },
                    xaxis: { title: 'Year' },
                    yaxis: { title: 'Score / Points' },
                  }}
                />
                <DataTable data={iqr} />
              </>
            : <div className="empty-state"><div className="icon">📭</div><h3>No data.</h3></div>
        }
      </div>

      {/* Q6.5 State-wise Score Distribution */}
      <div className="card" style={{ marginTop: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div className="section-title" style={{ fontSize: '0.95rem' }}>
              Q6.5 — State-wise Score Distribution (Box Plot)
            </div>
            <div className="section-desc" style={{ marginTop: 4 }}>
              Comparing medians, interquartile ranges, and outlier scores across states (minimum {minInst} institutions) in {category} ({year}).
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <label className="form-label" style={{ marginBottom: 0, fontSize: '0.8rem' }}>Min Institutions:</label>
            <select
              className="form-select"
              style={{ width: 'auto', padding: '4px 10px', fontSize: '0.85rem' }}
              value={minInst}
              onChange={(e) => setMinInst(Number(e.target.value))}
            >
              {[1, 2, 3, 5, 8, 10].map((n) => (
                <option key={n} value={n}>{n}+</option>
              ))}
            </select>
          </div>
        </div>

        {l5 ? (
          <div className="loading-wrap"><div className="spinner" /></div>
        ) : stateScoreData?.records?.length ? (
          <>
            <PlotlyChart
              data={stateScoreData.figure?.data || [{
                type: 'box',
                x: stateScoreData.records.map(r => r.state),
                y: stateScoreData.records.map(r => r.score),
                boxpoints: 'outliers',
                marker: { color: '#6366f1' },
              }]}
              layout={{
                ...(stateScoreData.figure?.layout || {}),
                title: { text: `State-wise Score Distribution — ${category} (${year})`, font: { color: '#f1f5f9', size: 14 } },
                xaxis: { tickangle: -35, title: 'State / Union Territory' },
                yaxis: { title: 'NIRF Overall Score' },
                height: 440,
              }}
            />
            <DataTable data={stateScoreData.records} maxRows={25} />
          </>
        ) : (
          <div className="empty-state">
            <div className="icon">📭</div>
            <h3>No states have at least {minInst} institutions in {category} ({year}).</h3>
          </div>
        )}
      </div>
    </div>
  );
}
