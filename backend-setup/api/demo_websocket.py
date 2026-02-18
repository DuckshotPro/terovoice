"""
WebSocket handler for interactive demo functionality.
Handles real-time audio processing and AI responses.
"""

import asyncio
import json
import logging
from flask import Flask
from flask_socketio import SocketIO, emit, disconnect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend_setup.db.models import User, OnboardingState, ConversationLog
from backend_setup.services.analytics_service import AnalyticsService
import os
import base64
import tempfile
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tero_voice')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

analytics_service = AnalyticsService()

class DemoWebSocketHandler:
    """Handles WebSocket connections for interactive demo."""

    def __init__(self, socketio):
        self.socketio = socketio
        self.active_sessions = {}

    def register_handlers(self):
        """Register WebSocket event handlers."""

        @self.socketio.on('connect', namespace='/demo')
        def handle_connect():
            """Handle client connection."""
            logger.info(f"Demo client connected: {request.sid}")
            emit('status', {'message': 'Connected to demo service'})

        @self.socketio.on('disconnect', namespace='/demo')
        def handle_disconnect():
            """Handle client disconnection."""
            session_id = request.sid
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            logger.info(f"Demo client disconnected: {session_id}")

        @self.socketio.on('audio_chunk', namespace='/demo')
        def handle_audio_chunk(data):
            """Handle incoming audio chunk for STT processing."""
            try:
                session_id = request.sid
                customer_id = data.get('customerId')
                audio_data = data.get('data')

                if not customer_id or not audio_data:
                    emit('error', {'message': 'Missing required data'})
                    return

                # Initialize session if not exists
                if session_id not in self.active_sessions:
                    self.active_sessions[session_id] = {
                        'customer_id': customer_id,
                        'conversation': [],
                        'audio_buffer': []
                    }

                # Add audio chunk to buffer
                self.active_sessions[session_id]['audio_buffer'].append(audio_data)

                # Process audio chunk (simulate STT)
                # In a real implementation, you would:
                # 1. Send audio to STT service (on-site or IBM Cloud)
                # 2. Get transcription result
                # 3. Send to LLM for response
                # 4. Generate TTS audio

                # For demo purposes, simulate processing
                asyncio.create_task(self.process_audio_chunk(session_id, audio_data))

            except Exception as e:
                logger.error(f"Error handling audio chunk: {str(e)}")
                emit('error', {'message': 'Audio processing failed'})

        @self.socketio.on('audio_end', namespace='/demo')
        def handle_audio_end(data):
            """Handle end of audio input."""
            try:
                session_id = request.sid
                customer_id = data.get('customerId')

                if session_id in self.active_sessions:
                    # Process complete audio buffer
                    asyncio.create_task(self.process_complete_audio(session_id, customer_id))

            except Exception as e:
                logger.error(f"Error handling audio end: {str(e)}")
                emit('error', {'message': 'Audio processing failed'})

    async def process_audio_chunk(self, session_id, audio_data):
        """Process audio chunk with STT."""
        try:
            # Simulate STT processing delay
            await asyncio.sleep(0.1)

            # For demo purposes, simulate partial transcription
            # In real implementation, use actual STT service
            partial_text = "..."  # Placeholder for partial transcription

            self.socketio.emit('transcript', {
                'type': 'partial',
                'speaker': 'User',
                'text': partial_text,
                'timestamp': datetime.now().isoformat()
            }, namespace='/demo', room=session_id)

        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")

    async def process_complete_audio(self, session_id, customer_id):
        """Process complete audio input and generate AI response."""
        try:
            if session_id not in self.active_sessions:
                return

            session_data = self.active_sessions[session_id]

            # Simulate STT processing
            await asyncio.sleep(0.5)

            # For demo purposes, simulate different user inputs and responses
            demo_responses = [
                {
                    'user': "Hi, I'd like to schedule an appointment",
                    'ai': "I'd be happy to help you schedule an appointment! What type of service are you looking for, and do you have any preferred dates or times?"
                },
                {
                    'user': "What are your hours?",
                    'ai': "We're open Monday through Friday from 8 AM to 6 PM, and Saturday from 9 AM to 3 PM. We're closed on Sundays. Would you like to schedule something during these hours?"
                },
                {
                    'user': "How much does a consultation cost?",
                    'ai': "Our initial consultation is $150, which includes a comprehensive examination and treatment planning. This fee is applied toward any treatment you decide to proceed with. Would you like to schedule a consultation?"
                },
                {
                    'user': "This is an emergency",
                    'ai': "I understand this is urgent. Let me get you connected with our emergency line right away. Can you briefly describe what's happening so I can prioritize your call?"
                }
            ]

            # Select response based on conversation length
            response_index = len(session_data['conversation']) % len(demo_responses)
            demo_pair = demo_responses[response_index]

            # Emit user transcript
            self.socketio.emit('transcript', {
                'type': 'final',
                'speaker': 'User',
                'text': demo_pair['user'],
                'timestamp': datetime.now().isoformat()
            }, namespace='/demo', room=session_id)

            # Add to conversation history
            session_data['conversation'].append({
                'speaker': 'User',
                'text': demo_pair['user'],
                'timestamp': datetime.now().isoformat()
            })

            # Simulate AI processing delay
            await asyncio.sleep(1.0)

            # Emit AI response
            self.socketio.emit('transcript', {
                'type': 'final',
                'speaker': 'AI',
                'text': demo_pair['ai'],
                'timestamp': datetime.now().isoformat()
            }, namespace='/demo', room=session_id)

            # Add AI response to conversation
            session_data['conversation'].append({
                'speaker': 'AI',
                'text': demo_pair['ai'],
                'timestamp': datetime.now().isoformat()
            })

            # Simulate TTS processing and emit audio URL
            # In real implementation, generate actual audio
            await asyncio.sleep(0.5)

            # For demo, just indicate audio is ready
            self.socketio.emit('audio_response', {
                'audioUrl': '/demo/audio/response.mp3',  # Mock URL
                'text': demo_pair['ai']
            }, namespace='/demo', room=session_id)

            # Save conversation log to database
            await self.save_conversation_log(customer_id, session_data['conversation'])

            # Log analytics event
            analytics_service.log_event(
                user_id=customer_id,
                event_type='demo_interaction',
                event_data={
                    'interaction_count': len(session_data['conversation']),
                    'user_input': demo_pair['user'],
                    'ai_response': demo_pair['ai']
                }
            )

        except Exception as e:
            logger.error(f"Error processing complete audio: {str(e)}")
            self.socketio.emit('error', {
                'message': 'Failed to process audio'
            }, namespace='/demo', room=session_id)

    async def save_conversation_log(self, customer_id, conversation):
        """Save conversation to database for fine-tuning."""
        try:
            session = SessionLocal()

            # Create a mock call record for the demo
            # In real implementation, this would be linked to an actual call
            for exchange in conversation[-2:]:  # Save last user-AI pair
                if exchange['speaker'] == 'User':
                    user_utterance = exchange['text']
                elif exchange['speaker'] == 'AI':
                    ai_response = exchange['text']

                    # Save conversation log
                    log_entry = ConversationLog(
                        call_id=None,  # Demo calls don't have call IDs
                        user_id=customer_id,
                        user_utterance=user_utterance,
                        ai_response=ai_response,
                        stt_provider='demo',
                        tts_provider='demo',
                        confidence=0.95,  # Mock confidence
                        sentiment='NEUTRAL',
                        call_type='demo'
                    )
                    session.add(log_entry)

            session.commit()
            session.close()

        except Exception as e:
            logger.error(f"Error saving conversation log: {str(e)}")


def create_demo_websocket_app():
    """Create Flask app with SocketIO for demo WebSocket handling."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'demo-secret-key')

    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )

    # Initialize WebSocket handler
    demo_handler = DemoWebSocketHandler(socketio)
    demo_handler.register_handlers()

    @app.route('/demo/audio/<filename>')
    def serve_demo_audio(filename):
        """Serve demo audio files."""
        # In a real implementation, serve actual TTS-generated audio
        # For demo, return a placeholder response
        return "Demo audio file", 200, {'Content-Type': 'audio/mpeg'}

    return app, socketio


if __name__ == '__main__':
    app, socketio = create_demo_websocket_app()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)