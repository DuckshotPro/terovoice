import React from 'react';

export const AnalyticsChart = ({ title, data, dataKey, color, format = 'number' }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <p className="text-gray-600 text-center py-8">No data available</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.map((d) => d[dataKey]));
  const minValue = Math.min(...data.map((d) => d[dataKey]));
  const range = maxValue - minValue || 1;

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatValue = (value) => {
    if (format === 'currency') {
      return `$${(value / 100).toFixed(0)}`;
    }
    return value.toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>

      {/* Simple Bar Chart */}
      <div className="space-y-4">
        {data.map((item, idx) => {
          const normalizedValue = (item[dataKey] - minValue) / range;
          const displayValue = normalizedValue * 100 || 5; // Minimum 5% for visibility

          return (
            <div key={idx}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600">{formatDate(item.date)}</span>
                <span className="text-sm font-semibold text-gray-900">
                  {formatValue(item[dataKey])}
                </span>
              </div>
              <div className="h-8 bg-gray-100 rounded-lg overflow-hidden">
                <div
                  className="h-full rounded-lg transition-all duration-300"
                  style={{
                    width: `${displayValue}%`,
                    backgroundColor: color,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs text-gray-600 mb-1">Total</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatValue(data.reduce((sum, d) => sum + d[dataKey], 0))}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Average</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatValue(
              data.reduce((sum, d) => sum + d[dataKey], 0) / data.length
            )}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Peak</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatValue(maxValue)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsChart;
