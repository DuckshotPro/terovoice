# Frontend Integration Task List - Part 3: VPS Connection Guide

## Your Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│                    IONOS VPS                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ PostgreSQL (Port 5432)                              │  │
│  │ - Users, Subscriptions, Clients, Calls, Invoices   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Flask API (Port 8000)                               │  │
│  │ - /api/auth, /api/users, /api/subscriptions, etc   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ LiveKit Server (Port 5060 SIP, 7880 WebSocket)     │  │
│  │ - Handles incoming calls                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Agent Worker (Python)                               │  │
│  │ - Processes calls, logs analytics                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↑                                    ↑
         │ HTTPS                             │ HTTPS
         │                                   │
    ┌────────────────┐              ┌──────────────────┐
    │ React Frontend │              │ Hugging Face VPS │
    │ (Your Machine) │              │ (LLM Inference)  │
    └────────────────┘              └──────────────────┘
```

## Step 1: PostgreSQL Connection from Frontend

### 1.1 Create Database User
SSH into IONOS and create a restricted user:

```bash
ssh root@your-ionos-ip

# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE ai_receptionist;

# Create user with limited permissions
CREATE USER frontend_user WITH PASSWORD 'your_secure_password';

# Grant permissions
GRANT CONNECT ON DATABASE ai_receptionist TO frontend_user;
GRANT USAGE ON SCHEMA public TO frontend_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO frontend_user;

# Exit
\q
```

### 1.2 Configure PostgreSQL for Remote Access
Edit `/etc/postgresql/*/main/postgresql.conf`:

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf

# Find and change:
# listen_addresses = 'localhost'
# To:
listen_addresses = '*'

# Save and exit
```

Edit `/etc/postgresql/*/main/pg_hba.conf`:

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Add at the end:
host    ai_receptionist    frontend_user    0.0.0.0/0    md5

# Save and exit
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### 1.3 Test Connection from Your Machine

```bash
# Install psql client (if not already installed)
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql-client
# Windows: Download from postgresql.org

# Test connection
psql -h your-ionos-ip -U frontend_user -d ai_receptionist

# You should see the psql prompt
ai_receptionist=>
```

### 1.4 Connection String for Backend

Add to your backend `.env`:

```env
DATABASE_URL=postgresql://frontend_user:your_secure_password@your-ionos-ip:5432/ai_receptionist
```

---

## Step 2: Flask API Connection

### 2.1 Create Flask API Routes

Add to `backend-setup/api/users.py`:

```python
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import jwt
from config.settings import settings

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/profile', methods=['GET'])
@cross_origin()
def get_profile():
    """Get current user profile"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=['HS256'])
        user_id = payload['user_id']

        # Query database
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': str(user.id),
            'email': user.email,
            'name': user.name,
            'created_at': user.created_at.isoformat()
        })

    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

@users_bp.route('/profile', methods=['PUT'])
@cross_origin()
def update_profile():
    """Update user profile"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    data = request.json

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=['HS256'])
        user_id = payload['user_id']

        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.name = data.get('name', user.name)
        db.session.commit()

        return jsonify({'status': 'success'})

    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
```

### 2.2 Enable CORS

Update `backend-setup/ui/app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173",  # Vite dev server
            "https://yourdomain.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 2.3 Test API from Frontend

```bash
# From your React app directory
curl -H "Authorization: Bearer your_token" \
  https://your-ionos-ip:8000/api/users/profile
```

---

## Step 3: Frontend Environment Configuration

### 3.1 Create `.env.local` in React app

```env
# API
REACT_APP_API_URL=https://your-ionos-ip:8000
REACT_APP_WS_URL=wss://your-ionos-ip:7880

# OAuth
REACT_APP_GOOGLE_CLIENT_ID=your_google_id
REACT_APP_GITHUB_CLIENT_ID=your_github_id

# PayPal
REACT_APP_PAYPAL_CLIENT_ID=your_paypal_id
```

### 3.2 Create API Service

Create `src/services/api.js`:

```javascript
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 3.3 Create Auth Hook

Create `src/hooks/useAuth.js`:

```javascript
import { useState, useEffect } from 'react';
import api from '../services/api';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.get('/api/users/profile')
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password });
    localStorage.setItem('token', res.data.token);
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return { user, loading, login, logout };
}
```

---

## Step 4: Hugging Face VPS Connection

### 4.1 Verify HF VPS is Running

```bash
# From your machine
curl https://your-hf-vps:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "max_new_tokens": 10}'

