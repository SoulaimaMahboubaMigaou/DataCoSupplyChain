import { useState } from "react";
import PredictionForm from "../components/PredictionForm";
import PredictionResult from "../components/PredictionResult";

export const HISTORY_KEY = "dataco_prediction_history";

export default function Prediction() {
  const [result, setResult] = useState(null);

  function handleResult(data) {
  setResult(data);

  // Do not save the temporary reset before a prediction
  if (!data) return;

  try {
    const old = JSON.parse(
      localStorage.getItem(HISTORY_KEY) || "[]"
    );

    old.unshift({
      date: new Date().toISOString(),
      result: data,
    });

    localStorage.setItem(
      HISTORY_KEY,
      JSON.stringify(old.slice(0, 100))
    );
  } catch {
    // Local history storage unavailable
  }
}

  return (
    <section className="panel">
      <span className="eyebrow">DELIVERY RISK</span>
      <h2>Predict a delivery</h2>
      <PredictionForm onResult={handleResult} />
      {result && <PredictionResult result={result} />}
    </section>
  );
}