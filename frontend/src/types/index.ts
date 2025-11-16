// Core Types for Gaming Platform Frontend

export interface User {
  id: string;
  username: string;
  email: string;
  phone: string;
  display_name?: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
  kyc_status: 'pending' | 'approved' | 'rejected' | 'not_submitted';
  referral_code: string;
  created_at: string;
  total_games_played: number;
  total_winnings: number;
  level: number;
  xp: number;
}

export interface Wallet {
  id: string;
  user_id: string;
  wallet_type: 'cash' | 'bonus' | 'winnings';
  balance: number;
  updated_at: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  transaction_type: 'deposit' | 'withdrawal' | 'game_entry' | 'game_win' | 'refund' | 'bonus' | 'referral';
  amount: number;
  status: 'pending' | 'completed' | 'failed' | 'cancelled';
  payment_method?: string;
  payment_id?: string;
  description: string;
  created_at: string;
}

export interface Game {
  id: string;
  code: string;
  name: string;
  description: string;
  thumbnail_url?: string;
  min_players: number;
  max_players: number;
  min_entry_fee: number;
  max_entry_fee: number;
  is_active: boolean;
  category: string;
  rules?: any;
}

export interface GameSession {
  id: string;
  game_id: string;
  session_code: string;
  entry_fee: number;
  prize_pool: number;
  max_players: number;
  current_players: number;
  status: 'waiting' | 'in_progress' | 'completed' | 'cancelled';
  is_private: boolean;
  created_by: string;
  started_at?: string;
  completed_at?: string;
}

export interface GameParticipant {
  id: string;
  session_id: string;
  user_id: string;
  username: string;
  position?: number;
  prize_amount?: number;
  joined_at: string;
}

export interface Achievement {
  id: string;
  code: string;
  name: string;
  description: string;
  icon_url?: string;
  xp_reward: number;
  bonus_reward: number;
  requirement: any;
  category: string;
}

export interface UserAchievement {
  id: string;
  user_id: string;
  achievement_id: string;
  progress: number;
  is_claimed: boolean;
  claimed_at?: string;
  created_at: string;
}

export interface Referral {
  id: string;
  referrer_id: string;
  referred_id: string;
  referral_code: string;
  status: 'pending' | 'active' | 'rewarded';
  bonus_amount: number;
  created_at: string;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  avatar_url?: string;
  score: number;
  games_played: number;
  win_rate: number;
}

export interface DailyBonus {
  id: string;
  user_id: string;
  day_number: number;
  bonus_amount: number;
  claimed_at: string;
}

export interface KYCDocument {
  id: string;
  user_id: string;
  document_type: 'aadhaar' | 'pan' | 'driving_license' | 'passport';
  document_number: string;
  document_url: string;
  status: 'pending' | 'verified' | 'rejected';
  verified_at?: string;
  rejection_reason?: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Auth Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  phone: string;
  password: string;
  display_name?: string;
  referral_code?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Form Types
export interface DepositRequest {
  amount: number;
  payment_method: 'upi' | 'card' | 'netbanking';
}

export interface WithdrawalRequest {
  amount: number;
  wallet_type: 'cash' | 'winnings';
}

export interface CreateSessionRequest {
  game_id: string;
  entry_fee: number;
  session_type: 'public' | 'private';
  max_players: number;
  is_private?: boolean;
}

export interface JoinSessionRequest {
  session_code: string;
}

// State Types
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

export interface WalletState {
  wallets: Wallet[];
  isLoading: boolean;
  fetchWallets: () => Promise<void>;
  getTotalBalance: () => number;
  getWalletByType: (type: string) => Wallet | undefined;
}
