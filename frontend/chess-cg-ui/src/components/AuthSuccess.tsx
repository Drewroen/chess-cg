import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function AuthSuccess() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleAuthSuccess = async () => {
      try {
        console.debug("Authentication successful, tokens are now stored in httpOnly cookies");

        // Trigger a custom event to notify the app about the auth change
        window.dispatchEvent(new CustomEvent("authStateChanged"));

        // Redirect back to main app after a short delay
        setTimeout(() => {
          navigate("/");
        }, 500);
      } catch (error) {
        console.error("Error handling auth success:", error);
      }
    };

    handleAuthSuccess();
  }, [navigate]);

  return <></>;
}
