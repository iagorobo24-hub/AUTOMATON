import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Pause, AlertTriangle, Loader2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API = "http://localhost:8001/api";

export default function ExecutionEngine({ agents }) {
  const [isLiquidating, setIsLiquidating] = useState(false);
  
  const handleEmergencyStop = async () => {
    if (!window.confirm("CRITICAL ACTION: Terminate all active agents and liquidate positions?")) {
      return;
    }
    
    setIsLiquidating(true);
    try {
      const response = await axios.post(`${API}/agents/emergency-stop?confirm=true`);
      if (response.data.success) {
        toast.error("EMERGENCY STOP EXECUTED", {
          description: `${response.data.terminated_count} agents terminated immediately.`,
          duration: 10000,
        });
      }
    } catch (error) {
      console.error("Emergency stop failed:", error);
      toast.error("COMMAND FAILED", {
        description: "Could not execute emergency protocol."
      });
    } finally {
      setIsLiquidating(false);
    }
  };

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
      
      <button 
        className="button-filament" 
        onClick={handleEmergencyStop}
        disabled={isLiquidating}
      >
        {isLiquidating ? (
          <><Loader2 className="animate-spin mr-2" size={16} /> PROCESSING...</>
        ) : (
          "Emergency Liquidation"
        )}
      </button>
    </div>
  );
}
