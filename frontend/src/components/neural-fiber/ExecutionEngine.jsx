import React from 'react';
import { TrendingUp, TrendingDown, Pause, AlertTriangle } from 'lucide-react';

export default function ExecutionEngine({ agents }) {
  const activeAgents = agents?.filter(a => a.status === 'active') || [];
  const replicatingAgents = agents?.filter(a => a.status === 'replicating') || [];
  const dyingAgents = agents?.filter(a => a.status === 'dying') || [];
  
  const totalExposure = agents?.reduce((sum, agent) => {
    return sum + (agent.finances?.current_balance || 0);
  }, 0) || 0;
  
  const maxExposure = 1000000; // 1M max exposure
  const exposurePercent = Math.min((totalExposure / maxExposure) * 100, 100);

  const AgentCard = ({ agent, statusColor, statusText }) => {
    const roi = agent.performance?.roi_percent || 0;
    const balance = agent.finances?.current_balance || 0;
    
    return (
      <div className={`asset-card ${agent.status}`}>
        <div className="card-header">
          <span className="agent-name">{agent.name || `Agent-${agent.id?.slice(0, 8)}`}</span>
          <span className="agent-status" style={{ color: statusColor }}>
            {statusText}
          </span>
        </div>
        <div className="agent-details">
          Size: {balance.toFixed(2)}€<br />
          ROE: {roi >= 0 ? '+' : ''}{roi.toFixed(2)}%
        </div>
      </div>
    );
  };

  return (
    <div className="execution-engine">
      <span className="label">Execution Engine</span>
      
      <div className="agents-list">
        {activeAgents.map(agent => (
          <AgentCard 
            key={agent.id} 
            agent={agent} 
            statusColor="#00ff88" 
            statusText="ACTIVE"
          />
        ))}
        
        {replicatingAgents.map(agent => (
          <AgentCard 
            key={agent.id} 
            agent={agent} 
            statusColor="#00f2ff" 
            statusText="REPLICATING"
          />
        ))}
        
        {dyingAgents.map(agent => (
          <AgentCard 
            key={agent.id} 
            agent={agent} 
            statusColor="#ff004c" 
            statusText="DYING"
          />
        ))}
      </div>

      <div className="filament-container">
        <div className="data-thread"></div>
        <div className="data-thread" style={{ animationDelay: '1.5s' }}></div>
        <div className="risk-content">
          <span className="label">Risk Filament</span>
          <div className="risk-bar">
            <div 
              className="risk-fill" 
              style={{ width: `${exposurePercent}%` }}
            ></div>
          </div>
          <span className="risk-text">
            {exposurePercent.toFixed(0)}% Exposure Limit
          </span>
        </div>
      </div>
      
      <button className="button-filament">Emergency Liquidation</button>
    </div>
  );
}
