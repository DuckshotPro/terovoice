"""
Main entrypoint for LiveKit voice agent.
Handles incoming calls and routes to correct client.
"""
import logging
import sys
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli

from agent.base_agent import AIReceptionistAgent
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("entrypoint")


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint called by LiveKit when a new call comes in.

    Args:
        ctx: LiveKit job context
    """
    # Extract incoming phone number from SIP headers
    # This depends on how LiveKit passes SIP metadata
    incoming_number = ctx.room.metadata.get("incoming_number", "unknown")

    logger.info(f"🔵 New call received - Room: {ctx.room.name}, From: {incoming_number}")

    # Initialize and run agent
    agent = AIReceptionistAgent()

    try:
        await agent.handle_call(ctx, incoming_number)
        logger.info(f"✅ Call completed successfully")
    except Exception as e:
        logger.error(f"❌ Error handling call: {e}", exc_info=True)
        raise


def main():
    """Start the LiveKit agent worker."""
    logger.info("🚀 Starting AI Receptionist Agent Worker")
    logger.info(f"📡 LiveKit URL: {settings.livekit_url}")
    logger.info(f"🤖 LLM: Hugging Face ({settings.huggingface_api_url})")
    logger.info(f"🎤 STT: Deepgram")
    logger.info(f"🔊 TTS: Cartesia")

    # Run the worker
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
