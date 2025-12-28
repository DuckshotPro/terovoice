import React, { useEffect, useState } from 'react';
import { Phone, Clock, CheckCircle, AlertCircle, Search, Filter } from 'lucide-react';
import CallDetail from '../../components/calls/CallDetail';

export const Calls = () => {
  const [calls, setCalls] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCall, setSelectedCall] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchCalls();
  }, []);

  const fetchCalls = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Replace with actual API call
      // const response = await api.calls.list();
      // setCalls(response.data.calls || []);

      // Mock data for now
      setCalls([
        {
          id: '1',
          client_id: '1',
          client_name: 'Dr. Smith Dental',
          phone_number: '+1 (555) 123-4567',
          duration: 245,
          status: 'completed',
          transcript:
            'Customer: Hi, I need to schedule an appointment. Agent: Of course! What date works best for you?',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          sentiment: 'positive',
          booked: true,
        },
        {
          id: '2',
          client_id: '1',
          client_name: 'Dr. Smith Dental',
          phone_number: '+1 (555) 234-5678',
          duration: 180,
          status: 'completed',
          transcript: 'Customer: What are your hours? Agent: We are open 9am to 5pm, Monday through Friday.',
          created_at: new Date(Date.now() - 7200000).toISOString(),
          sentiment: 'neutral',
          booked: false,
        },
        {
          id: '3',
          client_id: '2',
          client_name: 'Mike\'s Plumbing',
          phone_number: '+1 (555) 345-6789',
          duration: 420,
          status: 'completed',
          transcript: 'Customer: Emergency! Water leak in basement. Agent: I can dispatch someone within 30 minutes.',
          created_at: new Date(Date.now() - 10800000).toISOString(),
          sentiment: 'positive',
          booked: true,
        },
      ]);
    } catch (err) {
      setError(err.message || 'Failed to fetch calls');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredCalls = calls.filter((call) => {
    const matchesSearch =
      call.client_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      call.phone_number.includes(searchTerm);
    const matchesStatus = filterStatus === 'all' || call.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 bg-green-50';
      case 'negative':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Call History</h1>
        <p className="text-gray-600 mt-2">View and manage all incoming calls</p>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Search and Filter */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by client name or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Calls</option>
            <option value="completed">Completed</option>
            <option value="missed">Missed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Calls List */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading calls...</p>
        </div>
      ) : filteredCalls.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <Phone className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No calls found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredCalls.map((call) => (
            <div
              key={call.id}
              onClick={() => setSelectedCall(call)}
              className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer border-l-4 border-blue-600"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Phone className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-gray-900">{call.client_name}</h3>
                    {call.booked && (
                      <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded">
                        Booked
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-2">
                    <div className="flex items-center gap-1">
                      <Phone className="w-4 h-4" />
                      {call.phone_number}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDuration(call.duration)}
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 line-clamp-2">{call.transcript}</p>
                </div>

                <div className="flex flex-col items-end gap-2">
                  <div className="flex items-center gap-2">
                    {call.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-600" />
                    )}
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {call.status}
                    </span>
                  </div>

                  <div
                    className={`text-xs font-medium px-2 py-1 rounded capitalize ${getSentimentColor(
                      call.sentiment
                    )}`}
                  >
                    {call.sentiment}
                  </div>

                  <span className="text-xs text-gray-500">{formatTime(call.created_at)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Call Detail Modal */}
      {selectedCall && (
        <CallDetail call={selectedCall} onClose={() => setSelectedCall(null)} />
      )}
    </div>
  );
};

export default Calls;
