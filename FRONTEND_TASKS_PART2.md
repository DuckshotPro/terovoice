# Frontend Integration Task List - Part 2: Detailed Tasks

## Phase 1: Setup & Infrastructure (Week 1)

### 1.1 Database Setup
- [ ] Create PostgreSQL tables (see schema in PART1)
- [ ] Create migrations (Alembic or similar)
- [ ] Add indexes on frequently queried columns
- [ ] Test connection from IONOS VPS
- [ ] Backup strategy

**Files to create:**
- `backend-setup/migrations/001_initial_schema.sql`
- `backend-setup/migrations/002_add_indexes.sql`

**Commands:**
```bash
# SSH to IONOS
 root@your-ionos-ip

# Connect to PostgreSQL
psql -U postgres -h localhost -d ai_receptionist

# Run migrations
psql -U postgres -h localhost -d ai_receptionist < migrations/001_initial_schema.sql
```

### 1.2 Backend API Setup
- [ ] Create Flask API routes for auth
- [ ] Create Flask API routes for users
- [ ] Create Flask API routes for subscriptions
- [ ] Create Flask API routes for clients
- [ ] Create Flask API routes for analytics
- [ ] Add CORS headers
- [ ] Add request validation
- [ ] Add error handling

**Files to create:**
- `backend-setup/api/auth.py`
- `backend-setup/api/users.py`
- `backend-setup/api/subscriptions.py`
- `backend-setup/api/clients.py`
- `backend-setup/api/analytics.py`

### 1.3 Environment Configuration
- [ ] Add PostgreSQL connection string to .env
- [ ] Add OAuth credentials (Google/GitHub)
- [ ] Add PayPal credentials
- [ ] Add JWT secret key
- [ ] Add CORS allowed origins

**Update .env:**
```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/ai_receptionist

# OAuth
GOOGLE_CLIENT_ID=your_google_id
GOOGLE_CLIENT_SECRET=your_google_secret
GITHUB_CLIENT_ID=your_github_id
GITHUB_CLIENT_SECRET=your_github_secret

# PayPal
PAYPAL_CLIENT_ID=your_paypal_id
PAYPAL_CLIENT_SECRET=your_paypal_secret
PAYPAL_MODE=sandbox  # or live

# JWT
JWT_SECRET=your_random_secret_key

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Phase 2: Authentication (Week 2)

### 2.1 OAuth Integration
- [ ] Set up Google OAuth
- [ ] Set up GitHub OAuth
- [ ] Create OAuth callback handler
- [ ] Store OAuth tokens securely
- [ ] Create user on first login

**Backend files:**
- `backend-setup/api/auth.py` - OAuth routes
- `backend-setup/services/oauth.py` - OAuth logic

**Frontend files:**
- `src/pages/auth/OAuthCallback.jsx`
- `src/components/auth/OAuthButtons.jsx`

### 2.2 JWT Token Management
- [ ] Generate JWT on login
- [ ] Store JWT in secure cookie
- [ ] Refresh token logic
- [ ] Logout (clear cookie)
- [ ] Token validation middleware

**Backend:**
```python
# backend-setup/services/jwt_service.py
def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm='HS256')
```

### 2.3 Protected Routes
- [ ] Create ProtectedRoute component
- [ ] Redirect unauthenticated users to login
- [ ] Check token validity on page load
- [ ] Handle token expiration

**Frontend:**
```jsx
// src/components/auth/ProtectedRoute.jsx
export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" />;
  
  return children;
}
```

### 2.4 Login/Signup Pages
- [ ] Create login page with OAuth buttons
- [ ] Create signup page
- [ ] Email verification flow
- [ ] Password reset flow
- [ ] Form validation

**Frontend files:**
- `src/pages/auth/Login.jsx`
- `src/pages/auth/Signup.jsx`
- `src/pages/auth/PasswordReset.jsx`

---

## Phase 3: Dashboard Pages (Week 3)

### 3.1 Main Dashboard
- [ ] Display user's subscription status
- [ ] Show total revenue this month
- [ ] Show total calls this month
- [ ] Show active clients count
- [ ] Real-time stats updates

**Frontend:**
- `src/pages/dashboard/Dashboard.jsx`
- `src/components/dashboard/StatsCard.jsx`

### 3.2 Clients Management
- [ ] List all user's clients
- [ ] Create new client form
- [ ] Edit client settings
- [ ] Delete client
- [ ] Assign phone number
- [ ] Select profession
- [ ] Upload voice sample

**Frontend:**
- `src/pages/dashboard/Clients.jsx`
- `src/components/dashboard/ClientForm.jsx`
- `src/components/dashboard/ClientTable.jsx`

### 3.3 Call Logs & Analytics
- [ ] Display recent calls
- [ ] Filter by date range
- [ ] Search by caller name
- [ ] View call transcript
- [ ] Show call duration
- [ ] Show sentiment analysis
- [ ] Export to CSV

**Frontend:**
- `src/pages/dashboard/CallLogs.jsx`
- `src/components/dashboard/CallTable.jsx`
- `src/components/dashboard/CallDetail.jsx`

### 3.4 Settings Page
- [ ] Update profile info
- [ ] Change password
- [ ] Update email
- [ ] Manage phone numbers
- [ ] Select profession
- [ ] Upload voice sample

**Frontend:**
- `src/pages/dashboard/Settings.jsx`
- `src/components/dashboard/ProfileForm.jsx`

---

## Phase 4: Billing & PayPal (Week 4)

### 4.1 Pricing Page
- [ ] Display 3 pricing tiers
- [ ] Show features per tier
- [ ] "Choose Plan" buttons
- [ ] FAQ section

**Frontend:**
- `src/pages/public/Pricing.jsx`
- `src/components/billing/PricingCard.jsx`

### 4.2 PayPal Integration
- [ ] Create PayPal subscription
- [ ] Handle PayPal approval
- [ ] Store subscription ID in DB
- [ ] Webhook for payment updates
- [ ] Cancel subscription

**Backend:**
```python
# backend-setup/services/paypal_service.py
def create_subscription(user_id, plan):
    # Create PayPal subscription
    # Store in database
    # Return approval URL
