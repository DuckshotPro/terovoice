# Phase 2: Authentication - Quick Start Guide

**Estimated Duration:** 3 days (Tasks 6-10)
**Tasks:** 5 main tasks + optional tests
**Status:** Ready to begin

---

## What You'll Build

A complete authentication system with:
- Login page with email/password
- Signup page with email/password/name
- OAuth integration (Google, GitHub)
- Protected routes
- Session persistence
- Error handling

---

## Quick Reference: Files to Create

### Task 6: Authentication Pages

```
src/pages/auth/
├── Login.jsx              # Login page
├── Signup.jsx             # Signup page
└── OAuthCallback.jsx      # OAuth callback handler
```

### Task 10: Authentication Components

```
src/components/auth/
├── LoginForm.jsx          # Login form component
├── SignupForm.jsx         # Signup form component
├── OAuthButtons.jsx       # OAuth buttons
└── AuthError.jsx          # Error display
```

---

## Implementation Checklist

### Task 6: Create Authentication Pages
- [ ] Create `src/pages/auth/Login.jsx`
  - Use LoginForm component
  - Handle form submission
  - Redirect on success
  
- [ ] Create `src/pages/auth/Signup.jsx`
  - Use SignupForm component
  - Handle form submission
  - Redirect on success
  
- [ ] Create `src/pages/auth/OAuthCallback.jsx`
  - Handle OAuth redirect
  - Exchange code for token
  - Redirect to dashboard

### Task 7: Implement Authentication Service
- [ ] Already done in AuthContext!
  - `login()` function
  - `signup()` function
  - `logout()` function
  - Token refresh in interceptor

### Task 8: Create useAuth Hook
- [ ] Already done!
  - `useAuth()` hook
  - Session persistence
  - Token management

### Task 9: Implement OAuth Integration
- [ ] Create OAuth button handlers
- [ ] Implement OAuth flow
- [ ] Handle OAuth errors

### Task 10: Create Authentication UI Components
- [ ] Create LoginForm component
- [ ] Create SignupForm component
- [ ] Create OAuthButtons component
- [ ] Create error display component

---

## Code Templates

### Login Page Template

```jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoginForm from '../../components/auth/LoginForm';

export const Login = () => {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuth();

  const handleSubmit = async (values) => {
    try {
      await login(values.email, values.password);
      navigate('/app/dashboard');
    } catch (err) {
      // Error handled by context
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <LoginForm onSubmit={handleSubmit} isLoading={isLoading} error={error} />
    </div>
  );
};

export default Login;
```

### LoginForm Component Template

```jsx
import React from 'react';
import { useForm } from '../../hooks/useForm';
import { validateLoginForm } from '../../utils/validation';

export const LoginForm = ({ onSubmit, isLoading, error }) => {
  const { values, errors, touched, handleChange, handleBlur, handleSubmit } = useForm(
    { email: '', password: '' },
    onSubmit,
    validateLoginForm
  );

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
      {/* Email field */}
      {/* Password field */}
      {/* Submit button */}
    </form>
  );
};

export default LoginForm;
```

---

## API Endpoints Used

```javascript
// Already configured in src/services/api.js

api.auth.register(userData)      // POST /auth/register
api.auth.login(credentials)      // POST /auth/login
api.auth.logout()                // POST /auth/logout
api.auth.refresh(refreshToken)   // POST /auth/refresh
api.auth.me()                    // GET /auth/me
```

---

## Validation Rules

### Login Form
- Email: required, valid email format
- Password: required

### Signup Form
- Name: required, min 2 characters
- Email: required, valid email format
- Password: required, min 8 chars, uppercase, lowercase, number
- Confirm Password: required, must match password

---

## Environment Variables Needed

```env
# Already in .env.local

VITE_API_URL=http://localhost:8000
VITE_ENABLE_OAUTH=false  # Set to true when ready
VITE_GOOGLE_CLIENT_ID=   # Add when ready
VITE_GITHUB_CLIENT_ID=   # Add when ready
```

---

## Testing Checklist

- [ ] Login with valid credentials
- [ ] Login with invalid credentials (error message)
- [ ] Signup with valid data
- [ ] Signup with invalid data (validation errors)
- [ ] Signup with existing email (error message)
- [ ] Logout redirects to login
- [ ] Protected routes redirect to login when not authenticated
- [ ] Session persists on page reload
- [ ] Token refresh works on expiration

---

## Common Patterns

### Using useAuth Hook

```jsx
import { useAuth } from '../contexts/AuthContext';

export const MyComponent = () => {
  const { user, isAuthenticated, login, logout } = useAuth();

  return (
    <div>
      {isAuthenticated ? (
        <>
          <p>Welcome, {user.name}</p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <p>Please log in</p>
      )}
    </div>
  );
};
```

### Using useForm Hook

```jsx
import { useForm } from '../hooks/useForm';
import { validateLoginForm } from '../utils/validation';

export const LoginForm = ({ onSubmit }) => {
  const { values, errors, touched, handleChange, handleBlur, handleSubmit } = useForm(
    { email: '', password: '' },
    onSubmit,
    validateLoginForm
  );

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="email"
        value={values.email}
        onChange={handleChange}
        onBlur={handleBlur}
      />
      {touched.email && errors.email && <span>{errors.email}</span>}
    </form>
  );
};
```

---

## Helpful Resources

- **Validation:** `src/utils/validation.js` - All validation functions
- **Error Handling:** `src/utils/errorHandler.js` - Error utilities
- **Formatting:** `src/utils/formatters.js` - Data formatting
- **API Client:** `src/services/api.js` - All API endpoints
- **Auth Context:** `src/contexts/AuthContext.jsx` - Auth state and functions

---

## Next Phase After Authentication

Once Phase 2 is complete, Phase 3 will build:
- Dashboard page
- Client management pages
- Call management pages
- Analytics pages
- Billing pages
- Settings pages

---

## Tips for Success

1. **Start with LoginForm** - It's the simplest
2. **Test validation** - Make sure error messages show correctly
3. **Test error handling** - Try invalid credentials
4. **Test session persistence** - Reload page and verify still logged in
5. **Test protected routes** - Try accessing /app without logging in

---

**Ready to build Phase 2!** 🚀

Start with Task 6: Create Authentication Pages
