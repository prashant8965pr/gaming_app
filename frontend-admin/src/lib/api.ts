/**
 * Admin API Client
 * Handles all API requests to the backend with authentication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  LoginRequest,
  LoginResponse,
  DashboardStats,
  PlatformUser,
  UserDetails,
  KYCDocument,
  ReviewKYCRequest,
  WithdrawalRequest,
  ReviewWithdrawalRequest,
  APIResponse,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class AdminAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('admin_token');
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('admin_token', token);
    }
  }

  private clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_user');
    }
  }

  // ============================================================================
  // Authentication
  // ============================================================================

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<APIResponse<LoginResponse>>('/auth/login', data);
    const loginData = response.data.data;

    // Store token and user
    this.setToken(loginData.access_token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('admin_user', JSON.stringify(loginData.user));
    }

    return loginData;
  }

  logout(): void {
    this.clearToken();
  }

  async getMe() {
    const response = await this.client.get('/auth/me');
    return response.data.data;
  }

  // ============================================================================
  // Dashboard
  // ============================================================================

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get<APIResponse<DashboardStats>>('/admin/dashboard/stats');
    return response.data.data;
  }

  // ============================================================================
  // User Management
  // ============================================================================

  async getUsers(params?: {
    limit?: number;
    offset?: number;
    search?: string;
    status_filter?: string;
    kyc_status_filter?: string;
  }): Promise<{ users: PlatformUser[]; total_count: number; limit: number; offset: number }> {
    const response = await this.client.get('/admin/users', { params });
    return response.data.data;
  }

  async getUserDetails(userId: string): Promise<UserDetails> {
    const response = await this.client.get<APIResponse<UserDetails>>(`/admin/users/${userId}`);
    return response.data.data;
  }

  async updateUserStatus(
    userId: string,
    status: string,
    reason?: string
  ): Promise<void> {
    await this.client.put(`/admin/users/${userId}/status`, { status_update: status, reason });
  }

  // ============================================================================
  // KYC Management
  // ============================================================================

  async getPendingKYC(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{ documents: KYCDocument[]; total_count: number }> {
    const response = await this.client.get('/admin/kyc/pending', { params });
    return response.data.data;
  }

  async reviewKYC(data: ReviewKYCRequest): Promise<void> {
    await this.client.post('/admin/kyc/review', data);
  }

  // ============================================================================
  // Withdrawal Management
  // ============================================================================

  async getPendingWithdrawals(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{ withdrawals: WithdrawalRequest[]; total_count: number }> {
    const response = await this.client.get('/admin/withdrawals/pending', { params });
    return response.data.data;
  }

  async reviewWithdrawal(data: ReviewWithdrawalRequest): Promise<void> {
    await this.client.post('/admin/withdrawals/review', data);
  }

  async processWithdrawalPayout(data: {
    withdrawal_id: string;
    utr_number: string;
    gateway_payout_id?: string;
    admin_notes?: string;
  }): Promise<void> {
    await this.client.post('/admin/withdrawals/process-payout', data);
  }

  // ============================================================================
  // Balance Adjustment
  // ============================================================================

  async adjustBalance(data: {
    user_id: string;
    wallet_type: string;
    amount: number;
    reason: string;
    admin_notes?: string;
  }): Promise<void> {
    await this.client.post('/admin/wallet/adjust-balance', data);
  }
}

// Export singleton instance
export const api = new AdminAPI();
