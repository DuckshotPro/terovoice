## You asked:

I am building a local, open-source AI Voice Agent to replace a commercial SaaS. I want to run this on my local machine using the LiveKit Agents framework. Please act as a Senior Python Architect and set up the project structure for me. Here are the requirements: 1. \*\*Framework:\*\* Use `livekit-agents` (Python SDK) as the core orchestrator. 2. \*\*Local Inference Stack:\*\* - \*\*LLM:\*\* Use `ollama` with the `llama3` model. - \*\*STT (Speech-to-Text):\*\* Use `deepgram` (for speed) OR `faster-whisper` (for local). Let's default to Deepgram for now but structure it to be swappable. - \*\*TTS (Text-to-Speech):\*\* Use `cartesia` (for ultra-low latency) OR providing a placeholder for a local TTS like `CosyVoice` or `Kokoro`. 3. \*\*Telephony:\*\* Explain how to configure the `SIP Inbound Trunk` in LiveKit so I can connect a Twilio phone number to this local agent. 4. \*\*Logic:\*\* Create a simple `entrypoint.py` where the agent: - Answers the call. - Introduces itself as a "Dental Receptionist". - Takes a message and saves it to a local `notes.txt` file. Output the full file structure, the `requirements.txt`, and the `agent.py` code.

Show more

---

## Claude Replied:

Local AI Voice Agent - Project Structure
========================================

📁 Project Structure
--------------------

    ai-voice-agent/
    ├── README.md
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── config/
    │   ├── __init__.py
    │   └── settings.py
    ├── services/
    │   ├── __init__.py
    │   ├── llm/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── ollama_provider.py
    │   ├── stt/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── deepgram_provider.py
    │   │   └── whisper_provider.py
    │   └── tts/
    │       ├── __init__.py
    │       ├── base.py
    │       ├── cartesia_provider.py
    │       └── local_tts_provider.py
    ├── agent/
    │   ├── __init__.py
    │   ├── dental_receptionist.py
    │   └── prompts.py
    ├── utils/
    │   ├── __init__.py
    │   └── file_handler.py
    ├── data/
    │   └── notes.txt
    ├── entrypoint.py
    └── docker-compose.yml (optional for Ollama)

* * *

📦 requirements.txt
-------------------

txt

    # LiveKit Core
    livekit-agents==0.9.0
    livekit-api==0.6.0
    livekit-protocol==0.6.0

    # LLM
    ollama==0.3.3

    # STT (Speech-to-Text)
    deepgram-sdk==3.5.0
    faster-whisper==1.0.3  # Optional local alternative

    # TTS (Text-to-Speech)
    cartesia==1.0.5

    # Utilities
    python-dotenv==1.0.0
    pydantic==2.7.0
    pydantic-settings==2.2.1
    aiofiles==24.1.0

    # Telephony (SIP support built into LiveKit)

* * *

⚙️ .env.example
---------------

bash

    # LiveKit Configuration
    LIVEKIT_URL=ws://localhost:7880
    LIVEKIT_API_KEY=your_api_key
    LIVEKIT_API_SECRET=your_api_secret

    # Deepgram STT
    DEEPGRAM_API_KEY=your_deepgram_key

    # Cartesia TTS
    CARTESIA_API_KEY=your_cartesia_key

    # Ollama Configuration
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=llama3

    # Agent Configuration
    AGENT_NAME=Dental Receptionist
    NOTES_FILE_PATH=./data/notes.txt

    # STT/TTS Provider Selection
    STT_PROVIDER=deepgram  # Options: deepgram, whisper
    TTS_PROVIDER=cartesia  # Options: cartesia, local

* * *

🔧 config/settings.py
---------------------

