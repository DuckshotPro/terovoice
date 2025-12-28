import React from 'react';
import { AuthProvider } from './AuthContext';
import { UserProvider } from './UserContext';
import { ClientsProvider } from './ClientsContext';

/**
 * Combined Context Provider
 * 
 * Wraps all context providers in the correct order
 */

export const AppContextProvider = ({ children }) => {
  return (
    <AuthProvider>
      <UserProvider>
        <ClientsProvider>
          {children}
        </ClientsProvider>
      </UserProvider>
    </AuthProvider>
  );
};

// Export individual contexts for direct use if needed
export { AuthProvider, useAuth } from './AuthContext';
export { UserProvider, useUser } from './UserContext';
export { ClientsProvider, useClients } from './ClientsContext';
