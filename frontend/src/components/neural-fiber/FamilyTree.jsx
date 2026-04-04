import React from 'react';
import { GitBranch, User, Skull } from 'lucide-react';

const Node = ({ node }) => {
  return (
    <div className="tree-node">
      <div className={`node-content ${node.status}`}>
        <div className="node-icon">
          {node.status === 'dead' ? <Skull size={14} /> : <User size={14} />}
        </div>
        <div className="node-info">
          <span className="node-name">{node.name}</span>
          <span className="node-roi">{node.roi.toFixed(1)}% ROI</span>
        </div>
      </div>
      
      {node.children && node.children.length > 0 && (
        <div className="node-children">
          {node.children.map(child => (
            <Node key={child.agent_id} node={child} />
          ))}
        </div>
      )}
    </div>
  );
};

export default function FamilyTree({ lineage }) {
  if (!lineage || !lineage.tree) {
    return (
      <div className="family-tree-empty">
        <GitBranch className="mb-2 opacity-20" size={32} />
        <span>Select an agent to view lineage</span>
      </div>
    );
  }

  return (
    <div className="family-tree-container">
      <Node node={lineage.tree} />
    </div>
  );
}