python

    """
    Configuration management using Pydantic Settings.
    Loads environment variables and provides type-safe config access.
    """
    from pydantic_settings import BaseSettings
    from pydantic import Field
    from typing import Literal


    class Settings(BaseSettings):
        """Application settings loaded from environment variables."""

        # LiveKit Configuration
        livekit_url: str = Field(default="ws://localhost:7880")
        livekit_api_key: str = Field(default="")
        livekit_api_secret: str = Field(default="")

        # Deepgram STT
        deepgram_api_key: str = Field(default="")

        # Cartesia TTS
        cartesia_api_key: str = Field(default="")

        # Ollama Configuration
        ollama_base_url: str = Field(default="http://localhost:11434")
        ollama_model: str = Field(default="llama3")

        # Agent Configuration
        agent_name: str = Field(default="Dental Receptionist")
        notes_file_path: str = Field(default="./data/notes.txt")

        # Provider Selection
        stt_provider: Literal["deepgram", "whisper"] = Field(default="deepgram")
        tts_provider: Literal["cartesia", "local"] = Field(default="cartesia")

        class Config:
            env_file = ".env"
            case_sensitive = False


    # Global settings instance
    settings = Settings()

* * *

🤖 services/llm/base.py
-----------------------

python

    """
    Abstract base class for LLM providers.
    Allows easy swapping between Ollama, OpenAI, Anthropic, etc.
    """
    from abc import ABC, abstractmethod
    from typing import AsyncIterator


    class BaseLLMProvider(ABC):
        """Base interface for all LLM providers."""

        @abstractmethod
        async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
            """
            Generate a single response from the LLM.

            Args:
                prompt: User message/query
                system_prompt: System instructions for the LLM

            Returns:
                Generated text response
            """
            pass

        @abstractmethod
        async def stream_response(self, prompt: str, system_prompt: str = "") -> AsyncIterator[str]:
            """
            Stream response tokens from the LLM.

            Args:
                prompt: User message/query
                system_prompt: System instructions for the LLM

            Yields:
                Text chunks as they're generated
            """
            pass

* * *

🤖 services/llm/ollama\_provider.py
-----------------------------------

python

    """
    Ollama LLM provider implementation.
    Connects to local Ollama instance for inference.
    """
    import ollama
    from typing import AsyncIterator
    from .base import BaseLLMProvider
    from config.settings import settings


    class OllamaProvider(BaseLLMProvider):
        """Ollama-based LLM provider for local inference."""

        def __init__(self, model: str = None, base_url: str = None):
            """
            Initialize Ollama provider.

            Args:
                model: Model name (defaults to settings)
                base_url: Ollama server URL (defaults to settings)
            """
            self.model = model or settings.ollama_model
            self.base_url = base_url or settings.ollama_base_url
            self.client = ollama.AsyncClient(host=self.base_url)

        async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
            """
            Generate a complete response from Ollama.

            Args:
                prompt: User message
                system_prompt: System instructions

            Returns:
                Complete generated response
            """
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            response = await self.client.chat(
                model=self.model,
                messages=messages
            )

            return response['message']['content']

        async def stream_response(self, prompt: str, system_prompt: str = "") -> AsyncIterator[str]:
            """
            Stream response tokens from Ollama.

            Args:
                prompt: User message
                system_prompt: System instructions

            Yields:
                Text chunks as they're generated
            """
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            stream = await self.client.chat(
                model=self.model,
                messages=messages,
                stream=True
            )

            async for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

* * *

🎤 services/stt/base.py
-----------------------

python

    """
    Abstract base class for Speech-to-Text providers.
    Enables swapping between Deepgram, Whisper, etc.
    """
    from abc import ABC, abstractmethod
    from typing import AsyncIterator


    class BaseSTTProvider(ABC):
        """Base interface for all STT providers."""

        @abstractmethod
        async def transcribe_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
            """
            Transcribe streaming audio to text.

            Args:
                audio_stream: Async iterator of audio bytes

            Yields:
                Transcribed text chunks
            """
            pass

* * *

🎤 services/stt/deepgram\_provider.py
-------------------------------------

