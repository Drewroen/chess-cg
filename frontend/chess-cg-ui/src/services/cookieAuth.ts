// Cookie-based authentication service for secure token handling

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export class CookieAuthService {
  private static instance: CookieAuthService;

  static getInstance(): CookieAuthService {
    if (!CookieAuthService.instance) {
      CookieAuthService.instance = new CookieAuthService();
    }
    return CookieAuthService.instance;
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
        // Try to refresh tokens if the access token is expired
        const refreshResponse = await fetch(`${BACKEND_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (refreshResponse.ok) {
          // Retry fetching the current user after refresh
          const retryResponse = await fetch(`${BACKEND_URL}/auth/me`, {
            method: "GET",
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
            },
          });

          if (retryResponse.ok) {
            const user = await retryResponse.json();
            return user;
          }
        }

        return null;
      }

      const user = await response.json();
      return user;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
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
