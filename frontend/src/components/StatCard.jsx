
export default function StatCard({
  icon: Icon,
  label,
  value,
  caption,
}) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        {Icon && (
          <span className="stat-icon">
            <Icon size={19} />
          </span>
        )}
      </div>

      <div className="stat-value">{value}</div>
      <p>{caption}</p>
    </article>
  );
}