# Should return a response
```

### 4.2 Update Backend Config

In `backend-setup/.env`:

```env
HUGGINGFACE_API_URL=https://your-hf-vps:8000
HUGGINGFACE_API_KEY=optional_auth_key
```

### 4.3 Test LLM Integration

```bash
# SSH to IONOS
ssh root@your-ionos-ip
cd ultimate-ai-receptionist

# Test HF connection
docker-compose exec agent python -c "
from services.llm.huggingface_provider import HuggingFaceLLMProvider
import asyncio

async def test():
    provider = HuggingFaceLLMProvider()
    response = await provider.generate_response('Hello, how are you?')
    print(response)

asyncio.run(test())
"
```

---

## Step 5: Network Security

### 5.1 Firewall Rules (IONOS)

```bash
# SSH to IONOS
ssh root@your-ionos-ip

# Allow PostgreSQL from your IP only
sudo ufw allow from YOUR_IP to any port 5432

# Allow Flask API from anywhere (or restrict to your domain)
sudo ufw allow 8000

# Allow LiveKit
sudo ufw allow 5060
sudo ufw allow 7880
sudo ufw allow 50000:50100/udp

# Check rules
sudo ufw status
```

### 5.2 SSL Certificates

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate for your domain
sudo certbot certonly --standalone -d your-ionos-ip

# Or use your domain
sudo certbot certonly --standalone -d yourdomain.com
```

### 5.3 Update Backend to Use HTTPS

```bash
# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /root/ultimate-ai-receptionist/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /root/ultimate-ai-receptionist/

# Update docker-compose.yml to mount certificates
```

---

## Step 6: Testing the Full Flow

### 6.1 Test User Registration

```bash
# From your React app
curl -X POST https://your-ionos-ip:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "secure_password",
    "name": "Test User"
  }'

# Should return token and user data
```

### 6.2 Test Client Creation

```bash
# From your React app
curl -X POST https://your-ionos-ip:8000/api/clients \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr Mike Dentistry",
    "phone_number": "+12025551234",
    "profession": "dentist"
  }'
```

### 6.3 Test Analytics

```bash
# From your React app
curl https://your-ionos-ip:8000/api/clients/client-id/stats \
  -H "Authorization: Bearer your_token"

# Should return call stats
```

---

## Step 7: Deployment Checklist

- [ ] PostgreSQL running on IONOS
- [ ] Flask API running on IONOS
- [ ] LiveKit running on IONOS
- [ ] Agent worker running on IONOS
- [ ] Hugging Face VPS running
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] CORS enabled on backend
- [ ] Environment variables set
- [ ] Frontend can connect to backend
- [ ] Frontend can authenticate
- [ ] Frontend can create clients
- [ ] Frontend can view analytics
- [ ] PayPal integration working
- [ ] Webhooks working

---

## Troubleshooting

### PostgreSQL Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if listening on all interfaces
sudo netstat -tlnp | grep 5432

# Check pg_hba.conf
sudo cat /etc/postgresql/14/main/pg_hba.conf
```

### Flask API Not Responding
```bash
# Check if Flask is running
docker-compose ps

# Check logs
docker-compose logs -f api

# Test locally
curl http://localhost:8000/api/users/profile
```

### Hugging Face Connection Failed
```bash
# Check if HF VPS is running
curl https://your-hf-vps:8000/api/v1/generate

# Check firewall
sudo ufw status

# Check network connectivity
ping your-hf-vps
```

### CORS Errors
```bash
# Check CORS headers
curl -i https://your-ionos-ip:8000/api/users/profile

# Should include:
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE
```

---

## Summary

Your frontend connects to:
1. **PostgreSQL** (IONOS) - User/billing data
2. **Flask API** (IONOS) - REST endpoints
3. **LiveKit** (IONOS) - Real-time updates
4. **Hugging Face VPS** - LLM inference (via backend)

All connections are HTTPS/WSS for security.

---

## Next Steps

1. ✅ Set up PostgreSQL on IONOS
2. ✅ Create Flask API routes
3. ✅ Configure CORS
4. ✅ Create React services/hooks
5. ✅ Test connections
6. ✅ Deploy frontend
7. ✅ Monitor and optimize

See FRONTEND_TASKS_PART2.md for detailed component tasks.
