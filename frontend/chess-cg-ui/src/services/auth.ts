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

  // Cookie utility methods
  private setCookie(name: string, value: string, days: number = 7): void {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Strict;Secure=${
      window.location.protocol === "https:"
    }`;
  }

  private getCookie(name: string): string | null {
    const nameEQ = name + "=";
    const ca = document.cookie.split(";");
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === " ") c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  private deleteCookie(name: string): void {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
  }

  // Get stored JWT token
  getToken(): string | null {
    return this.getCookie("authToken");
  }

  // Store JWT token
  setToken(token: string): void {
    this.setCookie("authToken", token, 7);
  }

  // Remove JWT token
  clearToken(): void {
    this.deleteCookie("authToken");
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
