
import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Menu, X, LogOut, Settings, User, Bell, ChevronDown } from 'lucide-react';
import Footer from '../common/Footer';

/**
 * ProtectedLayout Component
 *
 * Layout for authenticated pages
 * Includes navigation sidebar and top header
 */

export const ProtectedLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
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

  // Determine page title based on path
  const getPageTitle = () => {
    const path = location.pathname;
    if (path.includes('dashboard')) return 'Dashboard';
    if (path.includes('clients')) return 'Client Management';
    if (path.includes('calls')) return 'Call Logs';
    if (path.includes('analytics')) return 'Analytics';
    if (path.includes('billing')) return 'Billing & Subscription';
    if (path.includes('account')) return 'Account Settings';
    if (path.includes('portal')) return 'Member Portal';
    return 'Dashboard';
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar - Fixed Left */}
      <aside
        className={`${sidebarOpen ? 'w-64' : 'w-20'
          } bg-slate-900 text-white transition-all duration-300 flex flex-col shrink-0 z-20`}
      >
        {/* Logo Area */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
          {sidebarOpen && <div className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">Tero Voice</div>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          <NavLink to="/app/dashboard" icon="📊" label="Dashboard" sidebarOpen={sidebarOpen} active={location.pathname.includes('dashboard')} />
          <NavLink to="/app/clients" icon="👥" label="Clients" sidebarOpen={sidebarOpen} active={location.pathname.includes('clients')} />
          <NavLink to="/app/calls" icon="📞" label="Calls" sidebarOpen={sidebarOpen} active={location.pathname.includes('calls')} />
          <NavLink to="/app/analytics" icon="📈" label="Analytics" sidebarOpen={sidebarOpen} active={location.pathname.includes('analytics')} />
          <NavLink to="/app/billing" icon="💳" label="Billing" sidebarOpen={sidebarOpen} active={location.pathname.includes('billing')} />
          <div className="pt-4 mt-4 border-t border-slate-800">
            <NavLink to="/app/portal" icon="🚀" label="Portal Home" sidebarOpen={sidebarOpen} active={location.pathname.includes('portal')} />
          </div>
        </nav>
      </aside>

      {/* Main Content Wrapper - Right Side */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">

        {/* Top Header - Fixed Top */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0 z-10 shadow-sm">
          <h1 className="text-xl font-semibold text-slate-800">{getPageTitle()}</h1>

          <div className="flex items-center space-x-4">
            {/* Notification Bell */}
            <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors relative">
              <Bell size={20} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Separator */}
            <div className="h-6 w-px bg-slate-200"></div>

            {/* User Dropdown */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-3 p-1.5 rounded-lg hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-200"
              >
                <div className="text-right hidden md:block">
                  <p className="text-sm font-medium text-slate-700 leading-none">{user?.name || 'User'}</p>
                  <p className="text-xs text-slate-500 mt-1">{user?.email || 'user@example.com'}</p>
                </div>
                <div className="w-9 h-9 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center border border-blue-200">
                  <User size={18} />
                </div>
                <ChevronDown size={14} className="text-slate-400" />
              </button>

              {/* Dropdown Menu */}
              {userMenuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-30"
                    onClick={() => setUserMenuOpen(false)}
                  ></div>
                  <div className="absolute top-full right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-slate-100 py-2 z-40 transform origin-top-right transition-all">
                    <div className="px-4 py-2 border-b border-slate-50 mb-1">
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Account</p>
                    </div>
                    <button
                      onClick={() => {
                        navigate('/app/account');
                        setUserMenuOpen(false);
                      }}
                      className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-slate-50 text-sm text-slate-700 transition-colors"
                    >
                      <Settings size={16} />
                      <span>Account Settings</span>
                    </button>
                    <div className="my-1 border-t border-slate-50"></div>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-red-50 text-sm text-red-600 transition-colors"
                    >
                      <LogOut size={16} />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* content + footer container */}
        <main className="flex-1 overflow-auto flex flex-col bg-slate-50">
          <div className="flex-1 w-full max-w-7xl mx-auto w-full">
            <Outlet />
          </div>
          <Footer />
        </main>
      </div>
    </div>
  );
};

/**
 * NavLink Component
 */
const NavLink = ({ to, icon, label, sidebarOpen, active }) => {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate(to)}
      className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${active
          ? 'bg-blue-600 text-white shadow-md shadow-blue-900/20'
          : 'text-slate-400 hover:bg-slate-800 hover:text-white'
        }`}
      title={label}
    >
      <span className={`text-xl ${active ? 'text-white' : 'text-slate-400 group-hover:text-white'}`}>{icon}</span>
      {sidebarOpen && <span className="text-sm font-medium">{label}</span>}
    </button>
  );
};

export default ProtectedLayout;
