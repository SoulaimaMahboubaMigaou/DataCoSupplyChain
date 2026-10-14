import { useEffect, useMemo, useRef, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  Tooltip,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import {apiRequest, getShipments, getShipment,} from "../services/api";


function pinIcon(color) {
  return L.divIcon({
    className: "map-pin",
    html: `
      <svg width="26" height="36" viewBox="0 0 26 36"
           xmlns="http://www.w3.org/2000/svg">
        <path d="M13 0C5.8 0 0 5.8 0 13c0 9.8 13 23 13 23s13-13.2 13-23
                 c0-7.2-5.8-13-13-13z"
              fill="${color}" stroke="#0b1423" stroke-width="1.5" />
        <circle cx="13" cy="13" r="4.5" fill="#0b1423" opacity="0.85" />
      </svg>`,
    iconSize: [26, 36],
    iconAnchor: [13, 36],
    popupAnchor: [0, -32],
  });
}

const originIcon = pinIcon("#38bdf8");
const destinationIcon = pinIcon("#f87171");

// Recentre la carte sur les commandes affichées (ex. après une recherche).
function FitBounds({ points }) {
  const map = useMap();

  useEffect(() => {
    if (points.length === 0) return;

    if (points.length === 1) {
      map.setView(points[0], 6, { animate: true });
      return;
    }

    map.fitBounds(L.latLngBounds(points), {
      padding: [50, 50],
      maxZoom: 7,
    });
  }, [map, points]);

  return null;
}

export default function LiveTracking() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [prediction, setPrediction] = useState(null);
  const [predictionLoading, setPredictionLoading] = useState(false);

  async function predictRisk(id) {
  setPredictionLoading(true);
  setPrediction(null);
  setError("");

  try {
    const result = await apiRequest(
      `/predictions/${encodeURIComponent(id)}`,
      { method: "POST" }
    );
    setPrediction(result);
  } catch (err) {
    setError(err.message);
  } finally {
    setPredictionLoading(false);
  }
}

  // Le chargement du CSV prend ~2 s : sans ce garde, la réponse de la requête
  // initiale peut arriver après celle d'une recherche et écraser ses résultats.
  const requestRef = useRef(0);

  async function loadShipments() {
    const requestId = ++requestRef.current;

    setLoading(true);
    setError("");

    try {
      const data = await getShipments({ search, limit: 100 });
      if (requestId !== requestRef.current) return;
      setItems(data.items || []);
    } catch (err) {
      if (requestId === requestRef.current) setError(err.message);
    } finally {
      if (requestId === requestRef.current) setLoading(false);
    }
  }

  useEffect(() => {
    loadShipments();
  }, []);

  async function openDetails(id) {
    try {
      setSelected(await getShipment(id));
    } catch (err) {
      setError(err.message);
    }
  }

  const mapped = useMemo(
    () => items.filter((item) => item.origin || item.destination),
    [items]
  );

  const withDestination = useMemo(
    () => mapped.filter((item) => item.destination),
    [mapped]
  );

  const bounds = useMemo(
    () =>
      mapped.flatMap((item) =>
        [item.origin, item.destination]
          .filter(Boolean)
          .map((point) => [point.lat, point.lon])
      ),
    [mapped]
  );

  return (
    <section className="tracking-page">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">HISTORICAL SHIPMENT DATA</span>
          
          <p>Positions affichées à partir des coordonnées disponibles dans DataCo.</p>
        </div>
        <button className="secondary-button" onClick={loadShipments}>
          Actualiser
        </button>
      </div>

      <form
        className="search-row"
        onSubmit={(e) => {
          e.preventDefault();
          loadShipments();
        }}
      >
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher par numéro de commande..."
        />
        <button className="secondary-button">Rechercher</button>
      </form>

      {error && <p className="error-message">{error}</p>}

      <div className="tracking-map">
        <MapContainer
          center={[20, 0]}
          zoom={2}
          scrollWheelZoom
          style={{ height: "100%", minHeight: "380px", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <FitBounds points={bounds} />

          {mapped.map((item) => {
            const stops = [
              item.origin && {
                kind: "origin",
                label: "Départ (client)",
                icon: originIcon,
                position: [item.origin.lat, item.origin.lon],
                place: [item.customer_city, item.customer_country]
                  .filter(Boolean).join(", "),
              },
              item.destination && {
                kind: "destination",
                label: "Destination",
                icon: destinationIcon,
                position: [item.destination.lat, item.destination.lon],
                place: [item.destination_city, item.destination_country]
                  .filter(Boolean).join(", "),
              },
            ].filter(Boolean);

            return (
              <span key={item.tracking_id}>
                {stops.map((stop) => (
                  <Marker
                    key={`${item.tracking_id}-${stop.kind}`}
                    position={stop.position}
                    icon={stop.icon}
                    zIndexOffset={stop.kind === "destination" ? 500 : 0}
                  >
                    <Tooltip direction="top" offset={[0, -34]}>
                      {stop.label} · {stop.place || "Lieu inconnu"}
                    </Tooltip>
                    <Popup>
                      <strong>Commande #{item.tracking_id}</strong>
                      <br />
                      {stop.label} : {stop.place || "Lieu inconnu"}
                      <br />
                      Statut : {item.status}
                      {stop.kind === "destination" &&
                        item.destination_source === "geocoded" && (
                          <>
                            <br />
                            <em>Position approximative (ville géocodée)</em>
                          </>
                        )}
                      <br />
                      <button onClick={() => openDetails(item.tracking_id)}>
                        Voir les détails
                      </button>
                    </Popup>
                  </Marker>
                ))}
                {stops.length === 2 && (
                  <Polyline
                    positions={stops.map((stop) => stop.position)}
                    pathOptions={{ color: "#3b82f6", dashArray: "7 8" }}
                  />
                )}
              </span>
            );
          })}
        </MapContainer>
      </div>

      <div className="map-legend">
        <span><i className="legend-dot origin" /> Départ (client)</span>
        <span><i className="legend-dot destination" /> Destination</span>
      </div>

      <p className="form-note">
        {mapped.length} commandes localisées sur {items.length},
        dont {withDestination.length} avec une destination.
        Les destinations sont déduites de la ville de commande : ce n'est pas
        une localisation GPS en direct.
      </p>

      <section className="panel">
        <h2>Commandes</h2>
        {loading ? (
          <p className="muted">Chargement...</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Tracking ID</th>
                  <th>Destination</th>
                  <th>Mode</th>
                  <th>Statut</th>
                  <th>Détails</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.tracking_id}>
                    <td>{item.tracking_id}</td>
                    <td>
                      {[item.destination_city, item.destination_country]
                        .filter(Boolean).join(", ") || "Non disponible"}
                    </td>
                    <td>{item.shipping_mode || "—"}</td>
                    <td>{item.status}</td>
                    <td>
                      <button
                        className="text-button"
                        onClick={() => openDetails(item.tracking_id)}
                      >
                        Voir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selected && (
        <section className="panel">
          <div className="panel-heading">
            <h2>Commande #{selected.tracking_id}</h2>
            <button
              className="secondary-button"
              onClick={() => setSelected(null)}
            >
              Fermer
            </button>
          </div>

          <div className="model-details">
            <div><span>Statut historique</span><strong>{selected.status}</strong></div>
            <div><span>Risque de retard</span><strong>{String(selected.late_delivery_risk ?? "Non disponible")}</strong></div>
            <div><span>Mode d'expédition</span><strong>{selected.shipping_mode || "—"}</strong></div>
            <div><span>Date de commande</span><strong>{selected.order_date || "—"}</strong></div>
            <div><span>Date d'expédition</span><strong>{selected.shipping_date || "—"}</strong></div>
            <div><span>Jours de transport réels (dataset)</span><strong>{selected.real_days ?? "—"}</strong></div>
          </div>
          <button
  className="primary-button"
  onClick={() => predictRisk(selected.tracking_id)}
  disabled={predictionLoading}
>
  {predictionLoading ? "Prediction..." : "Predict delivery risk"}
</button>

{prediction && prediction.tracking_id === selected.tracking_id && (
  <div className="prediction-result">
    <h3>Random Forest prediction</h3>
    <p>
      Risk level: <strong>{prediction.risk_label}</strong>
    </p>
    <p>
      Probability of delay:{" "}
      <strong>
        {prediction.risk_probability == null
          ? "Not available"
          : `${(prediction.risk_probability * 100).toFixed(1)}%`}
      </strong>
    </p>
    <small>
      Estimation du modèle, pas confirmation de l'état réel de livraison.
    </small>
  </div>
)}
        </section>
      )}
    </section>
  );
}
