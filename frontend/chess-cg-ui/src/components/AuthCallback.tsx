import { useEffect, useState } from "react";
import { authService } from "../services/auth";

export function AuthCallback() {
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Get the authorization code from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get("code");
        const error = urlParams.get("error");

        if (error) {
          console.error("OAuth error:", error);
          setMessage(`OAuth error: ${error}`);
          setStatus("error");
          return;
        }

        if (!code) {
          console.error("No authorization code received");
          setMessage("No authorization code received from Google");
          setStatus("error");
          return;
        }

        console.debug("Authorization code received, exchanging for token...");

        // Send the authorization code to the backend
        const backendUrl =
          process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
        const response = await fetch(
          `${backendUrl}/auth/callback?code=${encodeURIComponent(code)}`
        );

        if (!response.ok) {
          throw new Error(`Backend auth failed: ${response.statusText}`);
        }

        const authResult = await response.json();

        if (authResult.success) {
          setStatus("success");
          setMessage("Authentication successful!");

          // Store the JWT token if provided in the redirect URL
          const redirectUrl = new URL(authResult.redirect_url);
          const token = redirectUrl.searchParams.get("token");

          if (token) {
            // Store token using auth service
            authService.setToken(token);
          }

          // Redirect back to main app after a short delay
          setTimeout(() => {
            window.location.href = "/";
          }, 2000);
        } else {
          setMessage(authResult.message || "Authentication failed");
          setStatus("error");
        }
      } catch (error) {
        console.error("Error handling auth callback:", error);
        setMessage(
          error instanceof Error ? error.message : "Unknown error occurred"
        );
        setStatus("error");
      }
    };

    handleAuthCallback();
  }, []);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        padding: "2rem",
        fontFamily: "inherit",
      }}
    >
      <div
        style={{
          background: "linear-gradient(145deg, #2a2a2a, #1e1e1e)",
          borderRadius: "20px",
          padding: "3rem",
          boxShadow:
            "0 20px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)",
          border: "1px solid #444",
          minWidth: "400px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "2rem",
          textAlign: "center",
        }}
      >
        {status === "loading" && (
          <>
            <div
              style={{
                color: "#ffffff",
                fontSize: "1.5rem",
                fontWeight: "600",
              }}
            >
              Authenticating with Google...
            </div>
            <div style={{ color: "#b0b0b0" }}>
              Please wait while we verify your credentials.
            </div>
          </>
        )}

        {status === "success" && (
          <>
            <div
              style={{
                color: "#4CAF50",
                fontSize: "1.5rem",
                fontWeight: "600",
              }}
            >
              Login Successful!
            </div>
            <div style={{ color: "#b0b0b0" }}>
              {message || "Redirecting you back to the game..."}
            </div>
          </>
        )}

        {status === "error" && (
          <>
            <div
              style={{
                color: "#f44336",
                fontSize: "1.5rem",
                fontWeight: "600",
              }}
            >
              Authentication Error
            </div>
            <div style={{ color: "#b0b0b0" }}>
              {message || "There was a problem with the login process."}
            </div>
            <button
              onClick={() => (window.location.href = "/")}
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
            >
              Return to Home
            </button>
          </>
        )}
      </div>
    </div>
  );
}
