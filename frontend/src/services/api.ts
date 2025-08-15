import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AuthResponse, LoginCredentials, RegisterData, User, Book, ApiError } from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth interceptor
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Helper method to handle API responses
  private handleResponse<T>(response: AxiosResponse<T>): T {
    return response.data;
  }

  // Helper method to handle API errors
  private handleError(error: unknown): never {
    interface ErrorWithResponse {
      response?: {
        data?: {
          error?: string;
          details?: Record<string, string[]> | string;
        };
        status?: number;
      };
      message?: string;
    }

    const errorObj = error as ErrorWithResponse;
    const rawDetails = errorObj.response?.data?.details;
    const apiError: ApiError = {
      error: errorObj.response?.data?.error || errorObj.message || 'An error occurred',
      details: typeof rawDetails === 'string' ? undefined : rawDetails,
      status: errorObj.response?.status || 500,
    };
    throw apiError;
  }

  // Authentication endpoints
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await this.api.post<AuthResponse>('/auth/login', credentials);
      const authData = this.handleResponse(response);
      
      // Store tokens
      localStorage.setItem('access_token', authData.access_token);
      localStorage.setItem('refresh_token', authData.refresh_token);
      
      return authData;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await this.api.post<AuthResponse>('/auth/register', data);
      const authData = this.handleResponse(response);
      
      // Store tokens
      localStorage.setItem('access_token', authData.access_token);
      localStorage.setItem('refresh_token', authData.refresh_token);
      
      return authData;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await this.api.get<User>('/auth/me');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // User endpoints
  async getUsers(): Promise<User[]> {
    try {
      const response = await this.api.get<User[]>('/auth/users');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getUser(userId: number): Promise<User> {
    try {
      const response = await this.api.get<User>(`/auth/users/${userId}`);
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Book endpoints
  async getBooks(): Promise<Book[]> {
    try {
      const response = await this.api.get<Book[]>('/books/');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getBook(bookId: number): Promise<Book> {
    try {
      const response = await this.api.get<Book>(`/books/${bookId}`);
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Search books
  async searchBooks(query: string): Promise<Book[]> {
    try {
      const response = await this.api.get<Book[]>(`/books/?search=${encodeURIComponent(query)}`);
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Friendship endpoints (placeholder - to be implemented)
  async getFriendships(): Promise<unknown> {
    try {
      const response = await this.api.get('/friends/');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async sendFriendRequest(): Promise<unknown> {
    try {
      const response = await this.api.post('/friends/request');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Exchange endpoints (placeholder - to be implemented)
  async getExchanges(): Promise<unknown> {
    try {
      const response = await this.api.get('/exchanges/');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async requestExchange(): Promise<unknown> {
    try {
      const response = await this.api.post('/exchanges/request');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Message endpoints (placeholder - to be implemented)
  async getMessages(): Promise<unknown> {
    try {
      const response = await this.api.get('/messages/');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async sendMessage(): Promise<unknown> {
    try {
      const response = await this.api.post('/messages/send');
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService; 