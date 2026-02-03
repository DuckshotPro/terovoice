# Plan: Fix Authentication Integration

The previous agent implementation of the Authentication system has created a mismatch between the Frontend and Backend contracts.
- **Frontend** (`AuthContext.jsx`, `api.js`) expects: `{ access_token, refresh_token, user }`
- **Backend** (`auth.py`) returns: `{ token, user }`

This plan aims to align the Frontend to the Backend's single-token architecture.

## Steps

1.  **Create `src/hooks/useAuth.js`**
    *   Create this file to re-export `useAuth` from `../contexts/AuthContext` to satisfy project structure expectations.

2.  **Update `src/contexts/AuthContext.jsx`**
    *   Modify `login` and `signup` functions to destructure `token` from response instead of `access_token`/`refresh_token`.
    *   Update `initializeAuth` to work with the single `token`.
    *   Remove `refresh_token` variable usage.

3.  **Update `src/services/api.js`**
    *   Modify `tokenManager` to simplify token handling (remove `refresh_token` references).
    *   Update the 401 interceptor. Since the backend `/refresh` endpoint requires a valid token (not expired), the current "refresh on 401" logic is flawed. We will temporarily disable the auto-refresh logic to prevent errors, redirecting to login on 401 instead.
    *   Update `api.auth.refresh` call signature if needed.

4.  **Verification**
    *   Review code changes to ensure variable names match.
