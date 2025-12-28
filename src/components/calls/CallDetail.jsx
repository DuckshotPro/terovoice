import React from 'react';
import { X, Phone, Clock, CheckCircle, Copy, Download } from 'lucide-react';

export const CallDetail = ({ call, onClose }) => {
  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${mins}m ${secs}s`;
    }
    return `${mins}m ${secs}s`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white">
          <h2 className="text-xl font-bold text-gray-900">Call Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Call Info */}
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{call.client_name}</h3>
                <p className="text-gray-600">{call.phone_number}</p>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <span className="font-medium text-green-600 capitalize">{call.status}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-gray-600 mb-1">Duration</p>
                <p className="font-semibold text-gray-900 flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatDuration(call.duration)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Date & Time</p>
                <p className="font-semibold text-gray-900 text-sm">
                  {new Date(call.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Sentiment</p>
                <p className="font-semibold text-gray-900 capitalize">{call.sentiment}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Appointment</p>
                <p className="font-semibold text-gray-900">
                  {call.booked ? '✓ Booked' : 'Not booked'}
                </p>
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-900">Call Information</h4>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Call ID</span>
                <div className="flex items-center gap-2">
                  <code className="text-sm font-mono text-gray-900">{call.id}</code>
                  <button
                    onClick={() => copyToClipboard(call.id)}
                    className="p-1 hover:bg-gray-200 rounded transition-colors"
                  >
                    <Copy className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Date & Time</span>
                <span className="text-sm font-mono text-gray-900">
                  {formatDate(call.created_at)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Duration</span>
                <span className="text-sm font-mono text-gray-900">
                  {formatDuration(call.duration)}
                </span>
              </div>
            </div>
          </div>

          {/* Transcript */}
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-900">Transcript</h4>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {call.transcript}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
              <Download className="w-4 h-4" />
              Download Transcript
            </button>
            <button
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallDetail;
