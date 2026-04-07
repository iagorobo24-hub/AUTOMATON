/**
 * App Mode Hook - Manages Real vs Test mode
 * Backend is the source of truth for mode.
 * All API calls are automatically filtered by current mode.
 */
import { useState, useEffect, useCallback } from "react";

const MODE_KEY = "automaton_mode";
const EVENT_NAME = "automaton_mode_change";
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8002/api";

export function useAppMode() {
  const [mode, setModeState] = useState(() => {
    const stored = localStorage.getItem(MODE_KEY);
    return stored === "real" ? "real" : "test";
  });
  const [synced, setSynced] = useState(false);

  const syncMode = useCallback(async (newMode) => {
    if (!["real", "test"].includes(newMode)) return;
    try {
      const resp = await fetch(`${API_BASE}/system/mode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: newMode }),
      });
      const data = await resp.json();
      if (data.success) {
        localStorage.setItem(MODE_KEY, newMode);
        setModeState(newMode);
        window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: newMode }));
      }
    } catch (e) {
      console.error("Failed to sync mode with backend:", e);
    }
  }, []);

  const toggleMode = useCallback(() => {
    syncMode(mode === "real" ? "test" : "real");
  }, [mode, syncMode]);

  // Listen for mode changes from other tabs
  useEffect(() => {
    const handler = (e) => {
      if (["real", "test"].includes(e.detail)) {
        setModeState(e.detail);
        localStorage.setItem(MODE_KEY, e.detail);
      }
    };
    window.addEventListener(EVENT_NAME, handler);
    return () => window.removeEventListener(EVENT_NAME, handler);
  }, []);

  // Sync with backend on mount
  useEffect(() => {
    fetch(`${API_BASE}/system/mode`)
      .then((r) => r.json())
      .then((data) => {
        if (data.mode && data.mode !== mode) {
          localStorage.setItem(MODE_KEY, data.mode);
          setModeState(data.mode);
        }
        setSynced(true);
      })
      .catch(() => setSynced(true));
  }, []);

  return {
    mode,
    setMode: syncMode,
    toggleMode,
    isReal: mode === "real",
    isTest: mode === "test",
    synced,
  };
}
