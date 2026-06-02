/**
 * @param {{ status: 'active'|'idle'|'error'|'ACTIVO'|'IDLE'|'ERROR'|'MUERTO'|'REPLICADO' }} props
 */
export default function StatusBadge({ status }) {
  const normalizedStatus = status?.toLowerCase() || 'idle';
  
  const variants = {
    active: 'badge-active',
    activo: 'badge-active',
    idle: 'badge-idle',
    error: 'badge-error',
    muerto: 'badge-error',
    replicado: 'badge-active',
  };

  const labels = {
    active: 'Active',
    activo: 'Active',
    idle: 'Idle',
    error: 'Error',
    muerto: 'Dead',
    replicado: 'Replicated',
  };

  const className = variants[normalizedStatus] || 'badge-idle';
  const label = labels[normalizedStatus] || status;

  return <span className={className}>{label}</span>;
}
