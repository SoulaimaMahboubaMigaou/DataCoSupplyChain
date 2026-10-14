const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "dataco_token";

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

// FastAPI renvoie `detail` en texte, en objet, ou en liste (erreurs Pydantic).
function readError(data, status) {
  const detail = data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => item?.msg)
      .filter(Boolean);
    if (messages.length) return messages.join(" · ");
  }

  if (detail && typeof detail === "object") {
    return detail.message || JSON.stringify(detail);
  }

  return `API error: ${status}`;
}

export async function apiRequest(path, options = {}) {
  const token = getToken();

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    clearToken();
    window.dispatchEvent(new Event("dataco:logout"));
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(readError(data, response.status));
  }

  return data;
}

export async function login(email, password) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(readError(data, response.status) || "Connexion impossible.");
  }

  setToken(data.access_token);
  return data;
}

export function logout() {
  clearToken();
  window.dispatchEvent(new Event("dataco:logout"));
}

// --- Administrator profile ---

export const getProfile = () => apiRequest("/auth/me");

// Les deux endpoints renvoient un token frais : l'ancien est lié à l'ancien
// email (PATCH) ou invalidé par le changement de mot de passe (POST).
export async function updateEmail(email, currentPassword) {
  const data = await apiRequest("/auth/me", {
    method: "PATCH",
    body: JSON.stringify({ email, current_password: currentPassword }),
  });

  setToken(data.access_token);
  return data;
}

export async function changePassword(currentPassword, newPassword) {
  const data = await apiRequest("/auth/change-password", {
    method: "POST",
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });

  setToken(data.access_token);
  return data;
}

export const getSummary = () => apiRequest("/tracking/summary");

export const getShipments = (params = {}) => {
  const query = new URLSearchParams(params);
  return apiRequest(`/tracking/shipments?${query}`);
};

export const getShipment = (id) =>
  apiRequest(`/tracking/shipments/${encodeURIComponent(id)}`);

// Predict delivery risk from the 16 feature values in the form


export const predictDeliveryRisk = (features) =>
  apiRequest("/predict", {
    method: "POST",
    body: JSON.stringify(features),
  });