python

    """
    Deepgram STT provider implementation.
    High-speed cloud-based transcription.
    """
    from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
    from typing import AsyncIterator
    from .base import BaseSTTProvider
    from config.settings import settings


    class DeepgramSTTProvider(BaseSTTProvider):
        """Deepgram-based STT provider for real-time transcription."""

        def __init__(self, api_key: str = None):
            """
            Initialize Deepgram provider.

            Args:
                api_key: Deepgram API key (defaults to settings)
            """
            self.api_key = api_key or settings.deepgram_api_key
            self.client = DeepgramClient(self.api_key)

        async def transcribe_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
            """
            Transcribe streaming audio using Deepgram Live API.

            Args:
                audio_stream: Async iterator of audio bytes

            Yields:
                Transcribed text as it becomes available
            """
            # Configure Deepgram options for low-latency transcription
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                encoding="linear16",
                sample_rate=16000,
                channels=1,
                interim_results=True,
                punctuate=True,
                smart_format=True
            )

            connection = self.client.listen.live.v("1")

            async def on_message(self, result, **kwargs):
                """Handle incoming transcription results."""
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) > 0:
                    yield sentence

            connection.on(LiveTranscriptionEvents.Transcript, on_message)

            # Start connection
            if not await connection.start(options):
                raise Exception("Failed to connect to Deepgram")

            # Stream audio data
            async for audio_chunk in audio_stream:
                connection.send(audio_chunk)

            # Close connection
            await connection.finish()

* * *

🔊 services/tts/base.py
-----------------------

python

    """
    Abstract base class for Text-to-Speech providers.
    Enables swapping between Cartesia, local TTS, etc.
    """
    from abc import ABC, abstractmethod
    from typing import AsyncIterator


    class BaseTTSProvider(ABC):
        """Base interface for all TTS providers."""

        @abstractmethod
        async def synthesize_stream(self, text: str) -> AsyncIterator[bytes]:
            """
            Synthesize text to speech audio stream.

            Args:
                text: Text to convert to speech

            Yields:
                Audio bytes chunks
            """
            pass

* * *

🔊 services/tts/cartesia\_provider.py
-------------------------------------

python

    """
    Cartesia TTS provider implementation.
    Ultra-low latency voice synthesis.
    """
    from cartesia import AsyncCartesia
    from typing import AsyncIterator
    from .base import BaseTTSProvider
    from config.settings import settings


    class CartesiaTTSProvider(BaseTTSProvider):
        """Cartesia-based TTS provider for low-latency synthesis."""

        def __init__(self, api_key: str = None):
            """
            Initialize Cartesia provider.

            Args:
                api_key: Cartesia API key (defaults to settings)
            """
            self.api_key = api_key or settings.cartesia_api_key
            self.client = AsyncCartesia(api_key=self.api_key)
            # Use a professional, friendly voice for dental receptionist
            self.voice_id = "694f9389-aac1-45b6-b726-9d9369183238"  # Friendly female voice

        async def synthesize_stream(self, text: str) -> AsyncIterator[bytes]:
            """
            Stream synthesized audio from Cartesia.

            Args:
                text: Text to synthesize

            Yields:
                Raw audio bytes (PCM 16-bit, 16kHz)
            """
            # Stream audio in real-time for minimal latency
            stream = await self.client.tts.sse(
                model_id="sonic-english",
                transcript=text,
                voice_id=self.voice_id,
                output_format={
                    "container": "raw",
                    "encoding": "pcm_s16le",
                    "sample_rate": 16000
                },
                stream=True
            )

            async for chunk in stream:
                if "audio" in chunk:
                    yield chunk["audio"]

* * *

📝 agent/prompts.py
-------------------

python

    """
    System prompts and agent personalities.
    Centralized prompt management for easy tuning.
    """

    DENTAL_RECEPTIONIST_SYSTEM_PROMPT = """You are a friendly and professional dental receptionist at a busy dental practice. Your role is to:

    1. **Greet callers warmly** - Make them feel welcome and comfortable
    2. **Listen carefully** - Pay attention to their needs, concerns, or appointment requests
    3. **Take detailed messages** - Capture caller name, phone number, reason for calling, and any urgency
    4. **Be empathetic** - If they're in pain or anxious, acknowledge their feelings
    5. **Be concise** - Keep responses brief and to the point
    6. **Stay professional** - Maintain a courteous tone at all times

    When taking a message, ensure you get:
    - Caller's full name
    - Phone number
    - Reason for call (new patient, existing patient, emergency, question, etc.)
    - Best time to call back
    - Any special notes or urgency indicators

    After gathering information, summarize what you've noted and confirm with the caller before ending the call.

    Keep your responses natural, conversational, and under 2-3 sentences each."""


    def get_message_summary_prompt(conversation_history: str) -> str:
        """
        Generate a prompt to summarize the conversation into a structured message.

        Args:
            conversation_history: Full transcript of the call

        Returns:
            Prompt for LLM to extract structured message
        """
        return f"""Based on this phone conversation, extract and format the key information as a message note:

    Conversation:
    {conversation_history}

    Format the output as:
    ---
    DATE: [Current date/time]
    CALLER: [Full name]
    PHONE: [Phone number]
    REASON: [Reason for call]
    BEST TIME TO CALL: [Preferred callback time]
    URGENCY: [Normal/Urgent/Emergency]
    NOTES: [Any additional relevant details]
    ---

    If any information is missing, write "Not provided" for that field."""

