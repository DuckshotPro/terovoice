import React, { useState } from 'react';

const OnboardingStep1 = ({ data, onNext, customerId }) => {
  const [formData, setFormData] = useState({
    businessName: data.businessName || '',
    industry: data.industry || '',
    businessPhone: data.businessPhone || '',
    serviceDescription: data.serviceDescription || '',
  });
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [errors, setErrors] = useState({});

  const industries = [
    'Dental Practice',
    'Plumbing Services',
    'Electrical Services',
    'HVAC Services',
    'Auto Repair',
    'Locksmith Services',
    'Massage Therapy',
    'Chiropractic Care',
    'Photography',
    'Real Estate',
    'Tattoo Studio',
    'Home Inspection',
    'Other'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    setUploading(true);

    try {
      const uploadPromises = files.map(async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('customerId', customerId);

        const response = await fetch('/api/upload/business-document', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          return result.url;
        }
        throw new Error('Upload failed');
      });

      const uploadedUrls = await Promise.all(uploadPromises);
      setDocuments(prev => [...prev, ...uploadedUrls]);
    } catch (error) {
      console.error('File upload failed:', error);
      alert('File upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.businessName.trim()) {
      newErrors.businessName = 'Business name is required';
    }

    if (!formData.industry) {
      newErrors.industry = 'Please select an industry';
    }

    if (!formData.businessPhone.trim()) {
      newErrors.businessPhone = 'Business phone number is required';
    } else if (!/^\+?[\d\s\-\(\)]+$/.test(formData.businessPhone)) {
      newErrors.businessPhone = 'Please enter a valid phone number';
    }

    if (!formData.serviceDescription.trim()) {
      newErrors.serviceDescription = 'Service description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onNext({
        ...formData,
        businessDocuments: documents,
      });
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Tell us about your business
        </h2>
        <p className="text-gray-600">
          This information helps us customize your AI receptionist to represent your business accurately.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="businessName" className="block text-sm font-medium text-gray-700 mb-2">
            Business Name *
          </label>
          <input
            type="text"
            id="businessName"
            name="businessName"
            value={formData.businessName}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.businessName ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="e.g., Smith Family Dentistry"
          />
          {errors.businessName && (
            <p className="mt-1 text-sm text-red-600">{errors.businessName}</p>
          )}
        </div>

        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-2">
            Industry *
          </label>
          <select
            id="industry"
            name="industry"
            value={formData.industry}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.industry ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Select your industry</option>
            {industries.map((industry) => (
              <option key={industry} value={industry}>
                {industry}
              </option>
            ))}
          </select>
          {errors.industry && (
            <p className="mt-1 text-sm text-red-600">{errors.industry}</p>
          )}
        </div>

        <div>
          <label htmlFor="businessPhone" className="block text-sm font-medium text-gray-700 mb-2">
            Business Phone Number *
          </label>
          <input
            type="tel"
            id="businessPhone"
            name="businessPhone"
            value={formData.businessPhone}
            onChange={handleInputChange}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.businessPhone ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="e.g., (555) 123-4567"
          />
          {errors.businessPhone && (
            <p className="mt-1 text-sm text-red-600">{errors.businessPhone}</p>
          )}
        </div>

        <div>
          <label htmlFor="serviceDescription" className="block text-sm font-medium text-gray-700 mb-2">
            Service Description *
          </label>
          <textarea
            id="serviceDescription"
            name="serviceDescription"
            value={formData.serviceDescription}
            onChange={handleInputChange}
            rows={4}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.serviceDescription ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Describe the services you offer (e.g., general dentistry, cleanings, emergency dental care)"
          />
          {errors.serviceDescription && (
            <p className="mt-1 text-sm text-red-600">{errors.serviceDescription}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Business Documents (Optional)
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <div className="text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    Upload business license, insurance, or other documents
                  </span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                    onChange={handleFileUpload}
                    className="sr-only"
                    disabled={uploading}
                  />
                </label>
                <p className="mt-1 text-xs text-gray-500">
                  PDF, JPG, PNG, DOC up to 10MB each
                </p>
              </div>
            </div>
          </div>

          {uploading && (
            <div className="mt-2 text-sm text-blue-600">
              Uploading files...
            </div>
          )}

          {documents.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Uploaded Documents:</h4>
              <ul className="space-y-1">
                {documents.map((doc, index) => (
                  <li key={index} className="text-sm text-green-600">
                    ✓ Document {index + 1} uploaded
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Continue to Phone Setup
          </button>
        </div>
      </form>
    </div>
  );
};

export default OnboardingStep1;