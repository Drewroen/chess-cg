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
import styles from "./App.module.css";

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



  // Loading screen while checking authentication
  if (isCheckingAuth) {
    return <></>;
  }

  // Landing page component
  const LandingPage = () => (
    <div className={`${styles.landingContainer} ${isMobile ? styles.mobile : ''}`}>
      <>
        <div className={`${styles.mainCard} ${isMobile ? styles.mobile : ''}`}>
          <div className={styles.headerSection}>
            <h1 className={`${styles.title} ${isMobile ? styles.mobile : ''}`}>
              ReChess
            </h1>
            <p className={`${styles.subtitle} ${isMobile ? styles.mobile : ''}`}>
              Chess, but redefined.
            </p>
            {user && (
              <div className={`${styles.userInfo} ${user.user_type === "guest" ? styles.guest : styles.authenticated}`}>
                Playing as{" "}
                <span
                  onClick={handleUsernameClick}
                  className={styles.usernameLink}
                >
                  {user.username}
                </span>
              </div>
            )}
          </div>

          <div className={styles.actionsGrid}>
            <div className={styles.buttonContainer}>
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
                <div className={`${styles.loadingText} ${isMobile ? styles.mobile : ''}`}>
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
