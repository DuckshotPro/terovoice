import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import DashboardOverview from '../components/portal/DashboardOverview';
import CallLogs from '../components/portal/CallLogs';
import Settings from '../components/portal/Settings';
import Billing from '../components/portal/Billing';
import Help from '../components/portal/Help';
import Navigation from '../components/portal/Navigation';

const Portal = () => {
  const { customerId } = useParams();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [customerData, setCustomerData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomerData();
  }, [customerId]);

  const loadCustomerData = async () => {
    try {
      const response = await fetch(`/api/portal/${customerId}/dashboard`);
      if (response.ok) {
        const data = await response.json();
        setCustomerData(data);
      }
    } catch (error) {
      console.error('Failed to load customer data:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardOverview customerId={customerId} data={customerData} />;
      case 'calls':
        return <CallLogs customerId={customerId} />;
      case 'settings':
        return <Settings customerId={customerId} data={customerData} onUpdate={loadCustomerData} />;
      case 'billing':
        return <Billing customerId={customerId} data={customerData} />;
      case 'help':
        return <Help />;
      default:
        return <DashboardOverview customerId={customerId} data={customerData} />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your portal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        customerData={customerData}
      />

      <div className="max-w-7xl mx-auto py-8 px-4">
        {renderActiveTab()}
      </div>
    </div>
  );
};

export default Portal;