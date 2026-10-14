
import { useState } from "react";
import { predictDeliveryRisk } from "../services/api";

const fields = [
  ["days_for_shipment_scheduled", "Scheduled shipping days", "number"],
  ["shipping_mode", "Shipping mode", "text"],
  ["customer_segment", "Customer segment", "text"],
  ["market", "Market", "text"],
  ["order_region", "Order region", "text"],
  ["order_country", "Order country", "text"],
  ["category_name", "Category name", "text"],
  ["department_name", "Department name", "text"],
  ["order_item_quantity", "Item quantity", "number"],
  ["sales", "Sales", "number"],
  ["order_item_discount", "Discount", "number"],
  ["order_item_profit_ratio", "Profit ratio", "number"],
  ["product_price", "Product price", "number"],
  ["order_month", "Order month (1–12)", "number"],
  ["order_day_of_week", "Day of week (0–6)", "number"],
  ["order_quarter", "Order quarter (1–4)", "number"],
];

const initialValues = {
  days_for_shipment_scheduled: 2,
  shipping_mode: "Standard Class",
  customer_segment: "Consumer",
  market: "Europe",
  order_region: "Western Europe",
  order_country: "France",
  category_name: "Cleats",
  department_name: "Footwear",
  order_item_quantity: 1,
  sales: 100,
  order_item_discount: 0,
  order_item_profit_ratio: 0.1,
  product_price: 100,
  order_month: 10,
  order_day_of_week: 1,
  order_quarter: 4,
};

const numericFields = new Set(
  fields.filter(([, , type]) => type === "number").map(([key]) => key)
);

export default function PredictionForm({ onResult }) {
  const [values, setValues] = useState(initialValues);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    const { name, value } = event.target;

    setValues((previous) => ({
      ...previous,
      [name]: numericFields.has(name) && value !== ""
        ? Number(value)
        : value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    onResult(null);

    try {
      const result = await predictDeliveryRisk(values);
      onResult(result);
    } catch (err) {
      setError(err.message || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="panel prediction-form" onSubmit={handleSubmit}>
      <div className="panel-heading">
        <div>
          <span className="eyebrow">MACHINE LEARNING</span>
          <h2>Delivery risk prediction</h2>
          <p>Enter the order characteristics to run a prediction.</p>
        </div>
        <span className="model-tag">Random Forest</span>
      </div>

      <div className="form-grid">
        {fields.map(([name, label, type]) => (
          <label className="field" key={name}>
            <span>{label}</span>
            <input
              name={name}
              type={type}
              step={type === "number" ? "any" : undefined}
              min={
                ["order_month", "order_quarter"].includes(name) ? 1 :
                name === "order_day_of_week" ? 0 :
                ["sales", "product_price", "order_item_quantity",
                 "order_item_discount"].includes(name) ? 0 :
                undefined
              }
              max={
                name === "order_month" ? 12 :
                name === "order_quarter" ? 4 :
                name === "order_day_of_week" ? 6 :
                undefined
              }
              value={values[name]}
              onChange={updateField}
              required
            />
          </label>
        ))}
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      <button className="primary-button" type="submit" disabled={loading}>
        {loading ? "Analyzing order..." : "Predict delivery risk"}
      </button>

      <p className="form-note">
        Demo inputs only. Verify the expected categories and feature encoding
        against the training dataset before interpreting predictions.
      </p>
    </form>
  );
}