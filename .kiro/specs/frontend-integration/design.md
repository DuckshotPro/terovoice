# Frontend Integration Design

## Overview

The frontend is a React 18 single-page application (SPA) that provides a complete user interface for the AI Receptionist SaaS platform. It communicates with the backend API via REST endpoints and WebSocket for real-time updates. The application uses Vite for fast development and optimized builds, Tailwind CSS for styling, and Context API for state management.

**Key Design Principles:**
- Mobile-first responsive design
- Progressive enhancement (works without JavaScript)
- Accessibility (WCAG 2.1 AA compliance)
- Performance optimization (lazy loading, code splitting)
- Security by default (HTTPS, CSRF protection, XSS prevention)
- Real-time updates via WebSocket

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Pages (Login, Dashboard, Clients, Analytics, etc.)  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Components (Forms, Tables, Charts, etc.)            │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Hooks (useAuth, useClients, useApi, etc.)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Services (API client, Auth service, etc.)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Context (AuthContext, UserContext, etc.)            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
              ↓ HTTPS                    ↓ WebSocket
┌─────────────────────────────────────────────────────────────┐
│              Backend API (Flask)                             │
│  - REST endpoints for CRUD operations                       │
│  - WebSocket for real-time updates                          │
│  - JWT authentication                                       │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
App
├── Router
│   ├── PublicLayout
│   │   ├── Home
│   │   ├── Pricing
│   │   ├── About
│   │   ├── Login
│   │   └── Signup
│   └── ProtectedLayout
│       ├── Dashboard
│       │   ├── StatsCard
│       │   ├── CallChart
│       │   ├── SentimentChart
│       │   └── RecentCalls
│       ├── Clients
│       │   ├── ClientList
│       │   ├── ClientForm
│       │   └── ClientDetails
│       ├── CallLogs
│       │   ├── CallTable
│       │   ├── CallFilters
│       │   └── CallDetails
│       ├── Analytics
│       │   ├── TrendChart
│       │   ├── SentimentChart
│       │   └── ClientStats
│       ├── Billing
│       │   ├── SubscriptionCard
│       │   ├── InvoiceList
│       │   └── UpgradeForm
│       └── Settings
│           ├── ProfileForm
│           ├── SecuritySettings
│           ├── NotificationPreferences
│           └── APIKeys
```

## Components and Interfaces

### Core Components

#### 1. Authentication Components

**LoginForm.jsx**
```jsx
Props:
  - onSubmit: (email, password) => Promise<void>
  - isLoading: boolean
  - error: string | null

State:
  - email: string
  - password: string
  - showPassword: boolean
```

**SignupForm.jsx**
```jsx
Props:
  - onSubmit: (email, password, name) => Promise<void>
  - isLoading: boolean
  - error: string | null

State:
  - email: string
  - password: string
  - confirmPassword: string
  - name: string
```

**OAuthButtons.jsx**
```jsx
Props:
  - onGoogleClick: () => void
  - onGithubClick: () => void
  - isLoading: boolean
```

**ProtectedRoute.jsx**
```jsx
Props:
  - children: ReactNode
  - requiredRole?: string

Behavior:
  - Redirects to login if not authenticated
  - Checks authorization if role required
```

#### 2. Dashboard Components

**StatsCard.jsx**
```jsx
Props:
  - title: string
  - value: number | string
  - icon: ReactNode
  - trend?: number
  - unit?: string
```

**CallChart.jsx**
```jsx
Props:
  - data: Array<{ date: string, calls: number }>
  - loading: boolean
```

**SentimentChart.jsx**
```jsx
Props:
  - data: { positive: number, negative: number, neutral: number }
  - loading: boolean
```

**RecentCalls.jsx**
```jsx
Props:
  - calls: Array<Call>
  - loading: boolean
  - onCallClick: (call: Call) => void
```

#### 3. Client Management Components

**ClientList.jsx**
```jsx
Props:
  - clients: Array<Client>
  - loading: boolean
  - onEdit: (client: Client) => void
  - onDelete: (clientId: string) => void
  - onCreate: () => void
```

**ClientForm.jsx**
```jsx
Props:
  - client?: Client
  - onSubmit: (data: ClientFormData) => Promise<void>
  - isLoading: boolean
  - error: string | null
```

**ClientDetails.jsx**
```jsx
Props:
  - client: Client
  - calls: Array<Call>
  - stats: ClientStats
  - loading: boolean
