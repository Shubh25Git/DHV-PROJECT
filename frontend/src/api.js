/**
 * api.js — Centralised API client for the NIRF Analytics FastAPI backend.
 * All components import their data-fetching functions from here.
 */

import axios from 'axios';

const BASE = 'http://localhost:8000';

const client = axios.create({ baseURL: BASE, timeout: 30000 });

// ── Meta ─────────────────────────────────────────────────────
export const fetchMeta = () => client.get('/api/meta').then(r => r.data);

// ── Overview ─────────────────────────────────────────────────
export const fetchTopInstitutions = (year, category, limit = 10) =>
  client.get('/api/top-institutions', { params: { year, category, limit } }).then(r => r.data);

export const fetchInstitutions = (category) =>
  client.get('/api/institutions', { params: { category } }).then(r => r.data.institutions);

// ── Time-Series ───────────────────────────────────────────────
export const fetchInstitutionTrend = (name, category) =>
  client.get('/api/trend/institution', { params: { name, category } }).then(r => r.data);

export const fetchAverageScoreTrend = (category) =>
  client.get('/api/trend/average-score', { params: { category } }).then(r => r.data);

export const fetchImprovements = (category, start_year, end_year, limit = 10) =>
  client.get('/api/trend/improvements', { params: { category, start_year, end_year, limit } }).then(r => r.data);

export const fetchDeclines = (category, start_year, end_year, limit = 10) =>
  client.get('/api/trend/declines', { params: { category, start_year, end_year, limit } }).then(r => r.data);

export const fetchConsistentTop = (category, top_n = 10, min_years = 5) =>
  client.get('/api/trend/consistent-top', { params: { category, top_n, min_years } }).then(r => r.data);

// ── Geospatial ────────────────────────────────────────────────
export const fetchTopStates = (year, category, top_n = 100, limit = 15) =>
  client.get('/api/geo/top-states', { params: { year, category, top_n, limit } }).then(r => r.data);

export const fetchGeoDistributionTrend = (category, top_n = 100) =>
  client.get('/api/geo/distribution-trend', { params: { category, top_n } }).then(r => r.data);

export const fetchStateGrowth = (category, start_year, end_year) =>
  client.get('/api/geo/state-growth', { params: { category, start_year, end_year } }).then(r => r.data);

export const fetchCompareStates = (state1, state2, category, year) =>
  client.get('/api/geo/compare-states', { params: { state1, state2, category, year } }).then(r => r.data);

export const fetchNewlyAppearing = (category, base_year, recent_year) =>
  client.get('/api/geo/newly-appearing', { params: { category, base_year, recent_year } }).then(r => r.data);

// ── Univariate ────────────────────────────────────────────────
export const fetchScoreDistribution = (year, category) =>
  client.get('/api/univariate/score-distribution', { params: { year, category } }).then(r => r.data);

export const fetchRankDistribution = (year, category) =>
  client.get('/api/univariate/rank-distribution', { params: { year, category } }).then(r => r.data);

export const fetchSummaryStats = (year, category) =>
  client.get('/api/univariate/summary-stats', { params: { year, category } }).then(r => r.data);

export const fetchQuartiles = (year, category) =>
  client.get('/api/univariate/quartiles', { params: { year, category } }).then(r => r.data);

export const fetchSpreadByCategory = (year) =>
  client.get('/api/univariate/spread-by-category', { params: { year } }).then(r => r.data);

// ── Bivariate ─────────────────────────────────────────────────
export const fetchRpcVsScore = (year, category) =>
  client.get('/api/bivariate/rpc-vs-score', { params: { year, category } }).then(r => r.data);

export const fetchPerceptionVsScore = (year, category) =>
  client.get('/api/bivariate/perception-vs-score', { params: { year, category } }).then(r => r.data);

export const fetchAllParamsCorr = (year, category) =>
  client.get('/api/bivariate/all-parameters', { params: { year, category } }).then(r => r.data);

export const fetchTlrVsRpc = (year, category) =>
  client.get('/api/bivariate/tlr-vs-rpc', { params: { year, category } }).then(r => r.data);

export const fetchTwoVariable = (v1, v2, year, category) =>
  client.get('/api/bivariate/two-variable', { params: { v1, v2, year, category } }).then(r => r.data);

