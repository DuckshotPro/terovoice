import React from 'react';
import { Outlet } from 'react-router-dom';

/**
 * PublicLayout Component
 *
 * Layout for public pages (login, signup, landing page)
 * No authentication required
 */

export const PublicLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <Outlet />
    </div>
  );
};

export default PublicLayout;
