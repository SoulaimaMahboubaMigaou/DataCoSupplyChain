import { useState } from "react";
import { Boxes, LockKeyhole } from "lucide-react";
import { login } from "../services/api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      onLogin();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="login-logo"><Boxes size={30} /></div>
        <p className="eyebrow">DATACO INTELLIGENCE</p>
        <h1>Welcome back</h1>
        <p className="muted">Connectez-vous à votre espace administrateur.</p>

        <label className="field">
          Email
          <input
            type="email"
            autoComplete="username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@dataco.local"
            required
          />
        </label>

        <label className="field">
          Mot de passe
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && <p className="error-message">{error}</p>}

        <button className="primary-button" disabled={loading}>
          <LockKeyhole size={16} />
          {loading ? "Connexion..." : "Se connecter"}
        </button>

        <p className="form-note">Accès réservé à l'administrateur autorisé.</p>
      </form>
    </main>
  );
}