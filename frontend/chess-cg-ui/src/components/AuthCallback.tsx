import { useEffect, useState } from "react";
import { Button } from "./Button";
import { backendUrl } from "../config/environment";
import styles from "./AuthCallback.module.css";

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
        const response = await fetch(
          `${backendUrl}/auth/callback?code=${encodeURIComponent(code)}`,
          {
            credentials: "include", // Include cookies to receive the httpOnly tokens
          }
        );

        if (!response.ok) {
          throw new Error(`Backend auth failed: ${response.statusText}`);
        }

        // Check if we were redirected to the success page (tokens are now in cookies)
        if (response.redirected && response.url.includes("/auth/success")) {
          setStatus("success");
          setMessage("Authentication successful!");

          // Redirect back to main app after a short delay
          setTimeout(() => {
            window.location.href = "/";
          }, 2000);
        } else {
          setMessage("Authentication failed");
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
    <div className={styles.container}>
      <div className={styles.statusCard}>
        {status === "loading" && (
          <>
            <div className={`${styles.statusTitle} ${styles.loading}`}>
              Authenticating with Google...
            </div>
            <div className={styles.statusMessage}>
              Please wait while we verify your credentials.
            </div>
          </>
        )}

        {status === "success" && (
          <>
            <div className={`${styles.statusTitle} ${styles.success}`}>
              Login Successful!
            </div>
            <div className={styles.statusMessage}>
              {message || "Redirecting you back to the game..."}
            </div>
          </>
        )}

        {status === "error" && (
          <>
            <div className={`${styles.statusTitle} ${styles.error}`}>
              Authentication Error
            </div>
            <div className={styles.statusMessage}>
              {message || "There was a problem with the login process."}
            </div>
            <Button
              onClick={() => (window.location.href = "/")}
              variant="neutral"
              style={{ color: "#d0d0d0", borderColor: "#707070" }}
            >
              Return to Home
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
