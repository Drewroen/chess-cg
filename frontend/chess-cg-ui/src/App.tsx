import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { GameView } from "./components/GameView";
import { AuthCallback } from "./components/AuthCallback";
import { AuthSuccess } from "./components/AuthSuccess";
import { AuthError } from "./components/AuthError";
import { UsernameEditModal } from "./components/UsernameEditModal";
import { Button } from "./components/Button";
import { useAuth } from "./hooks/useAuth";
import "./App.css";

// Custom hook for responsive design
function useResponsive() {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return isMobile;
}

export default function App() {
  const [showGame, setShowGame] = useState(false);
  const [isUsernameModalOpen, setIsUsernameModalOpen] = useState(false);
  const isMobile = useResponsive();
  const { user, setUser, isCheckingAuth, login, logout } = useAuth();

  function startGame() {
    setShowGame(true);
  }

  function handleUsernameClick() {
    setIsUsernameModalOpen(true);
  }

  function handleUsernameModalClose() {
    setIsUsernameModalOpen(false);
  }

  function handleUsernameSave(newUsername: string) {
    if (user) {
      setUser({
        ...user,
        username: newUsername,
      });
    }
  }

  // Hover event handlers
  function handleUsernameMouseOver(e: React.MouseEvent<HTMLSpanElement>) {
    e.currentTarget.style.opacity = "0.8";
  }

  function handleUsernameMouseOut(e: React.MouseEvent<HTMLSpanElement>) {
    e.currentTarget.style.opacity = "1";
  }


  // Loading screen while checking authentication
  if (isCheckingAuth) {
    return <></>;
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
        padding: isMobile ? "1rem" : "2rem",
      }}
    >
      <>
        <div
          style={{
            background: "linear-gradient(145deg, #2a2a2a, #1e1e1e)",
            borderRadius: isMobile ? "12px" : "20px",
            padding: isMobile ? "1.5rem" : "3rem",
            boxShadow:
              "0 20px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)",
            border: "1px solid #444",
            minWidth: isMobile ? "280px" : "400px",
            maxWidth: isMobile ? "90vw" : "500px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: isMobile ? "1.5rem" : "2.5rem",
          }}
        >
          <div style={{ textAlign: "center" }}>
            <h1
              style={{
                fontSize: isMobile ? "2.5rem" : "3.5rem",
                fontWeight: "700",
                margin: "0",
                textShadow: "2px 2px 8px rgba(0,0,0,0.7)",
                color: "#ffffff",
                letterSpacing: isMobile ? "1px" : "2px",
              }}
            >
              ReChess
            </h1>
            <p
              style={{
                fontSize: isMobile ? "1rem" : "1.1rem",
                margin: "1rem 0 0 0",
                color: "#b0b0b0",
                fontWeight: "300",
              }}
            >
              Chess, but redefined.
            </p>
            {user && (
              <div
                style={{
                  marginTop: "1rem",
                  padding: "0.75rem 1rem",
                  background:
                    user.user_type === "guest"
                      ? "rgba(255, 193, 7, 0.1)"
                      : "rgba(76, 175, 80, 0.1)",
                  border:
                    user.user_type === "guest"
                      ? "1px solid rgba(255, 193, 7, 0.3)"
                      : "1px solid rgba(76, 175, 80, 0.3)",
                  borderRadius: "8px",
                  color: user.user_type === "guest" ? "#FFC107" : "#4CAF50",
                  fontSize: "0.9rem",
                }}
              >
                Playing as{" "}
                <span
                  onClick={handleUsernameClick}
                  style={{
                    cursor: "pointer",
                    textDecoration: "underline",
                    fontWeight: "600",
                  }}
                  onMouseOver={handleUsernameMouseOver}
                  onMouseOut={handleUsernameMouseOut}
                >
                  {user.username}
                </span>
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
              <Button
                onClick={startGame}
                variant="primary"
                isMobile={isMobile}
                style={{ fontSize: isMobile ? "1rem" : "1.1rem" }}
              >
                Play Now
              </Button>

              {user?.user_type === "guest" ? (
                <Button
                  onClick={login}
                  variant="secondary"
                  isMobile={isMobile}
                >
                  Login with Google
                </Button>
              ) : user?.user_type === "authenticated" ? (
                <Button
                  onClick={logout}
                  variant="danger"
                  isMobile={isMobile}
                >
                  Logout
                </Button>
              ) : (
                <div
                  style={{
                    padding: isMobile ? "0.875rem 1.5rem" : "1rem 2rem",
                    fontSize: isMobile ? "0.9rem" : "1rem",
                    color: "#888",
                    textAlign: "center",
                  }}
                >
                  Loading user session...
                </div>
              )}

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
          <Route path="/" element={showGame ? <GameView isMobile={isMobile} /> : <LandingPage />} />
        </Routes>
        {user && (
          <UsernameEditModal
            isOpen={isUsernameModalOpen}
            currentUsername={user.username}
            onClose={handleUsernameModalClose}
            onSave={handleUsernameSave}
          />
        )}
      </div>
    </Router>
  );
}
