# Backend API Quick Start

**Status:** ✅ Ready to Run
**Time to Setup:** ~15 minutes

---

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
cd backend-setup
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and set:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_receptionist
JWT_SECRET=your_random_secret_key_here
FLASK_PORT=8000
DEBUG=False
```

### 3. Initialize Database
```bash
python -c "from backend_setup.db.connection import init_db; init_db()"
```

### 4. Run API Server
```bash
python -m backend_setup.api.app
```

**Output:**
```
✅ Database initialized and connected
✅ API routes registered
🚀 Starting API server on port 8000
```

---

## ✅ Verify It's Working

### Health Check
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "ai-receptionist-api",
  "version": "1.0.0"
}
```

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

### Create Client
```bash
TOKEN="eyJhbGciOiJIUzI1NiIs..."

curl -X POST http://localhost:8000/api/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Mike'\''s Dental",
    "phone_number": "+1-555-0100",
    "profession": "dentist",
    "voice_name": "af_sarah"
  }'
```

**Response:**
```json
{
  "client": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Dr. Mike's Dental",
    "phone_number": "+1-555-0100",
    "profession": "dentist",
    "voice_name": "af_sarah",
    "created_at": "2025-12-26T10:30:00"
  }
}
```

---

## 📁 Project Structure

```
backend-setup/
├── api/
│   ├── __init__.py
│   ├── app.py                 # Main Flask app
│   └── routes/
│       ├── auth.py            # Authentication endpoints
│       ├── clients.py         # Client management
│       ├── calls.py           # Call logging
│       └── analytics.py       # Analytics endpoints
├── db/
│   ├── connection.py          # Database connection pool
│   └── models.py              # SQLAlchemy models
├── services/
│   └── auth_service.py        # Authentication logic
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── API_DOCUMENTATION.md       # Full API docs
└── BACKEND_QUICKSTART.md      # This file
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `api/app.py` | Main Flask application |
| `api/routes/auth.py` | User registration & login |
| `api/routes/clients.py` | Client CRUD operations |
| `api/routes/calls.py` | Call logging from Ollama |
| `api/routes/analytics.py` | Dashboard stats & trends |
| `db/models.py` | Database schema (SQLAlchemy) |
| `db/connection.py` | PostgreSQL connection pool |
| `services/auth_service.py` | JWT & password hashing |

---

## 🧪 Test All Endpoints

### 1. Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123","name":"Test"}'
```

Save the token from response.

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'
```

### 3. Get Current User
```bash
TOKEN="<token_from_above>"
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Create Client
```bash
curl -X POST http://localhost:8000/api/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Dr. Mike",
    "phone_number":"+1-555-0100",
    "profession":"dentist",
    "voice_name":"af_sarah"
  }'
```

Save the client_id from response.

### 5. List Clients
```bash
curl -X GET http://localhost:8000/api/clients \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Log Call
```bash
CLIENT_ID="<client_id_from_above>"
curl -X POST http://localhost:8000/api/calls \
  -H "Content-Type: application/json" \
  -d '{
    "client_id":"'$CLIENT_ID'",
    "caller_phone":"+1-555-0200",
    "caller_name":"John Smith",
    "duration_seconds":45.5,
    "stt_latency_ms":150,
    "llm_latency_ms":300,
    "tts_latency_ms":200,
    "transcript":"Customer: Hello...",
    "sentiment":"POSITIVE",
    "success":true
  }'
```

### 7. Get Dashboard Stats
```bash
curl -X GET http://localhost:8000/api/analytics/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐛 Troubleshooting

### "Cannot connect to PostgreSQL"
```bash
# Check if PostgreSQL is running
psql -h 74.208.227.161 -U user -d ai_receptionist

# Check connection string in .env
echo $DATABASE_URL
```

### "ModuleNotFoundError: No module named 'backend_setup'"
```bash
# Make sure you're in the right directory
cd backend-setup

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
```

### "JWT token invalid"
```bash
# Make sure JWT_SECRET is set in .env
# And it's the same when encoding/decoding
```

### "CORS error in frontend"
```bash
# Update CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## 📊 Database Check

### Connect to Database
```bash
psql -h 74.208.227.161 -U user -d ai_receptionist
```

### Check Tables
```sql
\dt
```

### Check Users
```sql
SELECT id, email, name, created_at FROM users;
```

### Check Clients
```sql
SELECT id, name, phone_number, profession FROM clients;
```

### Check Calls
```sql
SELECT id, caller_phone, duration_seconds, sentiment FROM calls;
```

---

## 🚀 Deploy to IONOS

### 1. SSH to IONOS
```bash
ssh root@your-ionos-ip
cd ultimate-ai-receptionist
```

### 2. Install Dependencies
```bash
pip install -r backend-setup/requirements.txt
```

### 3. Configure Environment
```bash
cd backend-setup
cp .env.example .env
# Edit .env with production settings
```

### 4. Run with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend_setup.api.app:app
```

### 5. Set Up Systemd Service
```bash
sudo tee /etc/systemd/system/ai-receptionist-api.service > /dev/null <<EOF
[Unit]
Description=AI Receptionist API
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/root/ultimate-ai-receptionist/backend-setup
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:8000 backend_setup.api.app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ai-receptionist-api
sudo systemctl start ai-receptionist-api
```

### 6. Check Status
```bash
sudo systemctl status ai-receptionist-api
```

---

## 📝 Next Steps

1. ✅ Backend API is running
2. 🔄 **Next:** Build React frontend (see `FRONTEND_INTEGRATION_SUMMARY.md`)
3. 🔄 Connect frontend to API
4. 🔄 Deploy frontend
5. 🔄 Set up monitoring

---

## 📚 Documentation

- `API_DOCUMENTATION.md` - Full API reference
- `DATABASE_FRONTEND_INTEGRATION.md` - Integration tasks
- `FRONTEND_INTEGRATION_SUMMARY.md` - Frontend setup

---

**Backend is ready! 🚀**

Next: Build the React frontend and connect it to these API endpoints.
