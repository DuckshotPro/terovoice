import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { AppContextProvider } from './contexts';
import { router } from './routes';
import './styles/global.css';

/**
 * Main App Component
 * 
 * Provides:
 * - Context providers (Auth, User, Clients)
 * - Router configuration
 * - Global styles
 */

function App() {
  return (
    <AppContextProvider>
      <RouterProvider router={router} />
    </AppContextProvider>
  );
}

export default App;
