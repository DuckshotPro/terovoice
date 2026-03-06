# START HERE - Frontend Integration Quick Start

## Your Current Status

✅ **Backend is FUNCTIONAL**
- LiveKit server running
- Agent worker processing calls
- Analytics logging
- Hugging Face inference working
- PostgreSQL on IONOS

❌ **Frontend is MISSING**
- No login/signup
- No dashboard
- No billing
- No user management

## What You Need to Build (In Order)

### Week 1: Authentication
**Goal:** Users can sign up and log in

**Files to create:**
1. `backend-setup/api/auth.py` - OAuth & JWT
2. `src/pages/auth/Login.jsx` - Login page
3. `src/pages/auth/Signup.jsx` - Signup page
4. `src/hooks/useAuth.js` - Auth hook

**Time:** 3-4 days

---

### Week 2: Dashboard
**Goal:** Users can see their clients and call stats

**Files to create:**
1. `src/pages/dashboard/Dashboard.jsx` - Main dashboard
2. `src/pages/dashboard/Clients.jsx` - Client management
3. `src/pages/dashboard/CallLogs.jsx` - Call analytics
4. `backend-setup/api/clients.py` - Client API

**Time:** 3-4 days

---

### Week 3: Billing
**Goal:** Users can subscribe with PayPal

**Files to create:**
1. `src/pages/public/Pricing.jsx` - Pricing page
2. `src/pages/dashboard/Billing.jsx` - Billing dashboard
3. `backend-setup/services/paypal_service.py` - PayPal logic
4. `backend-setup/api/webhooks.py` - PayPal webhooks

**Time:** 4-5 days

---

### Week 4: Polish & Deploy
**Goal:** Production-ready system

**Tasks:**
1. Integration testing
2. Performance optimization
3. Error handling
4. Deploy to production

**Time:** 3-4 days

---

## Quick Setup (30 minutes)

### 1. Create PostgreSQL Schema

SSH to IONOS:
```bash
ssh root@your-ionos-ip
cd ultimate-ai-receptionist

# Create schema
psql -U postgres -d ai_receptionist << 'EOF'
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  oauth_provider VARCHAR,
  oauth_id VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  plan VARCHAR,
  status VARCHAR,
  paypal_subscription_id VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name VARCHAR,
  phone_number VARCHAR,
  profession VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);
EOF
```

### 2. Add Backend API Routes

Create `backend-setup/api/auth.py`:
```python
from flask import Blueprint, request, jsonify
import jwt
from config.settings import settings

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    # TODO: Verify credentials
    # TODO: Create JWT token
    return jsonify({'token': 'jwt_token_here'})

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    # TODO: Create user
    # TODO: Create JWT token
    return jsonify({'token': 'jwt_token_here'})
```

### 3. Add Frontend Auth Hook

Create `src/hooks/useAuth.js`:
```javascript
import { useState } from 'react';
import api from '../services/api';

export function useAuth() {
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password });
    localStorage.setItem('token', res.data.token);
    setUser(res.data.user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return { user, login, logout };
}
```

### 4. Create Login Page

Create `src/pages/auth/Login.jsx`:
```jsx
import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <div className="max-w-md mx-auto mt-10">
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          className="w-full px-4 py-2 border rounded"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full px-4 py-2 border rounded"
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded"
        >
          Login
        </button>
      </form>
    </div>
  );
}
```

---

## File Checklist

### Must Create (Week 1)
- [ ] `backend-setup/api/auth.py`
- [ ] `backend-setup/services/jwt_service.py`
- [ ] `src/pages/auth/Login.jsx`
- [ ] `src/pages/auth/Signup.jsx`
- [ ] `src/hooks/useAuth.js`
- [ ] `src/services/api.js`

### Must Create (Week 2)
- [ ] `backend-setup/api/clients.py`
- [ ] `backend-setup/api/analytics.py`
- [ ] `src/pages/dashboard/Dashboard.jsx`
- [ ] `src/pages/dashboard/Clients.jsx`
- [ ] `src/pages/dashboard/CallLogs.jsx`
- [ ] `src/hooks/useClients.js`

