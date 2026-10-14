import { useEffect, useState } from "react";
import { CheckCircle2, Mail, ShieldCheck } from "lucide-react";

import {
  changePassword,
  getProfile,
  updateEmail,
} from "../services/api";

const MIN_PASSWORD_LENGTH = 10;

function Feedback({ message }) {
  if (!message?.text) return null;

  return (
    <div
      className={
        message.type === "error" ? "error-message" : "success-message"
      }
      role={message.type === "error" ? "alert" : "status"}
    >
      {message.type === "success" && <CheckCircle2 size={15} />}
      <span>{message.text}</span>
    </div>
  );
}

export default function Profile({ onProfileChange }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [email, setEmail] = useState("");
  const [emailPassword, setEmailPassword] = useState("");
  const [emailSaving, setEmailSaving] = useState(false);
  const [emailMessage, setEmailMessage] = useState(null);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState(null);

  useEffect(() => {
    let active = true;

    getProfile()
      .then((data) => {
        if (!active) return;
        setProfile(data);
        setEmail(data.email || "");
      })
      .catch((err) => active && setLoadError(err.message))
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
  }, []);

  function applyProfile(data) {
    setProfile(data);
    setEmail(data.email || "");
    onProfileChange?.(data);
  }

  async function submitEmail(event) {
    event.preventDefault();
    setEmailMessage(null);

    const next = email.trim().toLowerCase();

    if (!next) {
      setEmailMessage({ type: "error", text: "L'adresse email est obligatoire." });
      return;
    }

    if (next === profile?.email) {
      setEmailMessage({
        type: "error",
        text: "Cette adresse email est déjà la vôtre.",
      });
      return;
    }

    if (!emailPassword) {
      setEmailMessage({
        type: "error",
        text: "Saisissez votre mot de passe actuel pour confirmer.",
      });
      return;
    }

    if (
      !window.confirm(
        `Changer l'adresse de connexion en « ${next} » ? ` +
        "Elle remplacera votre identifiant actuel."
      )
    ) {
      return;
    }

    setEmailSaving(true);

    try {
      const data = await updateEmail(next, emailPassword);
      applyProfile(data.profile);
      setEmailPassword("");
      setEmailMessage({ type: "success", text: data.message });
    } catch (err) {
      setEmailMessage({ type: "error", text: err.message });
    } finally {
      setEmailSaving(false);
    }
  }

  async function submitPassword(event) {
    event.preventDefault();
    setPasswordMessage(null);

    if (!currentPassword) {
      setPasswordMessage({
        type: "error",
        text: "Saisissez votre mot de passe actuel.",
      });
      return;
    }

    if (newPassword.length < MIN_PASSWORD_LENGTH) {
      setPasswordMessage({
        type: "error",
        text:
          "Le nouveau mot de passe doit contenir au moins " +
          `${MIN_PASSWORD_LENGTH} caractères.`,
      });
      return;
    }

    if (!/[A-Za-z]/.test(newPassword) || !/\d/.test(newPassword)) {
      setPasswordMessage({
        type: "error",
        text: "Il doit contenir au moins une lettre et un chiffre.",
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordMessage({
        type: "error",
        text: "La confirmation ne correspond pas au nouveau mot de passe.",
      });
      return;
    }

    if (
      !window.confirm(
        "Changer le mot de passe ? Toutes les autres sessions seront " +
        "déconnectées."
      )
    ) {
      return;
    }

    setPasswordSaving(true);

    try {
      const data = await changePassword(currentPassword, newPassword);
      applyProfile(data.profile);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setPasswordMessage({ type: "success", text: data.message });
    } catch (err) {
      setPasswordMessage({ type: "error", text: err.message });
    } finally {
      setPasswordSaving(false);
    }
  }

  if (loading) {
    return (
      <section className="panel">
        <p className="muted">Chargement du profil...</p>
      </section>
    );
  }

  if (loadError) {
    return (
      <section className="panel">
        <div className="error-message" role="alert">{loadError}</div>
      </section>
    );
  }

  return (
    <div className="profile-page">
      <section className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">ACCOUNT INFORMATION</span>
            <h2>Informations du compte</h2>
            <p>Identifiant utilisé pour vous connecter au workspace.</p>
          </div>
          <span className="model-tag">Administrator</span>
        </div>

        <div className="model-details">
          <div>
            <span>Email actuel</span>
            <strong>{profile?.email}</strong>
          </div>
          <div>
            <span>Rôle</span>
            <strong>{profile?.role}</strong>
          </div>
          <div>
            <span>Dernière modification</span>
            <strong>
              {profile?.updated_at
                ? new Date(profile.updated_at).toLocaleString()
                : "—"}
            </strong>
          </div>
        </div>

        <form className="profile-form" onSubmit={submitEmail}>
          <label className="field">
            <span>Nouvelle adresse email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </label>

          <label className="field">
            <span>Mot de passe actuel (confirmation)</span>
            <input
              type="password"
              value={emailPassword}
              onChange={(event) => setEmailPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          <div className="form-actions">
            <Feedback message={emailMessage} />

            <button
              className="primary-button"
              type="submit"
              disabled={emailSaving}
            >
              <Mail size={16} />
              {emailSaving
                ? "Enregistrement..."
                : "Enregistrer les modifications"}
            </button>
          </div>
        </form>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">SECURITY</span>
            <h2>Sécurité</h2>
            <p>
              Au moins {MIN_PASSWORD_LENGTH} caractères, avec une lettre et un
              chiffre.
            </p>
          </div>
          <span className="model-tag">Argon2</span>
        </div>

        <form className="profile-form" onSubmit={submitPassword}>
          <label className="field">
            <span>Mot de passe actuel</span>
            <input
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          <label className="field">
            <span>Nouveau mot de passe</span>
            <input
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              autoComplete="new-password"
              minLength={MIN_PASSWORD_LENGTH}
              required
            />
          </label>

          <label className="field">
            <span>Confirmer le nouveau mot de passe</span>
            <input
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              autoComplete="new-password"
              minLength={MIN_PASSWORD_LENGTH}
              required
            />
          </label>

          <div className="form-actions">
            <Feedback message={passwordMessage} />

            <button
              className="primary-button"
              type="submit"
              disabled={passwordSaving}
            >
              <ShieldCheck size={16} />
              {passwordSaving ? "Mise à jour..." : "Changer le mot de passe"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
