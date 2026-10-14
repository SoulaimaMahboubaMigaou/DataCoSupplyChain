
export default function StatusBadge({ status }) {
  const healthy = status === "ok" || status === "connected";

  return (
    <span className={`status-badge ${healthy ? "healthy" : "offline"}`}>
      <span className="badge-dot" />
      {healthy ? "Operational" : "Unavailable"}
    </span>
  );
}