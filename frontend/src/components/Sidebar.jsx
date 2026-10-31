/**
 * Sidebar.jsx — Left navigation sidebar with icon + label nav items.
 */

const NAV_ITEMS = [
  { id: 'overview',      label: 'Dashboard Overview', icon: '📊', section: 'MAIN' },
  { id: 'timeseries',    label: 'Time-Series Trends',  icon: '📈', section: 'ANALYSIS' },
  { id: 'geospatial',    label: 'Geospatial Analysis', icon: '🗺️' },
  { id: 'univariate',    label: 'Univariate Analysis', icon: '📉' },
  { id: 'bivariate',     label: 'Bivariate & Correlation', icon: '🔗' },
  { id: 'multivariate',  label: 'Multivariate Analysis', icon: '🕸️' },
  { id: 'statistics',    label: 'Statistical Comparison', icon: '📋' },
  { id: 'transitions',   label: 'Ranking Transitions', icon: '🔄' },
  { id: 'outliers',      label: 'Outliers & Gaps', icon: '⚠️' },
  { id: 'dynamic',       label: 'Dynamic Explorer',    icon: '⚡', section: 'TOOLS' },
  { id: 'nlquery',       label: 'Ask NIRF Data (AI)',  icon: '💬' },
];

export default function Sidebar({ active, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="logo-icon">🎓</div>
          <div className="logo-text">
            <h1>NIRF Analytics</h1>
            <p>DHV Project · 2017–2025</p>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <div key={item.id}>
            {item.section && (
              <div className="nav-section-label">{item.section}</div>
            )}
            <div
              className={`nav-item ${active === item.id ? 'active' : ''}`}
              onClick={() => onNavigate(item.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onNavigate(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </div>
          </div>
        ))}
      </nav>

      <div style={{ padding: '12px 20px 20px', borderTop: '1px solid var(--border)' }}>
        <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
          Data: NIRF 2017–2025<br />
          Backend: FastAPI · Frontend: React + Vite
        </p>
      </div>
    </aside>
  );
}
