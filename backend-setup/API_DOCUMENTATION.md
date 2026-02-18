# Backend API Documentation

**Status:** ✅ Phase 1 Complete
**Version:** 1.0.0
**Last Updated:** December 26, 2025

---

## 📋 Overview

The AI Receptionist SaaS backend API provides RESTful endpoints for:
- User authentication (registration, login, JWT tokens)
- Client management (CRUD operations for businesses)
- Call logging (recording call data from Ollama agent)
- Analytics (dashboard stats, trends, sentiment analysis)

**Base URL:** `http://localhost:8000/api` (development)
**Production URL:** `https://your-ionos-ip:8000/api`

---

## 🔐 Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

**Header Format:**
```
Authorization: Bearer <jwt_token>
```

**Token Expiration:** 24 hours

---

## 📚 API Endpoints

### Authentication (`/api/auth`)

#### 1. Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}

Response (201):
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

#### 2. Login User
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response (200):
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

#### 3. Get Current User
```
GET /api/auth/me
Authorization: Bearer <token>

Response (200):
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-12-26T10:30:00"
  }
}
```

#### 4. Refresh Token
```
POST /api/auth/refresh
Authorization: Bearer <token>

Response (200):
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### Clients (`/api/clients`)

#### 1. List All Clients
```
GET /api/clients
Authorization: Bearer <token>

Response (200):
{
  "clients": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Dr. Mike's Dental",
      "phone_number": "+1-555-0100",
      "profession": "dentist",
      "voice_name": "af_sarah",
      "created_at": "2025-12-26T10:30:00"
    }
  ]
}
```

#### 2. Create Client
```
POST /api/clients
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Dr. Mike's Dental",
  "phone_number": "+1-555-0100",
  "profession": "dentist",
  "voice_name": "af_sarah"
}

Response (201):
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

#### 3. Get Client Details
```
GET /api/clients/<client_id>
Authorization: Bearer <token>

Response (200):
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

#### 4. Update Client
```
PUT /api/clients/<client_id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Dr. Mike's Dental - Updated",
  "profession": "dentist",
  "voice_name": "af_sky"
}

Response (200):
{
  "client": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Dr. Mike's Dental - Updated",
    "phone_number": "+1-555-0100",
    "profession": "dentist",
    "voice_name": "af_sky",
    "created_at": "2025-12-26T10:30:00"
  }
}
```

#### 5. Delete Client
```
DELETE /api/clients/<client_id>
Authorization: Bearer <token>

Response (200):
{
  "message": "Client deleted"
}
```

---

### Calls (`/api/calls`)

#### 1. List All Calls
```
GET /api/calls?limit=50&offset=0&client_id=<id>&days=30
Authorization: Bearer <token>

Response (200):
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "calls": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "client_id": "550e8400-e29b-41d4-a716-446655440001",
      "caller_phone": "+1-555-0200",
      "caller_name": "John Smith",
      "duration_seconds": 45.5,
      "sentiment": "POSITIVE",
      "success": true,
      "created_at": "2025-12-26T10:30:00"
    }
  ]
}
```

#### 2. Log New Call (from Ollama Agent)
```
POST /api/calls
Content-Type: application/json

{
  "client_id": "550e8400-e29b-41d4-a716-446655440001",
  "caller_phone": "+1-555-0200",
  "caller_name": "John Smith",
  "duration_seconds": 45.5,
  "stt_latency_ms": 150,
  "llm_latency_ms": 300,
  "tts_latency_ms": 200,
  "transcript": "Customer: Hello, I'd like to schedule an appointment...",
  "sentiment": "POSITIVE",
  "success": true,
  "recording_url": "https://storage.example.com/call-123.wav",
  "notes": "Customer interested in cleaning appointment"
}

Response (201):
{
  "call": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "client_id": "550e8400-e29b-41d4-a716-446655440001",
    "created_at": "2025-12-26T10:30:00"
  }
}
```

#### 3. Get Call Details
```
GET /api/calls/<call_id>
Authorization: Bearer <token>

