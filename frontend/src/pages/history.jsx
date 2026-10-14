import { useState } from "react";
import { AlertTriangle, ShieldCheck } from "lucide-react";
import { HISTORY_KEY } from "./prediction";

function load() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleString();
}

export default function History() {
  const [items, setItems] = useState(load);

  function clear() {
    localStorage.removeItem(HISTORY_KEY);
    setItems([]);
  }

  return (
    <section className="panel">
      <span className="eyebrow">PREDICTIONS</span>
      <h2>History ({items.length})</h2>

      {items.length === 0 ? (
        <p className="muted">No predictions yet. Run one from the Prediction page.</p>
      ) : (
        <>
          <div className="table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Risk</th>
                  <th>Probability</th>
                  <th>Prediction ID</th>
                </tr>
              </thead>
              <tbody>
                {items.map((entry, index) => {
                  const result = entry.result || {};

                  const predictedClass = Number(
                    result.late_delivery_risk ??
                    result.predicted_late_delivery_risk
                  );
                  const isHighRisk = predictedClass === 1;

                  const probability = result.risk_probability;
                  const validProbability =
                    typeof probability === "number" &&
                    Number.isFinite(probability) &&
                    probability >= 0 &&
                    probability <= 1;

                  const id = result.prediction_id;

                  return (
                    <tr key={id || index}>
                      <td className="history-date">
                        {formatDate(entry.date || result.created_at)}
                      </td>

                      <td>
                        <span
                          className={`risk-badge ${
                            isHighRisk ? "risk-high" : "risk-low"
                          }`}
                        >
                          {isHighRisk
                            ? <AlertTriangle size={13} />
                            : <ShieldCheck size={13} />}
                          {isHighRisk ? "High risk" : "Low risk"}
                        </span>
                      </td>

                      <td>
                        {validProbability ? (
                          <div className="history-probability">
                            <strong>{(probability * 100).toFixed(1)}%</strong>
                            <div
                              className="progress-track"
                              role="progressbar"
                              aria-label="Estimated probability of late delivery"
                              aria-valuenow={probability * 100}
                              aria-valuemin={0}
                              aria-valuemax={100}
                            >
                              <div
                                className="progress-value"
                                style={{ width: `${probability * 100}%` }}
                              />
                            </div>
                          </div>
                        ) : (
                          <span className="muted">n/a</span>
                        )}
                      </td>

                      <td
                        className="history-id"
                        title={id || ""}
                      >
                        {id ? `${id.slice(0, 8)}…` : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <button className="secondary-button" onClick={clear}>Clear history</button>
        </>
      )}
    </section>
  );
}
