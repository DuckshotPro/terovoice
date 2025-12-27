"""
Base voice agent for handling incoming calls.
Integrates with LiveKit, routes to correct profession, logs analytics.
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Optional

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    llm,
    VoiceAssistantOptions,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, silero

from services.llm.huggingface_provider import HuggingFaceLLMProvider
from agent.router import ClientRouter
from analytics.db import log_call_to_db
from config.settings import settings

logger = logging.getLogger("voice-agent")


class AIReceptionistAgent:
    """Main voice agent for handling incoming calls."""

    def __init__(self):
        """Initialize agent with providers and router."""
        self.llm_provider = HuggingFaceLLMProvider()
        self.router = ClientRouter(settings.clients_db_path)
        self.conversation_history = []
        self.call_start_time = None
        self.latencies = {
            "stt": 0,
            "llm": 0,
            "tts": 0,
        }

    async def handle_call(
        self, ctx: JobContext, incoming_number: str
    ) -> None:
        """
        Main call handler.

        Args:
            ctx: LiveKit job context
            incoming_number: Caller's phone number (E.164)
        """
        self.call_start_time = time.time()
        logger.info(f"📞 Incoming call from: {incoming_number}")

        try:
            # Connect to LiveKit room
            await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

            # Get client config by phone number
            client_config = self.router.get_client_by_phone(incoming_number)
            if not client_config:
                logger.warning(f"No client found for {incoming_number}")
                return

            # Get profession-specific prompt
            profession = client_config.get("profession", "dentist")
            system_prompt = self.router.get_profession_prompt(profession)

            # Get participant (caller)
            participant = await ctx.wait_for_participant()
            logger.info(f"Participant joined: {participant.identity}")

            # Create voice assistant
            assistant = VoiceAssistant(
                vad=silero.VAD.load(),
                stt=deepgram.STT(),  # Cloud STT (fast)
                llm=self._create_llm_wrapper(system_prompt),
                tts=self._create_tts_wrapper(),
                voice_assistant_options=VoiceAssistantOptions(
                    base_volume=1.0,
                    transcription_options=deepgram.STTOptions(
                        model="nova-2",
                        language="en-US",
                    ),
                ),
            )

            # Start assistant
            assistant.start(ctx.room, participant)

            # Send greeting
            greeting = f"Hello! Thank you for calling. How can I help you today?"
            await assistant.say(greeting, allow_interruptions=True)

            # Track conversation
            @assistant.on("user_speech_committed")
            def on_user_speech(msg: str):
                self.conversation_history.append(f"Caller: {msg}")

            @assistant.on("agent_speech_committed")
            def on_agent_speech(msg: str):
                self.conversation_history.append(f"Agent: {msg}")

            # Wait for call to end
            await assistant.wait_for_completion()

            # Log call analytics
            await self._log_call_analytics(client_config)

        except Exception as e:
            logger.error(f"❌ Call error: {e}", exc_info=True)

    def _create_llm_wrapper(self, system_prompt: str):
        """
        Create LLM wrapper compatible with LiveKit.

        Args:
            system_prompt: System instructions for this profession

        Returns:
            LLM instance
        """

        class HFLLMWrapper(llm.LLM):
            def __init__(self, provider, sys_prompt):
                super().__init__()
                self.provider = provider
                self.system_prompt = sys_prompt

            async def chat(self, chat_ctx: llm.ChatContext) -> llm.ChatResponse:
                # Get last user message
                messages = chat_ctx.messages
                user_msg = messages[-1].content if messages else ""

                # Get response from HF
                response_text = await self.provider.generate_response(
                    prompt=user_msg,
                    system_prompt=self.system_prompt,
                )

                return llm.ChatResponse(
                    message=llm.ChatMessage(
                        role="assistant",
                        content=response_text,
                    )
                )

        return HFLLMWrapper(self.llm_provider, system_prompt)

    def _create_tts_wrapper(self):
        """Create TTS wrapper (Cartesia for ultra-low latency)."""
        from livekit.plugins import cartesia

        return cartesia.TTS(
            api_key=settings.cartesia_api_key,
            voice="sonic-english",
        )

    async def _log_call_analytics(self, client_config: dict) -> None:
        """
        Log call to analytics database.

        Args:
            client_config: Client configuration dict
        """
        try:
            total_duration = time.time() - self.call_start_time
            transcript = "\n".join(self.conversation_history)

            await log_call_to_db(
                client_name=client_config.get("name", "unknown"),
                duration=total_duration,
                transcript=transcript,
                profession=client_config.get("profession", "unknown"),
                success=True,
            )

            logger.info(f"✅ Call logged: {total_duration:.1f}s")

        except Exception as e:
            logger.error(f"Error logging call: {e}")