```

#### 4. Analytics Components

**CallTable.jsx**
```jsx
Props:
  - calls: Array<Call>
  - loading: boolean
  - pagination: Pagination
  - onPageChange: (page: number) => void
  - onRowClick: (call: Call) => void
```

**CallFilters.jsx**
```jsx
Props:
  - onFilterChange: (filters: CallFilters) => void
  - loading: boolean
```

**CallDetails.jsx**
```jsx
Props:
  - call: Call
  - onClose: () => void
```

#### 5. Billing Components

**PricingCard.jsx**
```jsx
Props:
  - plan: Plan
  - isCurrentPlan: boolean
  - onSubscribe: (planId: string) => void
  - isLoading: boolean
```

**SubscriptionCard.jsx**
```jsx
Props:
  - subscription: Subscription
  - onUpgrade: () => void
  - onDowngrade: () => void
  - onCancel: () => void
```

**InvoiceList.jsx**
```jsx
Props:
  - invoices: Array<Invoice>
  - loading: boolean
  - onDownload: (invoiceId: string) => void
```

### Data Models

```typescript
// User
interface User {
  id: string
  email: string
  name: string
  oauthProvider?: string
  createdAt: string
  updatedAt: string
}

// Client
interface Client {
  id: string
  userId: string
  name: string
  phoneNumber: string
  profession: string
  voiceName: string
  status: 'active' | 'inactive'
  createdAt: string
  updatedAt: string
}

// Call
interface Call {
  id: string
  clientId: string
  phoneNumber: string
  duration: number
  transcript: string
  sentiment: 'positive' | 'negative' | 'neutral'
  recordingUrl?: string
  status: 'completed' | 'failed' | 'missed'
  createdAt: string
}

// Subscription
interface Subscription {
  id: string
  userId: string
  planId: string
  status: 'active' | 'cancelled' | 'expired'
  paypalSubscriptionId: string
  renewalDate: string
  createdAt: string
}

// Plan
interface Plan {
  id: string
  name: string
  price: number
  minutesPerMonth: number
  features: string[]
}

// Invoice
interface Invoice {
  id: string
  subscriptionId: string
  amount: number
  status: 'paid' | 'pending' | 'failed'
  dueDate: string
  paidDate?: string
  createdAt: string
}
```

## Data Models

### Database Schema (PostgreSQL)

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR,
  name VARCHAR,
  oauth_provider VARCHAR,
  oauth_id VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Clients table
CREATE TABLE clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR NOT NULL,
  phone_number VARCHAR UNIQUE NOT NULL,
  profession VARCHAR,
  voice_name VARCHAR,
  status VARCHAR DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Calls table
CREATE TABLE calls (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
  phone_number VARCHAR,
  duration INTEGER,
  transcript TEXT,
  sentiment VARCHAR,
  recording_url VARCHAR,
  status VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions table
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id VARCHAR,
  status VARCHAR,
  paypal_subscription_id VARCHAR,
  renewal_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Invoices table
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID REFERENCES subscriptions(id),
  amount DECIMAL(10, 2),
  status VARCHAR,
  due_date TIMESTAMP,
  paid_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- API Keys table
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  key_hash VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  last_used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### State Management (Context API)

```typescript
// AuthContext
interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

// UserContext
interface UserContextType {
  user: User | null
  subscription: Subscription | null
  isLoading: boolean
  updateProfile: (data: Partial<User>) => Promise<void>
  updateSubscription: (subscriptionId: string) => Promise<void>
}

// ClientsContext
interface ClientsContextType {
  clients: Client[]
  isLoading: boolean
  error: string | null
  fetchClients: () => Promise<void>
  createClient: (data: ClientFormData) => Promise<Client>
  updateClient: (id: string, data: Partial<Client>) => Promise<void>
  deleteClient: (id: string) => Promise<void>
}
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Authentication State Persistence
**For any** user session, if a valid JWT token exists in localStorage, refreshing the page should restore the authenticated state without requiring re-login.
**Validates: Requirements 1.8**

### Property 2: Protected Route Access Control
**For any** protected route and any unauthenticated user, attempting to access the route should redirect to the login page.
**Validates: Requirements 1.10**

### Property 3: Form Validation Consistency
**For any** form submission with invalid data, the system should display validation errors and prevent submission.
**Validates: Requirements 8.1**

