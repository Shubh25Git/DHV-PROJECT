/**
 * useApi.js — Custom React hook for API calls.
 * Provides loading, error, and data states with optional automatic refetch.
 */

import { useState, useEffect, useCallback } from 'react';

/**
 * useApi(fetchFn, deps)
 * @param {Function} fetchFn - async function that returns data
 * @param {Array}    deps    - dependency array (re-fetches when these change)
 */
export function useApi(fetchFn, deps = []) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => { load(); }, [load]);

  return { data, loading, error, refetch: load };
}

/**
 * useLazyApi()
 * Returns a [trigger, state] pair — the fetch only runs when trigger is called.
 */
export function useLazyApi() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const trigger = useCallback(async (fetchFn) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  return [trigger, { data, loading, error }];
}
