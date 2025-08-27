// Cookie-based authentication service for secure token handling

import { backendUrl } from "../config/environment";

export interface User {
  id: string;
  email: string;
  name: string;
  username: string;
  user_type?: string;
}

export interface GuestUser extends User {
  user_type: "guest";
}

export class CookieAuthService {
  private static instance: CookieAuthService;

  static getInstance(): CookieAuthService {
    if (!CookieAuthService.instance) {
      CookieAuthService.instance = new CookieAuthService();
    }
    return CookieAuthService.instance;
  }

  // New method to create guest session
  async createGuestSession(): Promise<GuestUser | null> {
    try {
      const response = await fetch(`${backendUrl}/auth/guest-session`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        console.error("Failed to create guest session");
        return null;
      }

      // Get the guest user info from the new access token
      return this.getCurrentUser() as Promise<GuestUser | null>;
    } catch (error) {
      console.error("Error creating guest session:", error);
      return null;
    }
  }

  // Get current user information from backend
  async getCurrentUser(): Promise<User | null> {
    try {
      let response = await fetch(`${backendUrl}/auth/me`, {
        method: "GET",
        credentials: "include", // Include cookies in request
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        // Try to refresh tokens
        const refreshResponse = await fetch(`${backendUrl}/auth/refresh`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!refreshResponse.ok) {
          // If refresh fails and no tokens exist, create guest session
          return await this.createGuestSession();
        }

        // Retry fetching the current user after refresh
        response = await fetch(`${backendUrl}/auth/me`, {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    }
  }

  // Update current user's username
  async updateUsername(newUsername: string): Promise<User | null> {
    try {
      const response = await fetch(`${backendUrl}/auth/me/username`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: newUsername }),
      });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ detail: "Unknown error" }));

        // Handle validation errors (array format)
        if (Array.isArray(errorData.detail)) {
          const errorMessage =
            errorData.detail[0]?.msg.replace(/^Value error, /, "") ||
            "Validation error";
          throw new Error(errorMessage);
        }

        // Handle simple string errors
        throw new Error(errorData.detail || "Failed to update username");
      }

      const updatedUser = await response.json();
      return updatedUser;
    } catch (error) {
      console.error("Error updating username:", error);
      throw error;
    }
  }

  // Logout user by calling backend logout endpoint
  async logout(): Promise<void> {
    try {
      await fetch(`${backendUrl}/auth/logout`, {
        method: "POST",
        credentials: "include", // Include cookies to clear them
        headers: {
          "Content-Type": "application/json",
        },
      });
    } catch (error) {
      console.error("Error logging out:", error);
    } finally {
      // Redirect to home page regardless of API call success
      window.location.href = "/";
    }
  }
}

export const cookieAuthService = CookieAuthService.getInstance();
