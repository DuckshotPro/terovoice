import { createBrowserRouter, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import PublicLayout from '../components/layouts/PublicLayout';
import ProtectedLayout from '../components/layouts/ProtectedLayout';

// Public Pages
import Home from '../pages/Home';
import About from '../pages/About';
import Products from '../pages/Products';
import NotFound from '../pages/NotFound';
import MemberPortal from '../pages/MemberPortal';

// Auth Pages
import Login from '../pages/auth/Login';
import Signup from '../pages/auth/Signup';

// Protected Pages
import Dashboard from '../pages/dashboard/Dashboard';
import Clients from '../pages/clients/Clients';
import Billing from '../pages/billing/Billing';
import Calls from '../pages/calls/Calls';
import Analytics from '../pages/analytics/Analytics';

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
      {
        path: 'auth/login',
        element: <Login />,
      },
      {
        path: 'auth/signup',
        element: <Signup />,
      },
      {
        path: 'member-portal',
        element: <MemberPortal />,
      },
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
      {
        index: true,
        element: <Navigate to="dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'clients',
        element: <Clients />,
      },
      {
        path: 'billing',
        element: <Billing />,
      },
      {
        path: 'calls',
        element: <Calls />,
      },
      {
        path: 'analytics',
        element: <Analytics />,
      },
      {
        path: 'portal',
        element: <MemberPortal />,
      },
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