* * *

📝 agent/dental\_receptionist.py
--------------------------------

python

    """
    Main agent logic for the Dental Receptionist voice agent.
    Orchestrates STT, LLM, and TTS to handle incoming calls.
    """
    import asyncio
    from datetime import datetime
    from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
    from livekit.agents.voice_assistant import VoiceAssistant
    from livekit.plugins import silero

    from services.llm.ollama_provider import OllamaProvider
    from agent.prompts import DENTAL_RECEPTIONIST_SYSTEM_PROMPT, get_message_summary_prompt
    from utils.file_handler import append_to_notes
    from config.settings import settings


    class DentalReceptionistAgent:
        """Voice agent that acts as a dental receptionist."""

        def __init__(self):
            """Initialize the dental receptionist agent."""
            self.llm_provider = OllamaProvider()
            self.conversation_history = []
            self.system_prompt = DENTAL_RECEPTIONIST_SYSTEM_PROMPT

        async def handle_call(self, ctx: JobContext):
            """
            Main call handling logic.

            Args:
                ctx: LiveKit job context containing room and participant info
            """
            await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

            # Get the participant (caller)
            participant = await ctx.wait_for_participant()

            # Initialize conversation
            initial_greeting = (
                f"Hello! Thank you for calling our dental office. "
                f"This is {settings.agent_name}, how may I help you today?"
            )

            # Create voice assistant with configured STT/TTS
            # NOTE: Actual LiveKit VoiceAssistant integration requires
            # proper plugin initialization - this is a conceptual structure
            assistant = VoiceAssistant(
                vad=silero.VAD.load(),  # Voice Activity Detection
                stt=self._get_stt_provider(),
                llm=self._create_llm_wrapper(),
                tts=self._get_tts_provider(),
                chat_ctx=llm.ChatContext()
            )

            # Start the assistant
            assistant.start(ctx.room, participant)

            # Send initial greeting
            await assistant.say(initial_greeting, allow_interruptions=True)

            # Track conversation for note-taking
            @assistant.on("user_speech_committed")
            def on_user_speech(msg: str):
                """Capture user speech for conversation history."""
                self.conversation_history.append(f"Caller: {msg}")

            @assistant.on("agent_speech_committed")
            def on_agent_speech(msg: str):
                """Capture agent responses for conversation history."""
                self.conversation_history.append(f"Agent: {msg}")

            # Wait for call to end
            await assistant.wait_for_completion()

            # Save conversation summary to notes
            await self._save_call_summary()

        def _get_stt_provider(self):
            """
            Factory method to get configured STT provider.

            Returns:
                Configured STT provider instance
            """
            if settings.stt_provider == "deepgram":
                from livekit.plugins import deepgram
                return deepgram.STT()
            else:
                # Fallback to Whisper or other local STT
                # This would need proper implementation
                raise NotImplementedError("Whisper STT not yet implemented")

        def _get_tts_provider(self):
            """
            Factory method to get configured TTS provider.

            Returns:
                Configured TTS provider instance
            """
            if settings.tts_provider == "cartesia":
                from livekit.plugins import cartesia
                return cartesia.TTS()
            else:
                # Fallback to local TTS
                raise NotImplementedError("Local TTS not yet implemented")

        def _create_llm_wrapper(self):
            """
            Create an LLM wrapper compatible with LiveKit's expected interface.

            Returns:
                LLM instance for voice assistant
            """
            # LiveKit expects an LLM with specific interface
            # This wraps our Ollama provider to match that interface
            from livekit.agents import llm as livekit_llm

            # Create a custom LLM that uses our Ollama provider
            class OllamaLLM(livekit_llm.LLM):
                def __init__(self, provider: OllamaProvider):
                    super().__init__()
                    self.provider = provider

                async def chat(self, chat_ctx: livekit_llm.ChatContext):
                    # Convert chat context to prompt
                    messages = chat_ctx.messages
                    prompt = messages[-1].content if messages else ""

                    # Get response from Ollama
                    response = await self.provider.generate_response(
                        prompt=prompt,
                        system_prompt=DENTAL_RECEPTIONIST_SYSTEM_PROMPT
                    )

                    return livekit_llm.ChatResponse(
                        message=livekit_llm.ChatMessage(
                            role="assistant",
                            content=response
                        )
                    )

            return OllamaLLM(self.llm_provider)

        async def _save_call_summary(self):
            """
            Generate and save a structured summary of the call.
            Uses LLM to extract key information from conversation.
            """
            if not self.conversation_history:
                return

            # Format conversation
            conversation_text = "\n".join(self.conversation_history)

            # Generate summary using LLM
            summary_prompt = get_message_summary_prompt(conversation_text)
            summary = await self.llm_provider.generate_response(
                prompt=summary_prompt,
                system_prompt=""
            )

            # Save to notes file
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note_entry = f"\n\n{'='*60}\nCALL RECEIVED: {timestamp}\n{'='*60}\n{summary}\n"

            await append_to_notes(settings.notes_file_path, note_entry)

            print(f"✅ Call summary saved to {settings.notes_file_path}")

