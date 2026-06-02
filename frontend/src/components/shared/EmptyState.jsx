/**
 * @param {{ icon: React.ComponentType, title: string, subtitle?: string }} props
 */
export default function EmptyState({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {Icon && <Icon className="h-12 w-12 text-[var(--text-muted)] mb-4" />}
      <h3 className="text-lg font-medium text-[var(--text-primary)]">{title}</h3>
      {subtitle && (
        <p className="mt-1 text-sm text-[var(--text-muted)]">{subtitle}</p>
      )}
    </div>
  );
}
