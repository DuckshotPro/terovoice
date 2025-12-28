import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Menu, X, LogOut, Settings, User } from 'lucide-react';

/**
 * ProtectedLayout Component
 * 
 * Layout for authenticated pages
 * Includes navigation, sidebar, and user menu
 */

export const ProtectedLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/auth/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-slate-900 text-white transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          {sidebarOpen && <h1 className="text-xl font-bold">Tero</h1>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-slate-800 rounded"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <NavLink
            to="/app/dashboard"
            icon="📊"
            label="Dashboard"
            sidebarOpen={sidebarOpen}
          />
          <NavLink
            to="/app/clients"
            icon="👥"
            label="Clients"
            sidebarOpen={sidebarOpen}
          />
          <NavLink
            to="/app/calls"
            icon="📞"
            label="Calls"
            sidebarOpen={sidebarOpen}
          />
          <NavLink
            to="/app/analytics"
            icon="📈"
            label="Analytics"
            sidebarOpen={sidebarOpen}
          />
          <NavLink
            to="/app/billing"
            icon="💳"
            label="Billing"
            sidebarOpen={sidebarOpen}
          />
        </nav>

        {/* User Menu */}
        <div className="p-4 border-t border-slate-700">
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="w-full flex items-center space-x-2 p-2 hover:bg-slate-800 rounded"
            >
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <User size={16} />
              </div>
              {sidebarOpen && (
                <div className="text-left flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{user?.name}</p>
                  <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                </div>
              )}
            </button>

            {/* Dropdown Menu */}
            {userMenuOpen && (
              <div className="absolute bottom-full left-0 right-0 mb-2 bg-slate-800 rounded shadow-lg z-10">
                <button
                  onClick={() => {
                    navigate('/app/settings');
                    setUserMenuOpen(false);
                  }}
                  className="w-full flex items-center space-x-2 px-4 py-2 hover:bg-slate-700 text-sm"
                >
                  <Settings size={16} />
                  <span>Settings</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center space-x-2 px-4 py-2 hover:bg-slate-700 text-sm text-red-400"
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

/**
 * NavLink Component
 * Navigation link with icon and label
 */
const NavLink = ({ to, icon, label, sidebarOpen }) => {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate(to)}
      className="w-full flex items-center space-x-3 px-4 py-2 rounded hover:bg-slate-800 transition-colors"
      title={label}
    >
      <span className="text-xl">{icon}</span>
      {sidebarOpen && <span className="text-sm">{label}</span>}
    </button>
  );
};

export default ProtectedLayout;
