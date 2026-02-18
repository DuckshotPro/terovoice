import React, { useState } from 'react';
import { MessageCircle, Upload, FileText } from 'lucide-react';

const OnboardingStep3 = ({ onNext, onBack, initialData = {} }) => {
  const [formData, setFormData] = useState({
    callerResponses: initialData.callerResponses || {
      appointment_request: 'I\'d be happy to help you schedule an appointment. Let me check our availability.',
      pricing_inquiry: 'I can provide you with pricing information. What specific service are you interested in?',
      emergency: 'I understand this is urgent. Let me connect you with someone right away.',
      other: 'Thank you for calling. How can I assist you today?'
    },
    ...initialData
  });
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const responseTypes = [
    {
      key: 'appointment_request',
      label: 'Appointment Requests',
      description: 'When customers want to schedule an appointment'
    },
    {
      key: 'pricing_inquiry',
      label: 'Pricing Questions',
      description: 'When customers ask about costs or pricing'
    },
    {
      key: 'emergency',
      label: 'Emergency Calls',
      description: 'When customers have urgent needs'
    },
    {
      key: 'other',
      label: 'General Inquiries',
      description: 'Default response for other questions'
    }
  ];

  const handleResponseChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      callerResponses: {
        ...prev.callerResponses,
        [key]: value
      }
    }));
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);

    // TODO: Implement file upload to S3 or local storage
    const uploadPromises = files.map(async (file) => {
      // Simulate file upload
      await new Promise(resolve => setTimeout(resolve, 1000));
      return {
        name: file.name,
        size: file.size,
        type: file.type,
        url: `/uploads/${file.name}` // Mock URL
      };
    });

    try {
      const uploadedFileData = await Promise.all(uploadPromises);
      setUploadedFiles(prev => [...prev, ...uploadedFileData]);
    } catch (error) {
      console.error('File upload failed:', error);
      alert('File upload failed. Please try again.');
    }
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`/api/onboarding/${initialData.customerId}/step-3`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          businessDocuments: uploadedFiles
        }),
      });

      if (response.ok) {
        const result = await response.json();
        onNext(result);
      } else {
        throw new Error('Failed to save caller responses');
      }
    } catch (error) {
      console.error('Error saving caller responses:', error);
      alert('Failed to save caller responses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <MessageCircle className="w-16 h-16 text-blue-600 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Caller Responses</h2>
        <p className="text-gray-600">
          Customize how your AI receptionist responds to different types of calls
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Response Templates */}
        <div className="grid gap-6">
          {responseTypes.map((type) => (
            <div key={type.key} className="border border-gray-200 rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{type.label}</h3>
                <p className="text-sm text-gray-600">{type.description}</p>
              </div>

              <textarea
                value={formData.callerResponses[type.key]}
                onChange={(e) => handleResponseChange(type.key, e.target.value)}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder={`Enter response for ${type.label.toLowerCase()}...`}
              />
            </div>
          ))}
        </div>

        {/* Business Documents Upload */}
        <div className="border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FileText className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Business Documents</h3>
          </div>

          <p className="text-sm text-gray-600 mb-4">
            Upload documents that help your AI understand your business better (menus, price lists, FAQs, etc.)
          </p>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600 mb-2">
              Drag and drop files here, or click to select
            </p>
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
            >
              Select Files
            </label>
            <p className="text-xs text-gray-500 mt-2">
              Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG (Max 10MB each)
            </p>
          </div>

          {/* Uploaded Files List */}
          {uploadedFiles.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Uploaded Files:</h4>
              <div className="space-y-2">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                    <div className="flex items-center">
                      <FileText className="w-4 h-4 text-gray-500 mr-2" />
                      <span className="text-sm text-gray-900">{file.name}</span>
                      <span className="text-xs text-gray-500 ml-2">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-6">
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Back
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Continue'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default OnboardingStep3;