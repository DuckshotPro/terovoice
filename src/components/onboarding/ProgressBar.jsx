import React from 'react';

const ProgressBar = ({ currentStep, progress }) => {
  const steps = [
    { number: 1, title: 'Business Info', description: 'Tell us about your business' },
    { number: 2, title: 'Phone Setup', description: 'Configure your phone number' },
    { number: 3, title: 'Responses', description: 'Customize AI responses' },
    { number: 4, title: 'Calendar', description: 'Connect your calendar' },
    { number: 5, title: 'Demo', description: 'Test your AI receptionist' },
    { number: 6, title: 'Review', description: 'Review your setup' },
    { number: 7, title: 'Go Live', description: 'Activate your service' },
  ];

  return (
    <div className="mb-8">
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm font-medium text-gray-700">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Step Indicators */}
      <div className="flex justify-between">
        {steps.map((step) => (
          <div key={step.number} className="flex flex-col items-center">
            <div 
              className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium mb-2 ${
                step.number < currentStep 
                  ? 'bg-green-500 text-white' 
                  : step.number === currentStep
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {step.number < currentStep ? '✓' : step.number}
            </div>
            <div className="text-center">
              <div className="text-xs font-medium text-gray-900">{step.title}</div>
              <div className="text-xs text-gray-500 hidden sm:block">{step.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressBar;