/**
 * Admin Panel TypeScript Definitions
 */

// Admin User
export interface AdminUser {
  id: string;
  username: string;
  email: string;
  phone: string;
  display_name?: string;
  avatar_url?: string;
  role: 'admin' | 'superadmin';
  status: 'active' | 'suspended' | 'banned';
  kyc_status: 'pending' | 'verified' | 'rejected';
  is_email_verified: boolean;
  is_phone_verified: boolean;
  referral_code: string;
  created_at: string;
  last_login_at?: string;
}

// Dashboard Statistics
export interface DashboardStats {
  users: {
    total: number;
    active: number;
    new_today: number;
    suspended: number;
  };
  kyc: {
    pending: number;
    approved: number;
  };
  withdrawals: {
    pending_count: number;
    pending_amount: number;
  };
  transactions: {
    deposits_today: number;
    withdrawals_today: number;
    revenue_total: number;
  };
  sessions: {
    active: number;
  };
}

// User Management
export interface PlatformUser {
  id: string;
  username: string;
  email: string;
  phone: string;
  display_name?: string;
  role: 'user' | 'admin' | 'superadmin';
  status: 'active' | 'suspended' | 'banned';
  kyc_status: 'pending' | 'verified' | 'rejected';
  is_email_verified: boolean;
  is_phone_verified: boolean;
  total_balance: number;
  games_played: number;
  total_winnings: number;
  created_at: string;
  last_login_at?: string;
}

export interface UserDetails {
  user: {
    id: string;
    username: string;
    email: string;
    phone: string;
    display_name?: string;
    avatar_url?: string;
    date_of_birth?: string;
    role: string;
    status: string;
    kyc_status: string;
    is_email_verified: boolean;
    is_phone_verified: boolean;
    referral_code: string;
    created_at: string;
    last_login_at?: string;
  };
  statistics?: {
    total_games_played: number;
    total_games_won: number;
    total_games_lost: number;
    total_winnings: number;
    total_spent: number;
    current_level: number;
    experience_points: number;
  };
  profile?: {
    bio?: string;
    state?: string;
    city?: string;
    pincode?: string;
  };
  wallets: {
    wallet_type: string;
    balance: number;
  }[];
  recent_transactions: {
    id: string;
    type: string;
    amount: number;
    status: string;
    description: string;
    created_at: string;
  }[];
}

// KYC Management
export interface KYCDocument {
  id: string;
  user_id: string;
  document_type: string;
  document_number: string;
  full_name: string;
  date_of_birth: string;
  status: 'pending' | 'under_review' | 'approved' | 'rejected';
  document_front_url?: string;
  document_back_url?: string;
  selfie_url?: string;
  rejection_reason?: string;
  submitted_at: string;
  reviewed_at?: string;
  created_at: string;
}

export interface ReviewKYCRequest {
  kyc_id: string;
  action: 'approve' | 'reject' | 'request_resubmit';
  rejection_reason?: string;
  admin_notes?: string;
}

// Withdrawal Management
export interface WithdrawalRequest {
  id: string;
  requested_amount: number;
  tds_amount: number;
  processing_fee: number;
  final_amount: number;
  status: 'pending' | 'processing' | 'completed' | 'rejected';
  account_holder_name: string;
  account_number: string;
  ifsc_code: string;
  bank_name: string;
  utr_number?: string;
  rejection_reason?: string;
  requested_at: string;
  completed_at?: string;
}

export interface ReviewWithdrawalRequest {
  withdrawal_id: string;
  action: 'approve' | 'reject' | 'complete';
  rejection_reason?: string;
  utr_number?: string;
  admin_notes?: string;
}

// API Response Types
export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  limit: number;
  offset: number;
}

// Auth Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AdminUser;
}
