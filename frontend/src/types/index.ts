// User types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  bio: string;
  location: string;
  avatar?: string;
  is_profile_public: boolean;
  created_at: string;
}

export interface UserProfile {
  user: User;
  reading_preferences: Record<string, unknown>;
  favorite_genres: string[];
  reading_goals: Record<string, unknown>;
  website?: string;
  twitter?: string;
  instagram?: string;
  goodreads?: string;
}

// Authentication types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  confirm_password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Book types
export interface Author {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
}

export interface Genre {
  id: number;
  name: string;
  description?: string;
}

export interface Publisher {
  id: number;
  name: string;
  description?: string;
}

export interface Book {
  id: number;
  title: string;
  subtitle?: string;
  authors: Author[];
  author_names: string;
  isbn_10?: string;
  isbn_13?: string;
  publisher?: Publisher;
  publication_date?: string;
  edition?: string;
  language: string;
  pages?: number;
  format?: string;
  description?: string;
  genres: Genre[];
  cover_image?: string;
  created_at: string;
  updated_at: string;
}

export interface UserBook {
  id: number;
  user: User;
  book: Book;
  status: 'owned' | 'reading' | 'read' | 'want_to_read' | 'available' | 'lent_out' | 'exchanged';
  condition: 'new' | 'like_new' | 'very_good' | 'good' | 'acceptable' | 'poor';
  notes?: string;
  rating?: number;
  review?: string;
  available_for_exchange: boolean;
  exchange_type: 'permanent' | 'temporary' | 'both';
  current_page: number;
  date_started?: string;
  date_finished?: string;
  added_at: string;
  updated_at: string;
}

// Friendship types
export interface Friendship {
  id: number;
  user1: User;
  user2: User;
  status: 'pending' | 'accepted' | 'declined' | 'blocked';
  initiated_by: User;
  message?: string;
  created_at: string;
  updated_at: string;
  accepted_at?: string;
}

// Exchange types
export interface BookExchange {
  id: number;
  requester: User;
  owner: User;
  requested_book: UserBook;
  offered_book?: UserBook;
  exchange_type: 'permanent' | 'temporary';
  status: 'requested' | 'accepted' | 'declined' | 'cancelled' | 'in_transit' | 'completed' | 'returned';
  message?: string;
  loan_duration_days?: number;
  return_by_date?: string;
  meeting_location?: string;
  meeting_date?: string;
  created_at: string;
  updated_at: string;
}

// Message types
export interface PrivateMessage {
  id: number;
  sender: User;
  recipient: User;
  content: string;
  subject?: string;
  is_read: boolean;
  related_book?: Book;
  reply_to?: PrivateMessage;
  created_at: string;
  read_at?: string;
}

export interface BookDiscussion {
  id: number;
  book: Book;
  title: string;
  description?: string;
  creator: User;
  is_public: boolean;
  is_archived: boolean;
  allow_comments: boolean;
  is_pinned: boolean;
  is_locked: boolean;
  views_count: number;
  participants_count: number;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  error: string;
  details?: Record<string, string[]>;
  status: number;
}

// UI types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

// Search types
export interface SearchFilters {
  query?: string;
  genre?: string;
  author?: string;
  status?: string;
  available_for_exchange?: boolean;
  location?: string;
  distance?: number;
} 