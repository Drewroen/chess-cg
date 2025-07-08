import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export function AuthError() {
  const [message, setMessage] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    // Get the error message from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const errorMessage = urlParams.get("message");

    if (errorMessage) {
      setMessage(decodeURIComponent(errorMessage));
    } else {
      setMessage("An unknown authentication error occurred");
    }
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
        <div
          style={{
            color: "#f44336",
            fontSize: "1.5rem",
            fontWeight: "600",
          }}
        >
          Authentication Error
        </div>
        <div style={{ color: "#b0b0b0" }}>{message}</div>
        <button
          onClick={() => navigate("/")}
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
          Return to Home
        </button>
      </div>
    </div>
  );
}
