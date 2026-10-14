import { Link } from "react-router-dom";
import { Activity, Boxes, Truck } from "lucide-react";

export default function Overview({ summary }) {
  return (
    <>
      <section className="welcome">
        <div>
          <span className="eyebrow">SUPPLY CHAIN INTELLIGENCE</span>
          <h2>Understand every delivery.</h2>
          <p>
            Explore historical delivery performance and available
            shipment locations from your DataCo dataset.
          </p>
          <Link className="primary-button welcome-button" to="/tracking">
            <Truck size={17} /> Explore shipments
          </Link>
        </div>
        <div className="welcome-icon"><Activity size={40} /></div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">Total orders <Boxes size={18} /></div>
          <div className="stat-value">{summary?.total_orders ?? "—"}</div>
          <p>Orders in the DataCo dataset</p>
        </div>
        <div className="stat-card">
          <div className="stat-top">On-time deliveries <Truck size={18} /></div>
          <div className="stat-value">{summary?.on_time_count ?? "—"}</div>
          <p>Historical delivery_status = On Time</p>
        </div>
        <div className="stat-card">
          <div className="stat-top">Late-risk orders <Activity size={18} /></div>
          <div className="stat-value">{summary?.late_risk_count ?? "—"}</div>
          <p>Historical late_delivery_risk = 1</p>
        </div>
      </section>

      <section className="panel">
        <span className="eyebrow">DATA SOURCE</span>
        <h2>DataCo Supply Chain</h2>
        <p className="muted">
          The map shows available origin and destination coordinates.
          It does not show a vehicle's current GPS position.
        </p>
        <Link className="secondary-button" to="/tracking">
          Open shipment tracking →
        </Link>
      </section>
    </>
  );
}
