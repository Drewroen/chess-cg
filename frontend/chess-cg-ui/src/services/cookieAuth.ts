// Cookie-based authentication service for secure token handling

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  user_type?: string;
}

export interface GuestUser extends User {
  user_type: 'guest';
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
      const response = await fetch(`${BACKEND_URL}/auth/guest-session`, {
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
      const response = await fetch(`${BACKEND_URL}/auth/me`, {
        method: "GET",
        credentials: "include", // Include cookies in request
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        // Check if the error is due to missing token vs expired token
        const errorData = await response.json().catch(() => ({ detail: "" }));
        
        // If no access token found, try to create guest session
        if (errorData.detail === "Access token not found") {
          return await this.createGuestSession();
        }
        
        // Try to refresh tokens if the access token is expired
        const refreshResponse = await fetch(`${BACKEND_URL}/auth/refresh`, {
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
        const retryResponse = await fetch(`${BACKEND_URL}/auth/me`, {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!retryResponse.ok) {
          return await this.createGuestSession();
        }

        const user = await retryResponse.json();
        return user;
      }

      const user = await response.json();
      return user;
    } catch (error) {
      console.error("Error fetching current user:", error);
      // Fallback to guest session on any error
      return await this.createGuestSession();
    }
  }

  // Logout user by calling backend logout endpoint
  async logout(): Promise<void> {
    try {
      await fetch(`${BACKEND_URL}/auth/logout`, {
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
