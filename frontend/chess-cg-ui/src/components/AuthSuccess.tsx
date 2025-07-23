import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/auth";

export function AuthSuccess() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleAuthSuccess = async () => {
      try {
        // Get the token from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get("access_token");

        if (!token) {
          console.error("No token received from backend");
          return;
        }

        console.debug("Token received, storing...");

        // Store token using auth service
        authService.setToken(token);

        // Trigger a custom event to notify the app about the auth change
        window.dispatchEvent(new CustomEvent("authStateChanged"));

        // Redirect back to main app after a short delay
        setTimeout(() => {
          navigate("/");
        });
      } catch (error) {
        console.error("Error handling auth success:", error);
      }
    };

    handleAuthSuccess();
  }, [navigate]);

  return <></>;
}
