// Auth service for handling authentication state and API calls

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export class AuthService {
  private static instance: AuthService;

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  // Get stored JWT token
  getToken(): string | null {
    return localStorage.getItem("authToken");
  }

  // Store JWT token
  setToken(token: string): void {
    localStorage.setItem("authToken", token);
  }

  // Remove JWT token
  clearToken(): void {
    localStorage.removeItem("authToken");
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  // Get current user information
  async getCurrentUser(): Promise<User | null> {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      const response = await fetch(
        `${BACKEND_URL}/auth/me?token=${encodeURIComponent(token)}`
      );

      if (!response.ok) {
        // Token might be expired or invalid
        this.clearToken();
        return null;
      }

      const user = await response.json();
      return user;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    }
  }

  // Logout user
  logout(): void {
    this.clearToken();
    window.location.href = "/";
  }
}

export const authService = AuthService.getInstance();