* * *

🛠️ utils/file\_handler.py
--------------------------

python

    """
    File handling utilities for saving call notes and transcripts.
    Async I/O for non-blocking file operations.
    """
    import aiofiles
    import os
    from pathlib import Path


    async def append_to_notes(file_path: str, content: str):
        """
        Append content to notes file asynchronously.
        Creates file and directories if they don't exist.

        Args:
            file_path: Path to the notes file
            content: Content to append
        """
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)

        # Append content to file
        async with aiofiles.open(file_path, mode='a', encoding='utf-8') as f:
            await f.write(content)


    async def read_notes(file_path: str) -> str:
        """
        Read entire notes file asynchronously.

        Args:
            file_path: Path to the notes file

        Returns:
            File contents as string
        """
        if not os.path.exists(file_path):
            return ""

        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            return await f.read()

* * *

🚀 entrypoint.py
----------------

python

    """
    Main entrypoint for the LiveKit Voice Agent.
    Initializes the worker and registers the agent handler.
    """
    from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
    from agent.dental_receptionist import DentalReceptionistAgent
    from config.settings import settings
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


    async def entrypoint(ctx: JobContext):
        """
        Main entrypoint called by LiveKit when a new call comes in.

        Args:
            ctx: Job context containing room and connection info
        """
        logger.info(f"🔵 New call received - Room: {ctx.room.name}")

        # Initialize and run the dental receptionist agent
        agent = DentalReceptionistAgent()

        try:
            await agent.handle_call(ctx)
            logger.info(f"✅ Call completed successfully")
        except Exception as e:
            logger.error(f"❌ Error handling call: {e}", exc_info=True)
            raise


    def main():
        """
        Start the LiveKit agent worker.
        Connects to LiveKit server and waits for incoming calls.
        """
        logger.info(f"🚀 Starting {settings.agent_name} Agent Worker")
        logger.info(f"📡 Connecting to LiveKit: {settings.livekit_url}")
        logger.info(f"🤖 LLM: Ollama ({settings.ollama_model})")
        logger.info(f"🎤 STT: {settings.stt_provider.upper()}")
        logger.info(f"🔊 TTS: {settings.tts_provider.upper()}")

        # Run the worker with configuration
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                api_key=settings.livekit_api_key,
                api_secret=settings.livekit_api_secret,
                ws_url=settings.livekit_url,
            )
        )


    if __name__ == "__main__":
        main()

