import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { GameView } from "./components/GameView";
import { AuthCallback } from "./components/AuthCallback";
import { AuthSuccess } from "./components/AuthSuccess";
import { AuthError } from "./components/AuthError";
import { authService, User } from "./services/auth";
import "./App.css";

export default function App() {
  const [showGame, setShowGame] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  // Check authentication status on app load
  useEffect(() => {
    const checkAuth = async () => {
      const isAuth = await authService.isAuthenticated();
      if (isAuth) {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      }
      setIsCheckingAuth(false);
    };

    checkAuth();

    // Listen for auth state changes
    const handleAuthStateChange = () => {
      checkAuth();
    };

    window.addEventListener("authStateChanged", handleAuthStateChange);

    return () => {
      window.removeEventListener("authStateChanged", handleAuthStateChange);
    };
  }, []);

  function startGame() {
    setShowGame(true);
  }

  // Function to handle Google OAuth login
  async function handleLogin() {
    try {
      const backendUrl =
        process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

      // Get the Google auth URL from the backend
      const response = await fetch(`${backendUrl}/auth/google`);

      if (!response.ok) {
        throw new Error(`Failed to get auth URL: ${response.statusText}`);
      }

      const data = await response.json();

      // Redirect to Google OAuth page
      window.location.href = data.auth_url;
    } catch (error) {
      console.error("Error initiating Google login:", error);
      alert("Failed to initiate Google login. Please try again.");
    }
  }

  function handleLoadout() {
    console.log("Loadout clicked - coming soon!");
  }

  async function handleLogout() {
    await authService.logout();
    setUser(null);
  }

  // Loading screen while checking authentication
  if (isCheckingAuth) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          color: "#ffffff",
          fontSize: "1.2rem",
        }}
      >
        Loading...
      </div>
    );
  }

  // Landing page component
  const LandingPage = () => (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        padding: "2rem",
      }}
    >
      <>
        <div
          style={{
            background: "linear-gradient(145deg, #2a2a2a, #1e1e1e)",
            borderRadius: "20px",
            padding: "3rem",
            boxShadow:
              "0 20px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)",
            border: "1px solid #444",
            minWidth: "400px",
            maxWidth: "500px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "2.5rem",
          }}
        >
          <div style={{ textAlign: "center" }}>
            <h1
              style={{
                fontSize: "3.5rem",
                fontWeight: "700",
                margin: "0",
                textShadow: "2px 2px 8px rgba(0,0,0,0.7)",
                color: "#ffffff",
                letterSpacing: "2px",
              }}
            >
              Chess Reloaded
            </h1>
            <p
              style={{
                fontSize: "1.1rem",
                margin: "1rem 0 0 0",
                color: "#b0b0b0",
                fontWeight: "300",
              }}
            >
              Chess, but if your pieces were cooler
            </p>
            {user && (
              <div
                style={{
                  marginTop: "1rem",
                  padding: "0.75rem 1rem",
                  background: "rgba(76, 175, 80, 0.1)",
                  border: "1px solid rgba(76, 175, 80, 0.3)",
                  borderRadius: "8px",
                  color: "#4CAF50",
                  fontSize: "0.9rem",
                }}
              >
                Welcome back, {user.name}!
              </div>
            )}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr",
              gap: "1rem",
              width: "100%",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr",
                gap: "1rem",
                width: "100%",
              }}
            >
              <button
                onClick={startGame}
                style={{
                  padding: "1rem 2rem",
                  fontSize: "1.1rem",
                  fontWeight: "600",
                  border: "none",
                  borderRadius: "8px",
                  background: "linear-gradient(145deg, #ffffff, #e0e0e0)",
                  color: "#1a1a1a",
                  cursor: "pointer",
                  boxShadow:
                    "0 4px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.8)",
                  transition: "all 0.2s ease",
                  fontFamily: "inherit",
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.boxShadow =
                    "0 6px 16px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.8)";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow =
                    "0 4px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.8)";
                }}
              >
                Play Now
              </button>

              {!user ? (
                <button
                  onClick={handleLogin}
                  style={{
                    padding: "1rem 2rem",
                    fontSize: "1rem",
                    fontWeight: "500",
                    border: "2px solid #707070",
                    borderRadius: "8px",
                    background: "transparent",
                    color: "#d0d0d0",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    fontFamily: "inherit",
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = "#707070";
                    e.currentTarget.style.color = "#1a1a1a";
                    e.currentTarget.style.borderColor = "#808080";
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = "transparent";
                    e.currentTarget.style.color = "#d0d0d0";
                    e.currentTarget.style.borderColor = "#707070";
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  Login with Google
                </button>
              ) : (
                <button
                  onClick={handleLogout}
                  style={{
                    padding: "1rem 2rem",
                    fontSize: "1rem",
                    fontWeight: "500",
                    border: "2px solid #f44336",
                    borderRadius: "8px",
                    background: "transparent",
                    color: "#f44336",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    fontFamily: "inherit",
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = "#f44336";
                    e.currentTarget.style.color = "#ffffff";
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = "transparent";
                    e.currentTarget.style.color = "#f44336";
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  Logout
                </button>
              )}

              <button
                onClick={handleLoadout}
                style={{
                  padding: "1rem 2rem",
                  fontSize: "1rem",
                  fontWeight: "500",
                  border: "2px solid #505050",
                  borderRadius: "8px",
                  background: "transparent",
                  color: "#a0a0a0",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  fontFamily: "inherit",
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = "#505050";
                  e.currentTarget.style.color = "#f0f0f0";
                  e.currentTarget.style.borderColor = "#606060";
                  e.currentTarget.style.transform = "translateY(-1px)";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.color = "#a0a0a0";
                  e.currentTarget.style.borderColor = "#505050";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                Loadout
              </button>
            </div>
          </div>
        </div>
      </>
    </div>
  );

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/auth/success" element={<AuthSuccess />} />
          <Route path="/auth/error" element={<AuthError />} />
          <Route path="/" element={showGame ? <GameView /> : <LandingPage />} />
        </Routes>
      </div>
    </Router>
  );
}
