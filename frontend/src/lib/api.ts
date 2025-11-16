/**
 * API Client for Gaming Platform
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  ApiResponse,
  AuthResponse,
  LoginCredentials,
  RegisterData,
  User,
  Wallet,
  Transaction,
  Game,
  GameSession,
  CreateSessionRequest,
  JoinSessionRequest,
  Achievement,
  LeaderboardEntry,
  DailyBonus,
  KYCDocument,
  DepositRequest,
  WithdrawalRequest
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE_PATH = process.env.NEXT_PUBLIC_API_BASE_PATH || '/api/v1';
const BASE_URL = `${API_URL}${API_BASE_PATH}`;

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
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

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
  }

  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.client.post<ApiResponse<AuthResponse>>('/auth/login', credentials);
    return response.data.data;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.client.post<ApiResponse<AuthResponse>>('/auth/register', data);
    return response.data.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<ApiResponse<{ user: User }>>('/auth/me');
    return response.data.data.user;
  }

  async logout(): Promise<void> {
    this.clearToken();
  }

  // User
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await this.client.put<ApiResponse<User>>('/users/profile', data);
    return response.data.data;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.client.post('/users/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  // Wallet
  async getWallets(): Promise<Wallet[]> {
    const response = await this.client.get<ApiResponse<{ wallets: Wallet[] }>>('/wallet/balance');
    return response.data.data.wallets;
  }

  async deposit(data: DepositRequest): Promise<any> {
    const response = await this.client.post<ApiResponse>('/wallet/deposit', data);
    return response.data.data;
  }

  async withdraw(data: WithdrawalRequest): Promise<any> {
    const response = await this.client.post<ApiResponse>('/wallet/withdraw', data);
    return response.data.data;
  }

  async getTransactions(page = 1, pageSize = 20): Promise<Transaction[]> {
    const response = await this.client.get<ApiResponse<{ transactions: Transaction[] }>>(
      `/wallet/transactions?page=${page}&page_size=${pageSize}`
    );
    return response.data.data.transactions;
  }

  // Games
  async getGameCatalog(): Promise<Game[]> {
    const response = await this.client.get<ApiResponse<{ games: Game[] }>>('/games/catalog');
    return response.data.data.games;
  }

  async getGame(gameId: string): Promise<Game> {
    const response = await this.client.get<ApiResponse<Game>>(`/games/catalog/${gameId}`);
    return response.data.data;
  }

  async getGameSessions(status?: string): Promise<GameSession[]> {
    const url = status ? `/games/sessions?status=${status}` : '/games/sessions';
    const response = await this.client.get<ApiResponse<{ sessions: GameSession[] }>>(url);
    return response.data.data.sessions;
  }

  async getGameSession(sessionId: string): Promise<any> {
    const response = await this.client.get<ApiResponse>(`/games/sessions/${sessionId}`);
    return response.data.data;
  }

  async createGameSession(data: CreateSessionRequest): Promise<any> {
    const response = await this.client.post<ApiResponse>('/games/sessions/create', data);
    return response.data.data;
  }

  async joinGameSession(data: JoinSessionRequest): Promise<any> {
    const response = await this.client.post<ApiResponse>('/games/sessions/join', data);
    return response.data.data;
  }

  async getGameDashboard(): Promise<any> {
    const response = await this.client.get<ApiResponse>('/games/dashboard');
    return response.data.data;
  }

  // Achievements
  async getAchievements(): Promise<Achievement[]> {
    const response = await this.client.get<ApiResponse<{ achievements: Achievement[] }>>('/rewards/achievements');
    return response.data.data.achievements;
  }

  async claimAchievement(achievementId: string): Promise<any> {
    const response = await this.client.post<ApiResponse>(`/rewards/achievements/${achievementId}/claim`);
    return response.data.data;
  }

  // Leaderboard
  async getLeaderboard(period = 'all_time', limit = 100): Promise<LeaderboardEntry[]> {
    const response = await this.client.get<ApiResponse<{ leaderboard: LeaderboardEntry[] }>>(
      `/rewards/leaderboard?period=${period}&limit=${limit}`
    );
    return response.data.data.leaderboard;
  }

  async getMyRank(): Promise<any> {
    const response = await this.client.get<ApiResponse>('/rewards/leaderboard/my-rank');
    return response.data.data;
  }

  // Daily Bonus
  async getDailyBonusStatus(): Promise<any> {
    const response = await this.client.get<ApiResponse>('/rewards/daily-bonus/status');
    return response.data.data;
  }

  async claimDailyBonus(): Promise<DailyBonus> {
    const response = await this.client.post<ApiResponse<DailyBonus>>('/rewards/daily-bonus/claim');
    return response.data.data;
  }

  // Referrals
  async getReferralStats(): Promise<any> {
    const response = await this.client.get<ApiResponse>('/rewards/referrals/stats');
    return response.data.data;
  }

  async getReferrals(): Promise<any> {
    const response = await this.client.get<ApiResponse>('/rewards/referrals');
    return response.data.data;
  }

  // KYC
  async getKYCDocuments(): Promise<KYCDocument[]> {
    const response = await this.client.get<ApiResponse<{ documents: KYCDocument[] }>>('/kyc/documents');
    return response.data.data.documents;
  }

  async uploadKYCDocument(formData: FormData): Promise<KYCDocument> {
    const response = await this.client.post<ApiResponse<KYCDocument>>('/kyc/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data;
  }

  async getKYCStatus(): Promise<any> {
    const response = await this.client.get<ApiResponse>('/kyc/status');
    return response.data.data;
  }
}

export const api = new ApiClient();
export default api;
