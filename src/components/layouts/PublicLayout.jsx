import React from 'react';
import { Outlet } from 'react-router-dom';
import BackgroundWave from '../common/BackgroundWave';

/**
 * PublicLayout Component
 *
 * Layout for public pages (login, signup, landing page)
 * No authentication required
 */

export const PublicLayout = () => {
  return (
    <BackgroundWave>
      <Outlet />
    </BackgroundWave>
  );
};

export default PublicLayout;
