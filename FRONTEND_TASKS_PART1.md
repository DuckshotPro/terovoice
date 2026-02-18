# Frontend Integration Task List - Part 1: Overview & Setup

## System Status
✅ Backend: **FUNCTIONAL** (LiveKit + Agent + Analytics)
✅ Inference: **FUNCTIONAL** (Hugging Face VPS)
✅ Database: **FUNCTIONAL** (PostgreSQL on IONOS)
⏳ Frontend: **TODO** (React/Vite - this workspace)

## Frontend Scope

Your React app needs:
1. **Public Pages** (no auth required)
   - Landing page (hero, features, pricing)
   - About page
   - Pricing page
   - Blog/Resources

2. **Auth Pages** (OAuth + email)
   - Login (Google/GitHub OAuth)
   - Signup
   - Email verification
   - Password reset

3. **Dashboard Pages** (auth required)
   - Client dashboard (real-time stats)
   - Call logs & transcripts
   - Settings (phone number, profession, voice)
   - Billing & subscription
   - Account management

4. **Admin Pages** (admin only)
   - All clients list
   - Revenue dashboard
   - System health
   - User management

## Tech Stack (Your Current Setup)

```
Frontend: React 18.2.0 + Vite 4.4.5
Styling: Tailwind CSS 3.3.3
Routing: React Router DOM 6.14.0
Icons: Lucide React 0.263.1
Auth: NextAuth.js or Auth0
Payments: PayPal SDK
Database: PostgreSQL (on IONOS VPS)
API: REST (to your IONOS backend)
```

## Database Schema (PostgreSQL)

You need these tables:

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  oauth_provider VARCHAR,
  oauth_id VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Subscriptions
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  plan VARCHAR (solo/pro/white-label),
  status VARCHAR (active/cancelled/expired),
  paypal_subscription_id VARCHAR,
  amount DECIMAL,
  billing_cycle_start TIMESTAMP,
  billing_cycle_end TIMESTAMP,
  created_at TIMESTAMP
);

-- Clients (AI Receptionist instances)
CREATE TABLE clients (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR,
  phone_number VARCHAR,
  profession VARCHAR,
  voice_id VARCHAR,
  sip_username VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Call Analytics
CREATE TABLE calls (
  id UUID PRIMARY KEY,
  client_id UUID REFERENCES clients(id),
  duration DECIMAL,
  transcript TEXT,
  sentiment VARCHAR,
  success BOOLEAN,
  revenue_value DECIMAL,
  created_at TIMESTAMP
);

-- Invoices
CREATE TABLE invoices (
  id UUID PRIMARY KEY,
  subscription_id UUID REFERENCES subscriptions(id),
  amount DECIMAL,
  status VARCHAR (paid/pending/failed),
  paypal_invoice_id VARCHAR,
  due_date TIMESTAMP,
  paid_date TIMESTAMP,
  created_at TIMESTAMP
);
```

## API Endpoints Needed

Your React app will call these backend endpoints:

```
Auth:
POST   /api/auth/login              - OAuth login
POST   /api/auth/logout             - Logout
GET    /api/auth/me                 - Current user
POST   /api/auth/refresh            - Refresh token

Users:
GET    /api/users/profile           - Get user profile
PUT    /api/users/profile           - Update profile
DELETE /api/users/account           - Delete account

Subscriptions:
GET    /api/subscriptions/current   - Get current subscription
POST   /api/subscriptions/create    - Create subscription
POST   /api/subscriptions/cancel    - Cancel subscription
GET    /api/subscriptions/plans     - Get available plans

Clients:
GET    /api/clients                 - List user's clients
POST   /api/clients                 - Create new client
GET    /api/clients/:id             - Get client details
PUT    /api/clients/:id             - Update client
DELETE /api/clients/:id             - Delete client

Analytics:
GET    /api/clients/:id/stats       - Get client stats
GET    /api/clients/:id/calls       - Get call logs
GET    /api/clients/:id/revenue     - Get revenue data

Billing:
GET    /api/invoices                - List invoices
GET    /api/invoices/:id            - Get invoice details
POST   /api/billing/webhook         - PayPal webhook
```

## Integration Points

### 1. Backend Connection
- Your React app → IONOS VPS (REST API)
- IONOS VPS → PostgreSQL (user/billing data)
- IONOS VPS → Hugging Face (inference)
- IONOS VPS → LiveKit (call handling)

### 2. OAuth Integration
- Google OAuth (easiest)
- GitHub OAuth (optional)
- Email/password fallback

### 3. PayPal Integration
- Subscription creation
- Webhook handling
- Invoice generation

### 4. Real-time Updates
- WebSocket to dashboard for live call stats
- Or polling every 5 seconds

## File Structure (Frontend)

```
src/
├── pages/
│   ├── public/
│   │   ├── Home.jsx
│   │   ├── About.jsx
│   │   ├── Pricing.jsx
│   │   └── Blog.jsx
│   ├── auth/
│   │   ├── Login.jsx
│   │   ├── Signup.jsx
│   │   ├── OAuthCallback.jsx
│   │   └── PasswordReset.jsx
│   └── dashboard/
│       ├── Dashboard.jsx
│       ├── Clients.jsx
│       ├── CallLogs.jsx
│       ├── Settings.jsx
│       ├── Billing.jsx
│       └── Account.jsx
├── components/
│   ├── auth/
│   │   ├── ProtectedRoute.jsx
│   │   ├── LoginForm.jsx
│   │   └── OAuthButtons.jsx
│   ├── dashboard/
│   │   ├── StatsCard.jsx
│   │   ├── CallTable.jsx
│   │   ├── RevenueChart.jsx
│   │   └── ClientForm.jsx
│   └── billing/
│       ├── PricingCard.jsx
│       ├── SubscriptionForm.jsx
│       └── InvoiceList.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useUser.js
│   ├── useClients.js
│   └── useSubscription.js
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── clients.js
│   ├── billing.js
│   └── analytics.js
├── context/
│   ├── AuthContext.jsx
│   └── UserContext.jsx
├── utils/
│   ├── constants.js
│   ├── formatters.js
│   └── validators.js
└── App.jsx
```

## Dependencies to Add

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.0",
    "axios": "^1.4.0",
    "next-auth": "^4.22.0",
    "@paypal/checkout-server-sdk": "^1.0.2",
    "@paypal/paypal-js": "^5.1.0",
    "zustand": "^4.3.9",
    "react-query": "^3.39.3",
    "socket.io-client": "^4.5.4",
    "date-fns": "^2.30.0",
    "recharts": "^2.7.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "tailwindcss": "^3.3.3",
    "postcss": "^8.4.24",
    "autoprefixer": "^10.4.14"
  }
}
```

## Next: See FRONTEND_TASKS_PART2.md for detailed task breakdown
