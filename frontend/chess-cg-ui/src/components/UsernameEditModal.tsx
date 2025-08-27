import { useState } from "react";
import { cookieAuthService } from "../services/cookieAuth";
import { Button } from "./Button";
import styles from "./UsernameEditModal.module.css";

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
    <div className={styles.backdrop} onClick={handleBackdropClick}>
      <div className={styles.modal}>
        <h3 className={styles.title}>
          Edit Username
        </h3>

        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={isLoading}
          className={styles.input}
          placeholder="Enter username"
          autoFocus
        />

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        <div className={styles.buttonContainer}>
          <Button onClick={onClose} variant="neutral">
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="primary"
            isLoading={isLoading}
            disabled={isLoading}
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  );
};
