import { useState } from "react";
import { cookieAuthService } from "../services/cookieAuth";

interface UsernameEditModalProps {
  isOpen: boolean;
  currentUsername: string;
  onClose: () => void;
  onSave: (newUsername: string) => void;
}

export const UsernameEditModal: React.FC<UsernameEditModalProps> = ({
  isOpen,
  currentUsername,
  onClose,
  onSave,
}) => {
  const [username, setUsername] = useState(currentUsername);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!username.trim()) {
      setError("Username cannot be empty");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const updatedUser = await cookieAuthService.updateUsername(username.trim());
      if (updatedUser) {
        onSave(updatedUser.username);
        onClose();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update username");
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={handleBackdropClick}
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
          maxWidth: "500px",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <h3
          style={{
            color: "#ffffff",
            margin: "0",
            fontSize: "2rem",
            fontWeight: "700",
            textAlign: "center",
            textShadow: "2px 2px 8px rgba(0,0,0,0.7)",
            letterSpacing: "1px",
          }}
        >
          Edit Username
        </h3>

        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "1rem",
            fontSize: "1.1rem",
            border: "2px solid #444",
            borderRadius: "8px",
            background: "rgba(26, 26, 26, 0.8)",
            color: "#ffffff",
            outline: "none",
            fontFamily: "inherit",
            boxShadow: "inset 0 2px 4px rgba(0,0,0,0.3)",
            transition: "border-color 0.2s ease",
            boxSizing: "border-box",
            opacity: isLoading ? 0.6 : 1,
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = "#4CAF50";
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = "#444";
          }}
          placeholder="Enter username"
          autoFocus
        />

        {error && (
          <div
            style={{
              color: "#ff6b6b",
              fontSize: "0.9rem",
              textAlign: "center",
              padding: "0.5rem",
              background: "rgba(255, 107, 107, 0.1)",
              borderRadius: "4px",
              border: "1px solid rgba(255, 107, 107, 0.3)",
            }}
          >
            {error}
          </div>
        )}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem",
            width: "100%",
          }}
        >
          <button
            onClick={onClose}
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
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isLoading}
            style={{
              padding: "1rem 2rem",
              fontSize: "1rem",
              fontWeight: "600",
              border: "none",
              borderRadius: "8px",
              background: isLoading
                ? "linear-gradient(145deg, #cccccc, #aaaaaa)"
                : "linear-gradient(145deg, #ffffff, #e0e0e0)",
              color: "#1a1a1a",
              cursor: isLoading ? "not-allowed" : "pointer",
              boxShadow:
                "0 4px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.8)",
              transition: "all 0.2s ease",
              fontFamily: "inherit",
              opacity: isLoading ? 0.7 : 1,
            }}
            onMouseOver={(e) => {
              if (!isLoading) {
                e.currentTarget.style.transform = "translateY(-1px)";
                e.currentTarget.style.boxShadow =
                  "0 6px 16px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.8)";
              }
            }}
            onMouseOut={(e) => {
              if (!isLoading) {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow =
                  "0 4px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.8)";
              }
            }}
          >
            {isLoading ? "Saving..." : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
};
