import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Play, Square, Volume2, MessageSquare } from 'lucide-react';

const OnboardingStep5 = ({ onNext, onBack, initialData = {} }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(false);
  const [demoCompleted, setDemoCompleted] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const wsRef = useRef(null);

  // WebRTC and WebSocket setup
  useEffect(() => {
    // Initialize WebSocket connection for real-time communication
    const initWebSocket = () => {
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/demo`;
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected for demo');
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'transcript') {
          setTranscript(prev => [...prev, {
            id: Date.now(),
            speaker: data.speaker,
            text: data.text,
            timestamp: new Date().toLocaleTimeString()
          }]);
        } else if (data.type === 'audio_response') {
          // Play AI response audio
          playAudioResponse(data.audioUrl);
        }
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    initWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      });
      
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          
          // Send audio chunk to backend for real-time STT
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.onload = () => {
              wsRef.current.send(JSON.stringify({
                type: 'audio_chunk',
                data: reader.result,
                customerId: initialData.customerId
              }));
            };
            reader.readAsArrayBuffer(event.data);
          }
        }
      };
      
      mediaRecorder.onstop = () => {
        // Final processing when recording stops
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'audio_end',
            customerId: initialData.customerId
          }));
        }
      };
      
      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      
      // Add initial AI greeting to transcript
      if (transcript.length === 0) {
        setTranscript([{
          id: Date.now(),
          speaker: 'AI',
          text: 'Hello! Thank you for calling. This is your AI receptionist demo. How can I help you today?',
          timestamp: new Date().toLocaleTimeString()
        }]);
      }
      
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check your permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    }
  };

  const playAudioResponse = (audioUrl) => {
    const audio = new Audio(audioUrl);
    setIsPlaying(true);
    
    audio.onended = () => {
      setIsPlaying(false);
    };
    
    audio.onerror = () => {
      setIsPlaying(false);
      console.error('Error playing audio response');
    };
    
    audio.play().catch(error => {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
    });
  };

  const endDemo = async () => {
    setLoading(true);
    
    try {
      // Save demo completion and transcript
      const response = await fetch(`/api/onboarding/${initialData.customerId}/demo-complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          demoTranscripts: transcript,
          demoCompleted: true
        }),
      });

      if (response.ok) {
        setDemoCompleted(true);
      } else {
        throw new Error('Failed to save demo completion');
      }
    } catch (error) {
      console.error('Error saving demo:', error);
      alert('Failed to save demo. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`/api/onboarding/${initialData.customerId}/step-5`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          demoCompleted: true,
          demoTranscripts: transcript
        }),
      });

      if (response.ok) {
        const result = await response.json();
        onNext(result);
      } else {
        throw new Error('Failed to complete demo step');
      }
    } catch (error) {
      console.error('Error completing demo step:', error);
      alert('Failed to complete demo step. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <MessageSquare className="w-16 h-16 text-blue-600 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Interactive Demo</h2>
        <p className="text-gray-600">
          Try talking to your AI receptionist! This demo shows how it will handle real customer calls.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Demo Controls */}
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Demo Controls</h3>
            
            <div className="space-y-4">
              {/* Recording Controls */}
              <div className="flex items-center justify-center space-x-4">
                {!isRecording ? (
                  <button
                    onClick={startRecording}
                    disabled={isPlaying}
                    className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Mic className="w-5 h-5 mr-2" />
                    Start Talking
                  </button>
                ) : (
                  <button
                    onClick={stopRecording}
                    className="flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    <MicOff className="w-5 h-5 mr-2" />
                    Stop Talking
                  </button>
                )}
              </div>

              {/* Status Indicators */}
              <div className="text-center space-y-2">
                {isRecording && (
                  <div className="flex items-center justify-center text-green-600">
                    <div className="animate-pulse w-3 h-3 bg-green-600 rounded-full mr-2"></div>
                    Recording...
                  </div>
                )}
                
                {isPlaying && (
                  <div className="flex items-center justify-center text-blue-600">
                    <Volume2 className="w-4 h-4 mr-2" />
                    AI is responding...
                  </div>
                )}
              </div>

              {/* Demo Instructions */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-800 mb-2">Try saying:</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• "I'd like to schedule an appointment"</li>
                  <li>• "What are your hours?"</li>
                  <li>• "How much does a consultation cost?"</li>
                  <li>• "This is an emergency"</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Demo Actions */}
          {transcript.length > 2 && !demoCompleted && (
            <div className="text-center">
              <button
                onClick={endDemo}
                disabled={loading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Saving Demo...' : 'End Demo'}
              </button>
            </div>
          )}
        </div>

        {/* Live Transcript */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Conversation</h3>
          
          <div className="h-96 overflow-y-auto space-y-3 mb-4">
            {transcript.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Start talking to see the conversation here</p>
              </div>
            ) : (
              transcript.map((message) => (
                <div
                  key={message.id}
                  className={`p-3 rounded-lg ${
                    message.speaker === 'AI'
                      ? 'bg-blue-50 border-l-4 border-blue-500'
                      : 'bg-gray-50 border-l-4 border-gray-500'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className={`text-sm font-medium ${
                      message.speaker === 'AI' ? 'text-blue-700' : 'text-gray-700'
                    }`}>
                      {message.speaker === 'AI' ? 'AI Receptionist' : 'You'}
                    </span>
                    <span className="text-xs text-gray-500">{message.timestamp}</span>
                  </div>
                  <p className="text-gray-900">{message.text}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Demo Summary */}
      {demoCompleted && (
        <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Demo Completed!</h3>
          <p className="text-green-700 mb-4">
            Great job! Your AI receptionist handled the conversation well. 
            The transcript has been saved and will help improve future responses.
          </p>
          
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Demo Summary:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Total exchanges: {Math.floor(transcript.length / 2)}</li>
              <li>• AI responses: {transcript.filter(t => t.speaker === 'AI').length}</li>
              <li>• Your messages: {transcript.filter(t => t.speaker === 'User').length}</li>
              <li>• Demo duration: ~{Math.floor(transcript.length * 0.5)} minutes</li>
            </ul>
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between pt-8">
        <button
          type="button"
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={handleSubmit}
          disabled={loading || !demoCompleted}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Saving...' : 'Continue to Final Steps'}
        </button>
      </div>
    </div>
  );
};

export default OnboardingStep5;