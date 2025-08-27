import { useState, useEffect } from "react";
import { cookieAuthService, User, GuestUser } from "../services/cookieAuth";
import { backendUrl } from "../config/environment";

export function useAuth() {
  const [user, setUser] = useState<User | GuestUser | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const currentUser = await cookieAuthService.getCurrentUser();
      setUser(currentUser);
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

  const login = async () => {
    try {
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
  };

  const logout = async () => {
    await cookieAuthService.logout();
    setUser(null);
  };

  return {
    user,
    setUser,
    isCheckingAuth,
    login,
    logout,
  };
}