import React from 'react';
import { BarChart3, Brain, Activity, GitBranch } from 'lucide-react';
import FamilyTree from './FamilyTree';

export default function StructuralAnalysis({ stats, agents }) {
  const totalAgents = agents?.length || 0;
  const activeAgents = agents?.filter(a => a.status === 'active').length || 0;
  const successRate = stats?.trading?.win_rate || 0;
  const avgRoi = stats?.finances?.avg_roi || 0;

  // Build lineage from agents with parent_id
  const lineage = agents?.filter(a => a.parent_id) || [];

  const agentDistribution = {
    active: agents?.filter(a => a.status === 'active').length || 0,
    replicating: agents?.filter(a => a.status === 'replicating').length || 0,
    dying: agents?.filter(a => a.status === 'dying').length || 0,
    paused: agents?.filter(a => a.status === 'paused').length || 0,
  };

  const maxCount = Math.max(...Object.values(agentDistribution));

  return (
    <div className="structural-analysis">
      <span className="label">Structural Analysis</span>
      
      {/* Agent Distribution */}
      <div className="analysis-section">
        <div className="section-header">
          <span>Agent Distribution</span>
          <span>{totalAgents} Total</span>
        </div>
        {Object.entries(agentDistribution).map(([status, count]) => (
          <div key={status} className="metric-bar">
            <span className="metric-label">{status.toUpperCase()}</span>
            <div className="bar-container">
              <div 
                className="bar-fill" 
                style={{ width: `${(count / maxCount) * 100}%` }}
              ></div>
            </div>
            <span className="metric-value">{count}</span>
          </div>
        ))}
      </div>

      {/* Performance Metrics */}
      <div className="analysis-section">
        <span className="label">Performance Metrics</span>
        <div className="metrics-grid">
          <div className="metric-card">
            <span className="mini-label">Success Rate</span>
            <div className="metric-number">
              {(successRate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="metric-card">
            <span className="mini-label">Avg ROI</span>
            <div className="metric-number">
              {avgRoi >= 0 ? '+' : ''}{avgRoi.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>

      {/* Neural Weights */}
      <div className="analysis-section">
        <span className="label">Neural Weights</span>
        <div className="neural-grid">
          <div className="neural-card">
            <span className="mini-label">Sentiment</span>
            <div className="neural-value">0.89</div>
          </div>
          <div className="neural-card">
            <span className="mini-label">Volatility</span>
            <div className="neural-value">0.12</div>
          </div>
        </div>
      </div>

      {/* Lineage Mapping */}
      <div className="analysis-section">
        <div className="section-header">
          <span className="label">Lineage Mapping</span>
          <GitBranch size={14} className="opacity-50" />
        </div>
        <FamilyTree lineage={lineage} />
      </div>

      {/* Thread Integrity */}
      <div className="analysis-section">
        <span className="label">Thread Integrity</span>
        <svg viewBox="0 0 300 100" className="integrity-chart">
          <polyline 
            points="0,50 20,45 40,55 60,30 80,70 100,50 120,40 140,60 160,20 180,80 200,50 220,55 240,40 260,50 280,45 300,50" 
            stroke="#00f2ff" 
            fill="none" 
            opacity="0.5"
          />
        </svg>
      </div>
    </div>
  );
}
