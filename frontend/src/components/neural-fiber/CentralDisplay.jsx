import React from 'react';
import { TrendingUp, Bot } from 'lucide-react';

export default function CentralDisplay({ stats, agents }) {
  const portfolioValue = stats?.finances?.total_balance || 0;
  const efficiency24h = stats?.trading?.pnl_24h || 0;
  const activeAgents = agents?.filter(a => a.status === 'active').length || 0;
  
  // Find best performing agent
  const bestAgent = agents?.reduce((best, agent) => {
    const agentRoi = agent.performance?.roi_percent || 0;
    const bestRoi = best?.performance?.roi_percent || 0;
    return agentRoi > bestRoi ? agent : best;
  }, null);

  return (
    <div className="nexus-core">
      <div className="ring ring-1"></div>
      <div className="ring ring-2"></div>
      <div className="ring ring-3"></div>
      
      <div className="nexus-data">
        <span className="label">Portfolio Aggregate</span>
        <span className="big-price">
          €{portfolioValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
        
        {bestAgent && (
          <span className="agent-value">
            <Bot className="w-4 h-4 inline mr-2" />
            Best: €{(bestAgent.finances?.current_balance || 0).toLocaleString()}
          </span>
        )}
        
        <span className="system-status">
          SYSTEM ACTIVE: {activeAgents} AGENTS OPERATING
        </span>
      </div>
    </div>
  );
}