### Must Create (Week 3)
- [ ] `src/pages/public/Pricing.jsx`
- [ ] `src/pages/dashboard/Billing.jsx`
- [ ] `backend-setup/services/paypal_service.py`
- [ ] `backend-setup/api/webhooks.py`

---

## Environment Variables

Add to `backend-setup/.env`:
```env
DATABASE_URL=postgresql://user:pass@your-ionos-ip:5432/ai_receptionist
JWT_SECRET=your_random_secret_key
GOOGLE_CLIENT_ID=your_google_id
GOOGLE_CLIENT_SECRET=your_google_secret
PAYPAL_CLIENT_ID=your_paypal_id
PAYPAL_CLIENT_SECRET=your_paypal_secret
```

Add to `src/.env.local`:
```env
REACT_APP_API_URL=https://your-ionos-ip:8000
REACT_APP_GOOGLE_CLIENT_ID=your_google_id
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_id
```

---

## Testing Checklist

### Week 1
- [ ] User can sign up
- [ ] User can log in
- [ ] JWT token is created
- [ ] Token is stored in localStorage
- [ ] Protected routes redirect to login

### Week 2
- [ ] User can create client
- [ ] User can view clients
- [ ] User can see call stats
- [ ] Real-time updates work

### Week 3
- [ ] User can view pricing
- [ ] User can subscribe with PayPal
- [ ] Subscription is stored in DB
- [ ] Webhook is received

### Week 4
- [ ] All pages load <3s
- [ ] No console errors
- [ ] Mobile responsive
- [ ] All API endpoints working

---

## Common Issues & Solutions

### "Cannot connect to PostgreSQL"
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
psql -h your-ionos-ip -U postgres -d ai_receptionist
```

### "CORS error"
```python
# Add to backend-setup/ui/app.py
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### "JWT token invalid"
```python
# Make sure JWT_SECRET is set in .env
# And same secret is used for encoding/decoding
```

### "PayPal webhook not received"
```bash
# Check webhook URL is publicly accessible
curl https://your-ionos-ip:8000/api/webhooks/paypal

# Check PayPal sandbox settings
# Verify webhook is registered in PayPal dashboard
```

---

## Resources

**Full Documentation:**
- `FRONTEND_INTEGRATION_SUMMARY.md` - Complete overview
- `FRONTEND_TASKS_PART1.md` - Setup & infrastructure
- `FRONTEND_TASKS_PART2.md` - Detailed tasks
- `FRONTEND_TASKS_PART3.md` - VPS connection guide

**Backend:**
- `backend-setup/README.md`
- `backend-setup/DEPLOYMENT_GUIDE.md`

**External:**
- React: https://react.dev
- Flask: https://flask.palletsprojects.com
- PostgreSQL: https://www.postgresql.org/docs
- PayPal: https://developer.paypal.com

---

## Next Steps

1. **Read** `FRONTEND_INTEGRATION_SUMMARY.md` (10 min)
2. **Read** `FRONTEND_TASKS_PART1.md` (15 min)
3. **Set up** PostgreSQL schema (15 min)
4. **Create** `backend-setup/api/auth.py` (30 min)
5. **Create** `src/pages/auth/Login.jsx` (30 min)
6. **Test** login flow (15 min)

**Total: ~2 hours to get started**

---

## Success Metrics

After Week 1:
- ✅ Users can sign up
- ✅ Users can log in
- ✅ Protected routes work

After Week 2:
- ✅ Dashboard shows stats
- ✅ Users can manage clients
- ✅ Real-time updates work

After Week 3:
- ✅ Users can subscribe
- ✅ PayPal integration works
- ✅ Invoices are generated

After Week 4:
- ✅ System is production-ready
- ✅ All tests passing
- ✅ Performance optimized

---

## You're Ready! 🚀

Your backend is done. Now build the frontend.

Start with `FRONTEND_INTEGRATION_SUMMARY.md` for the big picture.

Then follow `FRONTEND_TASKS_PART2.md` for step-by-step tasks.

Good luck!