export const fetchCorrTrend = (param1, param2, category) =>
  client.get('/api/bivariate/correlation-trend', { params: { param1, param2, category } }).then(r => r.data);

export const fetchDynamicData = (filters) =>
  client.post('/api/dynamic/filter', filters).then(r => r.data);

// ── Multivariate ──────────────────────────────────────────────
export const fetchTopProfiles = (year, category, top_n = 5) =>
  client.get('/api/multivariate/top-profiles', { params: { year, category, top_n } }).then(r => r.data);

export const fetchHighResearchLowTeaching = (year, category) =>
  client.get('/api/multivariate/high-research-low-teaching', { params: { year, category } }).then(r => r.data);

export const fetchHighTeachingLowPerception = (year, category, percentile_high = 75, percentile_low = 50) =>
  client.get('/api/multivariate/high-teaching-low-perception', { params: { year, category, percentile_high, percentile_low } }).then(r => r.data);

export const fetchImprovedScoreDecliningParams = (category, start_year, end_year) =>
  client.get('/api/multivariate/improved-score-declining-params', { params: { category, start_year, end_year } }).then(r => r.data);

export const fetchStrongestWeakestGap = (year, category) =>
  client.get('/api/multivariate/strongest-weakest-gap', { params: { year, category } }).then(r => r.data);

// ── Statistics ────────────────────────────────────────────────
export const fetchTop10VsRest = (year, category) =>
  client.get('/api/stats/top10-vs-rest', { params: { year, category } }).then(r => r.data);

export const fetchDispersion = (category) =>
  client.get('/api/stats/dispersion', { params: { category } }).then(r => r.data);

export const fetchParamVariability = (year, category) =>
  client.get('/api/stats/parameter-variability', { params: { year, category } }).then(r => r.data);

export const fetchMedianIqrTrend = (category) =>
  client.get('/api/stats/median-iqr-trend', { params: { category } }).then(r => r.data);

export const fetchStateScoreDistribution = (year, category, min_institutions = 3) =>
  client.get('/api/stats/state-score-distribution', { params: { year, category, min_institutions } }).then(r => r.data);

// ── Transitions ───────────────────────────────────────────────
export const fetchBandToTop50 = (category, year1, year2) =>
  client.get('/api/transitions/band-to-top50', { params: { category, year1, year2 } }).then(r => r.data);

export const fetchTop10EntriesExits = (category, year1, year2) =>
  client.get('/api/transitions/top10-entries-exits', { params: { category, year1, year2 } }).then(r => r.data);

export const fetchBandRetention = (category, year1, year2) =>
  client.get('/api/transitions/band-retention', { params: { category, year1, year2 } }).then(r => r.data);

export const fetchLargestShifts = (category, year1, year2) =>
  client.get('/api/transitions/largest-shifts', { params: { category, year1, year2 } }).then(r => r.data);

export const fetchMobilitySummary = (category, year1, year2) =>
  client.get('/api/transitions/mobility-summary', { params: { category, year1, year2 } }).then(r => r.data);

// ── Outliers ──────────────────────────────────────────────────
export const fetchResearchOutliers = (year, category) =>
  client.get('/api/outliers/research-outliers', { params: { year, category } }).then(r => r.data);

export const fetchResearchTeachingGap = (year, category, limit = 15) =>
  client.get('/api/outliers/research-teaching-gap', { params: { year, category, limit } }).then(r => r.data);

export const fetchRankVolatility = (category, min_years = 4) =>
  client.get('/api/outliers/rank-volatility', { params: { category, min_years } }).then(r => r.data);

export const fetchScoreChangeOutliers = (category, year1, year2) =>
  client.get('/api/outliers/score-change', { params: { category, year1, year2 } }).then(r => r.data);

export const fetchStrongParamPoorRank = (year, category, param = 'rpc', param_percentile = 75, rank_min = 50) =>
  client.get('/api/outliers/strong-param-poor-rank', { params: { year, category, param, param_percentile, rank_min } }).then(r => r.data);

// ── Natural Language Query ────────────────────────────────────
export const postNLQuery = (question, category = null, year = null) =>
  client.post('/api/query/natural-language', { question, category, year }).then(r => r.data);
