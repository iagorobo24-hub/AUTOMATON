/**
 * App Mode Hook - Manages simulation vs normal mode
 * Uses localStorage for persistence and custom event for cross-tab sync
 */
import { useState, useEffect, useCallback } from "react";

const MODE_KEY = "automaton_mode";
const EVENT_NAME = "automaton_mode_change";

const validModes = ["normal", "simulation"];

export function useAppMode() {
  const [mode, setModeState] = useState(() => {
    try {
      const stored = localStorage.getItem(MODE_KEY);
      return validModes.includes(stored) ? stored : "normal";
    } catch {
      return "normal";
    }
  });

  const setMode = useCallback((newMode) => {
    if (!validModes.includes(newMode)) return;
    localStorage.setItem(MODE_KEY, newMode);
    setModeState(newMode);
    // Notify other tabs/components
    window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: newMode }));
  }, []);

  const toggleMode = useCallback(() => {
    setMode(mode === "normal" ? "simulation" : "normal");
  }, [mode, setMode]);

  // Listen for mode changes from other components/tabs
  useEffect(() => {
    const handler = (e) => {
      if (validModes.includes(e.detail)) {
        setModeState(e.detail);
      }
    };
    window.addEventListener(EVENT_NAME, handler);
    return () => window.removeEventListener(EVENT_NAME, handler);
  }, []);

  return { mode, setMode, toggleMode, isSimulation: mode === "simulation", isNormal: mode === "normal" };
}