* * *

📞 SIP Inbound Trunk Configuration
----------------------------------

### LiveKit SIP Setup Guide

To connect your Twilio phone number to this local agent:

#### 1\. **Enable SIP in LiveKit Server**

Add to your `livekit.yaml` config:

yaml

    sip:
      inbound_trunk:
        - name: "twilio-trunk"
          numbers: ["+1234567890"]  # Your Twilio number
          allowed_addresses: ["54.172.60.0/23", "54.244.51.0/24"]  # Twilio IPs
          auth_username: "your_sip_username"
          auth_password: "your_sip_password"

#### 2\. **Configure Twilio SIP Trunk**

In Twilio Console:

*   Go to **Elastic SIP Trunking** → Create new trunk
*   **Origination URI**: `sip:your-livekit-server.com:5060`
*   **Authentication**: Use credentials from LiveKit config
*   **Termination URI**: Add your LiveKit server IP
*   Assign your phone number to this trunk

#### 3\. **Route Calls to Your Agent**

In LiveKit, create a dispatch rule:

yaml

    dispatch_rules:
      - rule_id: "dental-receptionist"
        type: "sip_inbound"
        trunk_ids: ["twilio-trunk"]
        room_prefix: "dental-call-"
        agent_name: "dental-receptionist"

#### 4\. **Network Configuration**

If running locally:

*   Expose LiveKit server via **ngrok** or **Cloudflare Tunnel**
*   Update Twilio with public URL
*   Ensure port 5060 (SIP) and 7880 (WebSocket) are accessible

#### 5\. **Test the Connection**

bash

    # Call your Twilio number
    # LiveKit will create a room and trigger your agent
    # Monitor logs:
    tail -f livekit.log

* * *

🐳 docker-compose.yml (Optional Ollama Setup)
---------------------------------------------

yaml

    version: '3.8'

    services:
      ollama:
        image: ollama/ollama:latest
        container_name: ollama
        ports:
          - "11434:11434"
        volumes:
          - ollama-data:/root/.ollama
        environment:
          - OLLAMA_HOST=0.0.0.0
        restart: unless-stopped

      # Optional: Pull model on startup
      ollama-init:
        image: ollama/ollama:latest
        depends_on:
          - ollama
        entrypoint: ["/bin/sh", "-c"]
        command:
          - |
            sleep 5
            ollama pull llama3
        restart: "no"

    volumes:
      ollama-data:

* * *

🎯 Quick Start
--------------

bash

    # 1. Clone and setup
    git clone <your-repo>
    cd ai-voice-agent
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate

    # 2. Install dependencies
    pip install -r requirements.txt

    # 3. Start Ollama (if using Docker)
    docker-compose up -d
    # Or install Ollama locally and run: ollama serve

    # 4. Pull the model
    ollama pull llama3

    # 5. Configure environment
    cp .env.example .env
    # Edit .env with your API keys

    # 6. Create data directory
    mkdir -p data

    # 7. Run the agent
    python entrypoint.py start

* * *

🔄 Swapping Providers
---------------------

### Switch to Local Whisper STT:

bash

    # In .env
    STT_PROVIDER=whisper

    # Implement services/stt/whisper_provider.py (similar structure to Deepgram)

### Add Local TTS:

bash

    # In .env
    TTS_PROVIDER=local

    # Implement services/tts/local_tts_provider.py
    # Options: CosyVoice, Kokoro, Piper-TTS
    ```

    ---

    ## 📊 Architecture Overview
    ```
    Phone Call (Twilio)
        ↓ SIP
    LiveKit Server
        ↓ WebSocket
    Agent Worker (entrypoint.py)
        ↓
    DentalReceptionistAgent
        ├─→ STT (Deepgram/Whisper) → Text
        ├─→ LLM (Ollama/Llama3) → Response
        └─→ TTS (Cartesia/Local) → Audio
        ↓
    notes.txt (Message Log)

This architecture is fully modular—swap any component by implementing the base provider interface. All configuration is centralized in `settings.py` and `.env`.

---
