import React, { useEffect, useRef } from 'react';
import { Bot, TrendingUp, AlertTriangle, Zap } from 'lucide-react';

export default function ActivityConsole({ notifications }) {
  const consoleRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom when new notifications arrive
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [notifications]);

  const getLogIcon = (type) => {
    switch (type) {
      case 'agent_created': return <Bot className="w-3 h-3" />;
      case 'trade_executed': return <TrendingUp className="w-3 h-3" />;
      case 'agent_dying': return <AlertTriangle className="w-3 h-3" />;
      case 'system_alert': return <Zap className="w-3 h-3" />;
      default: return null;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'agent_created': return '#00ff88';
      case 'trade_executed': return '#00f2ff';
      case 'agent_dying': return '#ff004c';
      case 'system_alert': return '#f59e0b';
      default: return '#e0e0e0';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return `[${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}]`;
  };

  return (
    <div className="activity-console">
      <div className="console-output" ref={consoleRef}>
        {notifications?.map((notif, index) => (
          <div key={notif.id || index} className="log-entry">
            <span className="timestamp">{formatTimestamp(notif.created_at)}</span>
            <span 
              className="action"
              style={{ color: getLogColor(notif.type) }}
            >
              {getLogIcon(notif.type)}
              <span style={{ marginLeft: '8px' }}>
                {notif.message}
              </span>
            </span>
          </div>
        )).slice(-10).reverse()}
        
        {/* Default welcome message */}
        {(!notifications || notifications.length === 0) && (
          <div className="log-entry">
            <span className="timestamp">[00:00:00]</span>
            <span className="action">
              Neural engine initialized. AUTOMATON system online.
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
