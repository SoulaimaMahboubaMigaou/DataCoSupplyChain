import { useEffect, useState } from "react";
import {
  Navigate,
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  Activity,
  Boxes,
  Brain,
  History as HistoryIcon,
  LayoutDashboard,
  LogOut,
  Truck,
  UserCog,
} from "lucide-react";

import Login from "./pages/login";
import Overview from "./pages/overview";
import LiveTracking from "./pages/LiveTracking";
import Prediction from "./pages/prediction";
import History from "./pages/history";
import Profile from "./pages/profile";
import { apiRequest, clearToken, getToken } from "./services/api";

// Une seule source de vérité : l'URL, le titre et le menu dérivent de cette
// liste.
const PAGES = [
  { path: "/", title: "Overview", label: "Overview", icon: LayoutDashboard },
  {
    path: "/tracking",
    title: "Shipment Tracking",
    label: "Shipment Tracking",
    icon: Truck,
  },
  { path: "/prediction", title: "Prediction", label: "Prediction", icon: Brain },
  { path: "/history", title: "History", label: "History", icon: HistoryIcon },
  {
    path: "/profile",
    title: "My Profile",
    label: "My Profile",
    icon: UserCog,
  },
];

function navClass({ isActive }) {
  return `nav-item ${isActive ? "active" : ""}`;
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [checking, setChecking] = useState(true);
  const [summary, setSummary] = useState(null);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  const location = useLocation();
  const navigate = useNavigate();

  const title =
    PAGES.find((page) => page.path === location.pathname)?.title ?? "Overview";

  useEffect(() => {
    const handleLogout = () => {
      setAuthenticated(false);
      setChecking(false);
    };

    window.addEventListener("dataco:logout", handleLogout);

    async function verifySession() {
      if (!getToken()) {
        setChecking(false);
        return;
      }

      try {
        setProfile(await apiRequest("/auth/me"));
        setAuthenticated(true);
      } catch {
        clearToken();
        setAuthenticated(false);
      } finally {
        setChecking(false);
      }
    }

    verifySession();

    return () => window.removeEventListener("dataco:logout", handleLogout);
  }, []);

  useEffect(() => {
    if (!authenticated) return;

    apiRequest("/tracking/summary")
      .then(setSummary)
      .catch((err) => setError(err.message));
  }, [authenticated, location.pathname]);

  function logout() {
    clearToken();
    setAuthenticated(false);
    setProfile(null);
    navigate("/");
  }

  async function handleLogin() {
    setAuthenticated(true);

    try {
      setProfile(await apiRequest("/auth/me"));
    } catch {
      setProfile(null);
    }
  }

  if (checking) {
    return <div className="loading-screen">Vérification de la session...</div>;
  }

  // L'URL demandée est conservée : après connexion on revient dessus.
  if (!authenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo"><Boxes size={25} /></div>
          <div>
            <strong>DataCo <span>Intelligence</span></strong>
            <small>SUPPLY CHAIN ANALYTICS</small>
          </div>
        </div>

        <p className="nav-caption">WORKSPACE</p>

        <nav className="navigation">
          {PAGES.map(({ path, label, icon: Icon }) => (
            <NavLink key={path} to={path} end={path === "/"} className={navClass}>
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <span className="status-dot online" />
          <NavLink
            className="sidebar-account"
            to="/profile"
            title="Ouvrir mon profil"
          >
            <strong>Administrator</strong>
            <small>{profile?.email || "Session active"}</small>
          </NavLink>
          <button
            className="icon-button"
            onClick={logout}
            title="Déconnexion"
          >
            <LogOut size={17} />
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace / DataCo</span>
            <h1>{title}</h1>
          </div>
          <div className="topbar-right">
            <Activity size={16} />
            <span>Historical dataset</span>
          </div>
        </header>

        {error && <p className="error-message">{error}</p>}

        <Routes>
          <Route path="/" element={<Overview summary={summary} />} />
          <Route path="/tracking" element={<LiveTracking />} />
          <Route path="/prediction" element={<Prediction />} />
          <Route path="/history" element={<History />} />
          <Route
            path="/profile"
            element={<Profile onProfileChange={setProfile} />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        <footer>
          <span>DataCo Supply Chain Intelligence</span>
          <span>Admin workspace · Historical data</span>
        </footer>
      </main>
    </div>
  );
}
