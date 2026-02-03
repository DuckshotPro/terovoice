import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import OnboardingStep1 from '../components/onboarding/OnboardingStep1';
import OnboardingStep2 from '../components/onboarding/OnboardingStep2';
import OnboardingStep3 from '../components/onboarding/OnboardingStep3';
import OnboardingStep4 from '../components/onboarding/OnboardingStep4';
import OnboardingStep5 from '../components/onboarding/OnboardingStep5';
import OnboardingStep6 from '../components/onboarding/OnboardingStep6';
import OnboardingStep7 from '../components/onboarding/OnboardingStep7';
import ProgressBar from '../components/onboarding/ProgressBar';

const Onboarding = () => {
  const { customerId } = useParams();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [progress, setProgress] = useState(0);
  const [onboardingData, setOnboardingData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load onboarding state from API
    loadOnboardingState();
  }, [customerId]);

  const loadOnboardingState = async () => {
    try {
      const response = await fetch(`/api/onboarding/${customerId}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentStep(data.currentStep);
        setProgress(data.progress);
        setOnboardingData(data);
      }
    } catch (error) {
      console.error('Failed to load onboarding state:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateOnboardingState = async (stepData) => {
    try {
      const response = await fetch(`/api/onboarding/${customerId}/step-${currentStep}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(stepData),
      });

      if (response.ok) {
        const updatedData = await response.json();
        setOnboardingData(prev => ({ ...prev, ...updatedData }));
        setProgress(updatedData.progress);
        
        if (currentStep < 7) {
          setCurrentStep(currentStep + 1);
        } else {
          // Onboarding complete, redirect to portal
          navigate(`/portal/${customerId}`);
        }
      }
    } catch (error) {
      console.error('Failed to update onboarding state:', error);
    }
  };

  const renderCurrentStep = () => {
    const stepProps = {
      data: onboardingData,
      onNext: updateOnboardingState,
      customerId,
    };

    switch (currentStep) {
      case 1:
        return <OnboardingStep1 {...stepProps} />;
      case 2:
        return <OnboardingStep2 {...stepProps} />;
      case 3:
        return <OnboardingStep3 {...stepProps} />;
      case 4:
        return <OnboardingStep4 {...stepProps} />;
      case 5:
        return <OnboardingStep5 {...stepProps} />;
      case 6:
        return <OnboardingStep6 {...stepProps} />;
      case 7:
        return <OnboardingStep7 {...stepProps} />;
      default:
        return <div>Invalid step</div>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your onboarding...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to Tero Voice
            </h1>
            <p className="text-gray-600">
              Let's set up your AI receptionist in just a few steps
            </p>
          </div>

          <ProgressBar currentStep={currentStep} progress={progress} />

          <div className="mt-8">
            {renderCurrentStep()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;