```

**Frontend:**
- `src/components/billing/SubscriptionForm.jsx`
- `src/pages/dashboard/Billing.jsx`

### 4.3 Billing Dashboard
- [ ] Show current subscription
- [ ] Show next billing date
- [ ] Show payment history
- [ ] Download invoices
- [ ] Cancel subscription button
- [ ] Upgrade/downgrade plan

**Frontend:**
- `src/pages/dashboard/Billing.jsx`
- `src/components/billing/InvoiceList.jsx`

### 4.4 Webhook Handling
- [ ] PayPal webhook endpoint
- [ ] Update subscription status
- [ ] Send confirmation email
- [ ] Handle failed payments
- [ ] Retry logic

**Backend:**
- `backend-setup/api/webhooks.py`

---

## Phase 5: Integration & Testing (Week 5)

### 5.1 API Integration
- [ ] Connect frontend to backend API
- [ ] Handle API errors
- [ ] Loading states
- [ ] Error messages
- [ ] Success notifications

**Frontend:**
- `src/services/api.js` - Axios instance
- `src/hooks/useApi.js` - Custom hook

### 5.2 Real-time Updates
- [ ] WebSocket connection to dashboard
- [ ] Live call stats
- [ ] Live revenue counter
- [ ] Auto-refresh analytics

**Frontend:**
```jsx
// src/hooks/useRealtimeStats.js
export function useRealtimeStats(clientId) {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    const socket = io(process.env.REACT_APP_API_URL);
    socket.on('stats_update', setStats);
    return () => socket.disconnect();
  }, []);
  
  return stats;
}
```

### 5.3 Testing
- [ ] Unit tests for components
- [ ] Integration tests for API calls
- [ ] E2E tests for user flows
- [ ] Test OAuth flow
- [ ] Test PayPal flow
- [ ] Test protected routes

**Test files:**
- `src/__tests__/components/`
- `src/__tests__/pages/`
- `src/__tests__/services/`

### 5.4 Performance
- [ ] Code splitting
- [ ] Lazy loading pages
- [ ] Image optimization
- [ ] Bundle size analysis
- [ ] Lighthouse audit

---

## Phase 6: Deployment (Week 6)

### 6.1 Frontend Build
- [ ] Build React app
- [ ] Minify CSS/JS
- [ ] Generate source maps
- [ ] Test production build locally

**Commands:**
```bash
npm run build
npm run preview
```

### 6.2 Deploy to Production
- [ ] Deploy to Vercel or Netlify
- [ ] Or deploy to IONOS VPS
- [ ] Configure domain
- [ ] Set up SSL certificate
- [ ] Configure environment variables

### 6.3 Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Set up analytics (Mixpanel)
- [ ] Monitor API performance
- [ ] Monitor database performance
- [ ] Set up alerts

---

## Summary of Files to Create

### Backend (Python/Flask)
```
backend-setup/
├── api/
│   ├── __init__.py
│   ├── auth.py              ← OAuth, JWT
│   ├── users.py             ← User CRUD
│   ├── subscriptions.py      ← Subscription management
│   ├── clients.py           ← Client CRUD
│   ├── analytics.py         ← Call stats
│   └── webhooks.py          ← PayPal webhooks
├── services/
│   ├── oauth.py             ← OAuth logic
│   ├── jwt_service.py       ← JWT tokens
│   ├── paypal_service.py    ← PayPal API
│   └── email_service.py     ← Email sending
├── models/
│   ├── user.py
│   ├── subscription.py
│   ├── client.py
│   ├── call.py
│   └── invoice.py
├── migrations/
│   ├── 001_initial_schema.sql
│   └── 002_add_indexes.sql
└── requirements.txt         ← Add: sqlalchemy, psycopg2, paypalrestsdk
```

### Frontend (React)
```
src/
├── pages/
│   ├── public/
│   │   ├── Home.jsx
│   │   ├── Pricing.jsx
│   │   └── About.jsx
│   ├── auth/
│   │   ├── Login.jsx
│   │   ├── Signup.jsx
│   │   └── OAuthCallback.jsx
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
│   │   ├── ClientForm.jsx
│   │   ├── CallTable.jsx
│   │   └── RevenueChart.jsx
│   └── billing/
│       ├── PricingCard.jsx
│       ├── SubscriptionForm.jsx
│       └── InvoiceList.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useUser.js
│   ├── useClients.js
│   ├── useRealtimeStats.js
│   └── useApi.js
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── clients.js
│   ├── billing.js
│   └── analytics.js
├── context/
│   ├── AuthContext.jsx
│   └── UserContext.jsx
└── App.jsx
```

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Setup | 3-4 days | ⏳ TODO |
| Phase 2: Auth | 3-4 days | ⏳ TODO |
| Phase 3: Dashboard | 5-7 days | ⏳ TODO |
| Phase 4: Billing | 4-5 days | ⏳ TODO |
| Phase 5: Integration | 3-4 days | ⏳ TODO |
| Phase 6: Deployment | 2-3 days | ⏳ TODO |
| **Total** | **3-4 weeks** | |

---

## Next: See FRONTEND_TASKS_PART3.md for VPS connection guide