### Property 4: Client Isolation
**For any** user, they should only be able to view and modify their own clients, not clients belonging to other users.
**Validates: Requirements 4.1, 11.6**

### Property 5: Real-time Dashboard Updates
**For any** new call received, the dashboard should update within 2 seconds without requiring a page refresh.
**Validates: Requirements 3.5, 12.1**

### Property 6: Subscription Status Accuracy
**For any** active subscription, the system should display the correct plan name, renewal date, and remaining minutes.
**Validates: Requirements 6.4**

### Property 7: API Request Authorization
**For any** API request, the system should include a valid JWT token in the Authorization header.
**Validates: Requirements 11.3**

### Property 8: Error Message Clarity
**For any** API error response, the system should display a user-friendly error message (not raw error codes).
**Validates: Requirements 8.2**

### Property 9: Session Expiration Handling
**For any** expired JWT token, the system should redirect to login and display a session expired message.
**Validates: Requirements 1.9**

### Property 10: Responsive Layout Adaptation
**For any** screen size (mobile, tablet, desktop), the application should display a responsive layout optimized for that size.
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 11: Data Sanitization
**For any** user input in forms, the system should sanitize and validate input to prevent XSS attacks.
**Validates: Requirements 11.7**

### Property 12: WebSocket Reconnection
**For any** lost WebSocket connection, the system should attempt to reconnect automatically and sync missed updates.
**Validates: Requirements 12.6, 12.7**

## Error Handling

### API Error Handling

```typescript
// Error types
enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

// Error response
interface ApiError {
  type: ErrorType
  message: string
  details?: Record<string, string>
  statusCode: number
}

// Error handling strategy
- Network errors: Display "Connection error" with retry button
- 401 Unauthorized: Redirect to login
- 403 Forbidden: Display "Permission denied"
- 404 Not Found: Display "Resource not found"
- 422 Validation Error: Display field-level errors
- 5xx Server Error: Display "Server error" with error ID for support
- Unknown Error: Display generic error message
```

### Form Validation

```typescript
// Validation rules
- Email: Valid email format
- Password: Minimum 8 characters, at least one uppercase, one lowercase, one number
- Name: Non-empty, max 100 characters
- Phone: Valid E.164 format
- URL: Valid URL format

// Validation timing
- On blur: Validate field when user leaves it
- On submit: Validate all fields before submission
- Real-time: Show validation status as user types
```

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Test hooks with mock API responses
- Test utility functions
- Target: 80%+ coverage

### Integration Tests
- Test component interactions
- Test API integration
- Test authentication flow
- Test client management flow
- Test billing flow

### End-to-End Tests
- Test complete user journeys
- Test signup → login → create client → view analytics
- Test subscription flow
- Test error scenarios

### Property-Based Tests
- Test authentication state persistence across page refreshes
- Test protected route access control
- Test form validation consistency
- Test client isolation
- Test real-time updates
- Test subscription status accuracy
- Test API request authorization
- Test error message clarity
- Test session expiration handling
- Test responsive layout adaptation
- Test data sanitization
- Test WebSocket reconnection

## Performance Optimization

### Code Splitting
- Lazy load pages (Dashboard, Clients, Analytics, Billing, Settings)
- Lazy load heavy components (Charts, Tables)
- Lazy load third-party libraries (PayPal SDK, OAuth libraries)

### Bundle Optimization
- Minify and compress JavaScript
- Tree-shake unused code
- Use dynamic imports for large dependencies
- Target bundle size: <500KB gzipped

### Runtime Optimization
- Implement pagination for large lists
- Use virtual scrolling for long tables
- Debounce search input
- Memoize expensive computations
- Use React.memo for expensive components

### Network Optimization
- Implement request caching
- Use HTTP/2 server push
- Compress API responses
- Implement request batching

## Security Implementation

### Authentication
- Use JWT tokens with 24-hour expiration
- Store tokens in httpOnly cookies (not localStorage)
- Implement token refresh mechanism
- Validate tokens on every API request

### Authorization
- Check user permissions on frontend (UX)
- Verify permissions on backend (security)
- Implement role-based access control
- Prevent direct URL access to protected pages

### Data Protection
- Use HTTPS for all communication
- Sanitize user input to prevent XSS
- Implement CSRF protection
- Mask sensitive data (API keys, phone numbers)
- Clear sensitive data on logout

### API Security
- Validate all input on backend
- Implement rate limiting
- Use CORS to restrict origins
- Implement request signing for sensitive operations
