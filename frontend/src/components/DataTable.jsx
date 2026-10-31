/**
 * DataTable.jsx — Reusable dark-themed sortable data table.
 */

import { useState } from 'react';

function fmt(val) {
  if (val === null || val === undefined) return '—';
  if (typeof val === 'number') return Number.isInteger(val) ? val : val.toFixed(2);
  return String(val);
}

export default function DataTable({ data = [], columns = null, maxRows = 50 }) {
  const [sortKey, setSortKey]   = useState(null);
  const [sortAsc, setSortAsc]   = useState(true);

  if (!data.length) {
    return (
      <div className="empty-state">
        <div className="icon">📭</div>
        <h3>No data available</h3>
        <p>Try adjusting the filters.</p>
      </div>
    );
  }

  const cols = columns || Object.keys(data[0]);

  const sorted = sortKey
    ? [...data].sort((a, b) => {
        const av = a[sortKey], bv = b[sortKey];
        if (av == null) return 1;
        if (bv == null) return -1;
        return sortAsc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
      })
    : data;

  const rows = sorted.slice(0, maxRows);

  const handleSort = (key) => {
    if (sortKey === key) setSortAsc(a => !a);
    else { setSortKey(key); setSortAsc(true); }
  };

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {cols.map(col => (
              <th key={col} onClick={() => handleSort(col)} style={{ cursor: 'pointer', userSelect: 'none' }}>
                {col.replace(/_/g, ' ').toUpperCase()}
                {sortKey === col ? (sortAsc ? ' ↑' : ' ↓') : ''}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {cols.map(col => (
                <td key={col}>
                  {col === 'rank'
                    ? <span className="rank-badge">
                        {fmt(row[col])}
                      </span>
                    : fmt(row[col])
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > maxRows && (
        <p style={{ padding: '10px 14px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Showing first {maxRows} of {data.length} rows.
        </p>
      )}
    </div>
  );
}