Response (200):
{
  "call": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "client_id": "550e8400-e29b-41d4-a716-446655440001",
    "caller_phone": "+1-555-0200",
    "caller_name": "John Smith",
    "duration_seconds": 45.5,
    "stt_latency_ms": 150,
    "llm_latency_ms": 300,
    "tts_latency_ms": 200,
    "transcript": "Customer: Hello, I'd like to schedule an appointment...",
    "sentiment": "POSITIVE",
    "success": true,
    "recording_url": "https://storage.example.com/call-123.wav",
    "notes": "Customer interested in cleaning appointment",
    "created_at": "2025-12-26T10:30:00"
  }
}
```

---

### Analytics (`/api/analytics`)

#### 1. Dashboard Stats
```
GET /api/analytics/dashboard
Authorization: Bearer <token>

Response (200):
{
  "total_calls": 150,
  "total_duration": 3600.5,
  "success_rate": 95.3,
  "avg_sentiment": "POSITIVE",
  "total_clients": 5
}
```

#### 2. Calls Per Day
```
GET /api/analytics/calls-per-day?days=30
Authorization: Bearer <token>

Response (200):
{
  "data": [
    {
      "date": "2025-12-26",
      "calls": 15
    },
    {
      "date": "2025-12-25",
      "calls": 12
    }
  ]
}
```

#### 3. Sentiment Analysis
```
GET /api/analytics/sentiment
Authorization: Bearer <token>

Response (200):
{
  "POSITIVE": 95,
  "NEGATIVE": 10,
  "NEUTRAL": 45
}
```

#### 4. Client Stats
```
GET /api/analytics/client/<client_id>/stats
Authorization: Bearer <token>

Response (200):
{
  "client_id": "550e8400-e29b-41d4-a716-446655440001",
  "client_name": "Dr. Mike's Dental",
  "total_calls": 50,
  "total_duration": 1200.5,
  "success_rate": 96.0,
  "avg_stt_latency_ms": 145.2,
  "avg_llm_latency_ms": 295.8,
  "avg_tts_latency_ms": 198.5
}
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd backend-setup
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database
```bash
python -c "from backend_setup.db.connection import init_db; init_db()"
```

### 4. Run API Server
```bash
python -m backend_setup.api.app
```

Server will start on `http://localhost:8000`

---

## 🧪 Testing Endpoints

### Using cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Create Client:**
```bash
curl -X POST http://localhost:8000/api/clients \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Mike'\''s Dental",
    "phone_number": "+1-555-0100",
    "profession": "dentist",
    "voice_name": "af_sarah"
  }'
```

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  password_hash VARCHAR,
  oauth_provider VARCHAR,
  oauth_id VARCHAR,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Clients Table
```sql
CREATE TABLE clients (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR NOT NULL,
  phone_number VARCHAR UNIQUE NOT NULL,
  profession VARCHAR,
  voice_id VARCHAR,
  voice_name VARCHAR,
  system_prompt TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Calls Table
```sql
CREATE TABLE calls (
  id UUID PRIMARY KEY,
  client_id UUID REFERENCES clients(id),
  caller_phone VARCHAR,
  caller_name VARCHAR,
  duration_seconds FLOAT,
  stt_latency_ms FLOAT,
  llm_latency_ms FLOAT,
  tts_latency_ms FLOAT,
  transcript TEXT,
  sentiment VARCHAR,
  success BOOLEAN DEFAULT TRUE,
  recording_url VARCHAR,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "error": "Email and password required"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "error": "Client not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to create client"
}
```

---

## 🔄 Integration with Frontend

The frontend will use these endpoints to:

1. **Register/Login** - Get JWT token
2. **Create Clients** - Add businesses to manage
3. **View Calls** - Display call logs and transcripts
4. **View Analytics** - Show dashboard stats and trends

See `FRONTEND_INTEGRATION_SUMMARY.md` for frontend integration details.

---

## 📝 Next Steps

- [ ] Deploy API to IONOS VPS
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for frontend domain
- [ ] Add rate limiting
- [ ] Add request logging
- [ ] Set up monitoring and alerts
- [ ] Create API documentation (Swagger/OpenAPI)

---

**API is ready for frontend integration! 🚀**
