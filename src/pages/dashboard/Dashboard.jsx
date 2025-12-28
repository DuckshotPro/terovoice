import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { BarChart3, Phone, Users, TrendingUp } from 'lucide-react';

export const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome, {user?.name}!</h1>
        <p className="text-gray-600 mt-2">Here's your AI receptionist dashboard</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Calls</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            </div>
            <Phone className="w-12 h-12 text-blue-100" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Active Clients</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
            </div>
            <Users className="w-12 h-12 text-green-100" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Success Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">0%</p>
            </div>
            <TrendingUp className="w-12 h-12 text-purple-100" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Revenue</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">$0</p>
            </div>
            <BarChart3 className="w-12 h-12 text-orange-100" />
          </div>
        </div>
      </div>

      {/* Coming Soon */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">Coming Soon</h2>
        <p className="text-blue-700">
          More dashboard features are being built. Check back soon for call analytics, client
          management, and billing information.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
