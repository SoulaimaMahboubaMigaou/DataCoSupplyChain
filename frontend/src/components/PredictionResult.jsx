
import { AlertTriangle, ShieldCheck } from "lucide-react";

export default function PredictionResult({ result }) {
  if (!result) return null;

  // Support both backend response formats
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

  const riskLabel =
    result.risk_label ??
    (isHighRisk ? "HIGH RISK" : "LOW RISK");

  return (
    <section
      className={`panel result-panel ${
        isHighRisk ? "high-risk" : "low-risk"
      }`}
    >
      <div className="result-symbol">
        {isHighRisk
          ? <AlertTriangle size={27} />
          : <ShieldCheck size={27} />}
      </div>

      <div className="result-content">
        <span className="eyebrow">PREDICTION RESULT</span>
        <h2>{riskLabel}</h2>

        <p>
          Predicted late-delivery risk:{" "}
          <strong>{predictedClass === 1 ? "High" : "Low"}</strong>
        </p>

        {validProbability ? (
          <div className="probability-block">
            <div className="probability-label">
              <span>Estimated probability of late delivery</span>
              <strong>
                {(probability * 100).toFixed(1)}%
              </strong>
            </div>

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
                style={{
                  width: `${probability * 100}%`,
                }}
              />
            </div>
          </div>
        ) : (
          <p className="muted">
            Probability is not available from the model response.
          </p>
        )}

        {result.prediction_id && (
          <p className="result-id">
            Prediction ID: {result.prediction_id}
          </p>
        )}

        <p className="muted">
          This is a model estimate, not confirmation of actual delivery status.
        </p>
      </div>
    </section>
  );
}
