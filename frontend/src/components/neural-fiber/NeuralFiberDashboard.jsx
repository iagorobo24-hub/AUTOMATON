import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import CentralDisplay from './CentralDisplay';
import ExecutionEngine from './ExecutionEngine';
import StructuralAnalysis from './StructuralAnalysis';
import ActivityConsole from './ActivityConsole';
import '../../styles/neural-fiber.css';

const API = "http://localhost:8001/api";

export default function NeuralFiberDashboard() {
  const [stats, setStats] = useState(null);
  const [agents, setAgents] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [lineage, setLineage] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, agentsRes, notifRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/notifications?limit=10`)
      ]);
      
      const agentsData = agentsRes.data.agents || [];
      setStats(statsRes.data);
      setAgents(agentsData);
      setNotifications(notifRes.data.notifications || []);

      // Fetch lineage for the first agent if available
      if (agentsData.length > 0 && !lineage) {
        const linRes = await axios.get(`${API}/agents/${agentsData[0].id}/lineage`);
        setLineage(linRes.data);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    }
  }, [lineage]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="neural-fiber-dashboard">
      <div className="weave-overlay"></div>
      
      <header className="fiber-header">
        <div className="agent-status">
          <div className="status-orb"></div>
          <h1 className="app-title">
            AUTOMATON <span className="version">// NEXUS-9</span>
          </h1>
        </div>
        
        <div className="header-metrics">
          <div className="metric">
            <span className="label">Portfolio Value</span>
            <span className="metric-value">
              €{(stats?.finances?.total_balance || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </span>
          </div>
          
          <div className="metric">
            <span className="label">24H Efficiency</span>
            <span className={`metric-value ${(stats?.trading?.pnl_24h || 0) >= 0 ? 'positive' : 'negative'}`}>
              {(stats?.trading?.pnl_24h || 0) >= 0 ? '+' : ''}{((stats?.trading?.pnl_24h || 0) / (stats?.finances?.total_balance || 1) * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </header>

      <aside className="fiber-sidebar-left">
        <ExecutionEngine agents={agents} />
      </aside>

      <main className="fiber-main">
        <CentralDisplay stats={stats} agents={agents} />
      </main>

      <aside className="fiber-sidebar-right">
        <StructuralAnalysis stats={stats} agents={agents} />
      </aside>

      <footer className="fiber-console">
        <ActivityConsole notifications={notifications} />
      </footer>
    </div>
  );
}
