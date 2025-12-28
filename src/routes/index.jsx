import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import PublicLayout from '../components/layouts/PublicLayout';
import ProtectedLayout from '../components/layouts/ProtectedLayout';

// Public Pages
import Home from '../pages/Home';
import About from '../pages/About';
import Products from '../pages/Products';
import NotFound from '../pages/NotFound';

// Auth Pages (to be created)
// import Login from '../pages/auth/Login';
// import Signup from '../pages/auth/Signup';

// Protected Pages (to be created)
// import Dashboard from '../pages/dashboard/Dashboard';
// import Clients from '../pages/clients/Clients';
// import Calls from '../pages/calls/Calls';
// import Analytics from '../pages/analytics/Analytics';
// import Billing from '../pages/billing/Billing';
// import Settings from '../pages/settings/Settings';

/**
 * Application Routes
 * 
 * Structure:
 * - Public routes (no auth required)
 * - Auth routes (login, signup)
 * - Protected routes (auth required)
 */

export const router = createBrowserRouter([
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: 'about',
        element: <About />,
      },
      {
        path: 'products',
        element: <Products />,
      },
      // Auth routes will be added here
      // {
      //   path: 'login',
      //   element: <Login />,
      // },
      // {
      //   path: 'signup',
      //   element: <Signup />,
      // },
    ],
  },
  {
    path: '/app',
    element: (
      <ProtectedRoute>
        <ProtectedLayout />
      </ProtectedRoute>
    ),
    children: [
      // Protected routes will be added here
      // {
      //   path: 'dashboard',
      //   element: <Dashboard />,
      // },
      // {
      //   path: 'clients',
      //   element: <Clients />,
      // },
      // {
      //   path: 'calls',
      //   element: <Calls />,
      // },
      // {
      //   path: 'analytics',
      //   element: <Analytics />,
      // },
      // {
      //   path: 'billing',
      //   element: <Billing />,
      // },
      // {
      //   path: 'settings',
      //   element: <Settings />,
      // },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);

export default router;
