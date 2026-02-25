import React, { useEffect, useState } from 'react';
import { TrendingUp, Phone, CheckCircle, DollarSign, AlertCircle } from 'lucide-react';
import AnalyticsChart from '../../components/analytics/AnalyticsChart';
import MetricCard from '../../components/analytics/MetricCard';

export const Analytics = () => {
  const [metrics, setMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Replace with actual API call
      // const response = await api.analytics.getMetrics({ range: timeRange });
      // setMetrics(response.data);

      // Mock data for now
      setMetrics({
        total_calls: 1247,
        completed_calls: 1189,
        missed_calls: 58,
        average_duration: 245,
        success_rate: 95.3,
        total_revenue: 12450,
        sentiment_positive: 78,
        sentiment_neutral: 18,
        sentiment_negative: 4,
        calls_by_day: [
          { date: '2025-12-21', calls: 145 },
          { date: '2025-12-22', calls: 168 },
          { date: '2025-12-23', calls: 152 },
          { date: '2025-12-24', calls: 98 },
          { date: '2025-12-25', calls: 45 },
          { date: '2025-12-26', calls: 189 },
          { date: '2025-12-27', calls: 210 },
        ],
        revenue_by_day: [
          { date: '2025-12-21', revenue: 1450 },
          { date: '2025-12-22', revenue: 1680 },
          { date: '2025-12-23', revenue: 1520 },
          { date: '2025-12-24', revenue: 980 },
          { date: '2025-12-25', revenue: 450 },
          { date: '2025-12-26', revenue: 1890 },
          { date: '2025-12-27', revenue: 2100 },
        ],
      });
    } catch (err) {
      setError(err.message || 'Failed to fetch analytics');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-2">Track your AI receptionist performance</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
        </select>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      ) : metrics ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <MetricCard
              icon={Phone}
              label="Total Calls"
              value={metrics.total_calls.toLocaleString()}
              color="blue"
            />
            <MetricCard
              icon={CheckCircle}
              label="Completed"
              value={`${metrics.success_rate}%`}
              color="green"
            />
            <MetricCard
              icon={TrendingUp}
              label="Avg Duration"
              value={`${Math.floor(metrics.average_duration / 60)}m`}
              color="purple"
            />
            <MetricCard
              icon={DollarSign}
              label="Revenue"
              value={`$${(metrics.total_revenue / 1000).toFixed(1)}k`}
              color="orange"
            />
            <MetricCard
              icon={AlertCircle}
              label="Missed Calls"
              value={metrics.missed_calls}
              color="red"
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AnalyticsChart
              title="Calls Over Time"
              data={metrics.calls_by_day}
              dataKey="calls"
              color="#3b82f6"
            />
            <AnalyticsChart
              title="Revenue Over Time"
              data={metrics.revenue_by_day}
              dataKey="revenue"
              color="#10b981"
              format="currency"
            />
          </div>

          {/* Sentiment Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {metrics.sentiment_positive}%
                </div>
                <p className="text-gray-600">Positive</p>
                <div className="mt-2 h-2 bg-green-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-600"
                    style={{ width: `${metrics.sentiment_positive}%` }}
                  />
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-600 mb-2">
                  {metrics.sentiment_neutral}%
                </div>
                <p className="text-gray-600">Neutral</p>
                <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-600"
                    style={{ width: `${metrics.sentiment_neutral}%` }}
                  />
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600 mb-2">
                  {metrics.sentiment_negative}%
                </div>
                <p className="text-gray-600">Negative</p>
                <div className="mt-2 h-2 bg-red-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-600"
                    style={{ width: `${metrics.sentiment_negative}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default Analytics;
