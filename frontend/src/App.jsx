import { useState, useEffect, createContext } from 'react'
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import TimeSeries from './pages/TimeSeries'
import Geospatial from './pages/Geospatial'
import Univariate from './pages/Univariate'
import Bivariate from './pages/Bivariate'
import Multivariate from './pages/Multivariate'
import Statistics from './pages/Statistics'
import Transitions from './pages/Transitions'
import Outliers from './pages/Outliers'
import DynamicExplorer from './pages/DynamicExplorer'
import NLQuery from './pages/NLQuery'
import { fetchMeta } from './api'

export const FilterContext = createContext(null)

const DEFAULT_YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
const DEFAULT_CATEGORIES = [
  'Overall',
  'Engineering',
  'Management',
  'University',
  'College',
  'Pharmacy',
  'Medical',
  'Dental',
  'Law',
  'Architecture',
  'Agriculture',
  'Research',
]

function App() {
  const navigate = useNavigate()
  const location = useLocation()

  const [year, setYear] = useState(2024)
  const [category, setCategory] = useState('Overall')
  const [allYears, setAllYears] = useState(DEFAULT_YEARS)
  const [allCategories, setAllCategories] = useState(DEFAULT_CATEGORIES)
  const [allStates, setAllStates] = useState([])
  const [meta, setMeta] = useState(null)
  const [metaLoading, setMetaLoading] = useState(true)
  const [metaError, setMetaError] = useState(null)

  useEffect(() => {
    let isMounted = true
    fetchMeta()
      .then((data) => {
        if (!isMounted || !data) return
        setMeta(data)
        if (Array.isArray(data.years) && data.years.length > 0) {
          setAllYears(data.years)
          setYear(data.years[data.years.length - 1])
        }
        if (Array.isArray(data.categories) && data.categories.length > 0) {
          const sortedCats = data.categories.includes('Overall')
            ? ['Overall', ...data.categories.filter((c) => c !== 'Overall').sort()]
            : [...data.categories].sort()
          setAllCategories(sortedCats)
        }
        if (Array.isArray(data.states)) {
          setAllStates(data.states)
        }
      })
      .catch((err) => {
        console.warn('Could not load metadata from API:', err)
        setMetaError(err?.message || 'Failed to connect to FastAPI backend')
      })
      .finally(() => {
        if (isMounted) setMetaLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  // Derive current active tab from pathname
  const activeTab = location.pathname.replace(/^\//, '') || 'overview'

  const handleNavigate = (id) => {
    navigate(`/${id}`)
  }

  const contextValue = {
    year,
    setYear,
    category,
    setCategory,
    allYears,
    allCategories,
    allStates,
    meta,
    metaLoading,
    metaError,
  }

  return (
    <FilterContext.Provider value={contextValue}>
      <div className="app-shell">
        <Sidebar active={activeTab} onNavigate={handleNavigate} />
        <main className="main-content">
          <header className="topbar">
            <div className="topbar-title">NIRF Analytics Dashboard</div>
            <div className="topbar-badge">
              {meta?.year_range ? `${meta.year_range[0]}–${meta.year_range[1]}` : '2017–2025'}
            </div>
            <div className="topbar-spacer" />

            {/* Global Category Filter */}
            <div className="form-group" style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
              <label className="form-label" style={{ margin: 0 }}>Category</label>
              <select
                className="form-select"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                aria-label="Filter Category"
              >
                {allCategories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </header>

          {metaError && (
            <div className="error-box" style={{ margin: '16px 28px 0' }}>
              <strong>Backend Connection Notice:</strong> Unable to connect to the FastAPI backend at <code>http://localhost:8000</code>. Ensure the server is running with <code>uvicorn api.main:app --reload --port 8000</code>.
            </div>
          )}

          <div className="page-body">
            <Routes>
              <Route path="/" element={<Navigate to="/overview" replace />} />
              <Route path="/overview" element={<Overview />} />
              <Route path="/timeseries" element={<TimeSeries />} />
              <Route path="/geospatial" element={<Geospatial />} />
              <Route path="/univariate" element={<Univariate />} />
              <Route path="/bivariate" element={<Bivariate />} />
              <Route path="/multivariate" element={<Multivariate />} />
              <Route path="/statistics" element={<Statistics />} />
              <Route path="/transitions" element={<Transitions />} />
              <Route path="/outliers" element={<Outliers />} />
              <Route path="/dynamic" element={<DynamicExplorer />} />
              <Route path="/nlquery" element={<NLQuery />} />
              <Route path="*" element={<Navigate to="/overview" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </FilterContext.Provider>
  )
}

export default App
