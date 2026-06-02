/**
 * @param {{ title: string, value: string|number, subtitle?: string, icon: React.ComponentType }} props
 */
export default function StatCard({ title, value, subtitle, icon: Icon }) {
  return (
    <div className="app-card app-card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-[var(--text-secondary)]">{title}</p>
          <p className="mt-1 font-mono text-2xl font-bold text-[var(--accent)]">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-[var(--text-muted)]">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--bg-elevated)]">
            <Icon className="h-5 w-5 text-[var(--text-secondary)]" />
          </div>
        )}
      </div>
    </div>
  );
}
