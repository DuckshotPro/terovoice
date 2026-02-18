"""
Hugging Face LLM provider.
Calls your remote HF VPS for inference (Llama3, Mistral, etc).
"""
import httpx
import logging
from typing import AsyncIterator
from config.settings import settings

logger = logging.getLogger("hf-llm")


class HuggingFaceLLMProvider:
    """LLM provider that calls Hugging Face inference endpoint."""

    def __init__(self):
        """Initialize HF provider with remote endpoint."""
        self.api_url = settings.huggingface_api_url
        self.api_key = settings.huggingface_api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"HF LLM Provider initialized: {self.api_url}")

    async def generate_response(
        self, prompt: str, system_prompt: str = "", max_tokens: int = 256
    ) -> str:
        """
        Generate response from Hugging Face inference.

        Args:
            prompt: User message
            system_prompt: System instructions
            max_tokens: Max response length

        Returns:
            Generated text response
        """
        try:
            # Build the full prompt with system instructions
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            # Call your HF VPS endpoint
            # Assumes you're running text-generation-webui or similar
            response = await self.client.post(
                f"{self.api_url}/api/v1/generate",
                json={
                    "prompt": full_prompt,
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                    if self.api_key
                    else None
                },
            )

            if response.status_code == 200:
                data = response.json()
                # Extract text from response (adjust based on your HF endpoint format)
                text = data.get("results", [{}])[0].get("text", "").strip()
                return text if text else "I didn't understand that. Could you repeat?"
            else:
                logger.error(f"HF API error: {response.status_code} - {response.text}")
                return "Sorry, I'm having trouble processing that right now."

        except Exception as e:
            logger.error(f"HF LLM Error: {e}")
            return "I encountered an error. Please try again."

    async def stream_response(
        self, prompt: str, system_prompt: str = ""
    ) -> AsyncIterator[str]:
        """
        Stream response tokens from Hugging Face.

        Args:
            prompt: User message
            system_prompt: System instructions

        Yields:
            Text chunks as they're generated
        """
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            async with self.client.stream(
                "POST",
                f"{self.api_url}/api/v1/generate",
                json={
                    "prompt": full_prompt,
                    "max_new_tokens": 256,
                    "temperature": 0.7,
                    "stream": True,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                    if self.api_key
                    else None
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            data = line[5:].strip()
                            if data:
                                chunk = data.split('"text":"')[1].split('"')[0]
                                yield chunk
                        except (IndexError, ValueError):
                            continue

        except Exception as e:
            logger.error(f"HF Stream Error: {e}")
            yield "Error streaming response."
